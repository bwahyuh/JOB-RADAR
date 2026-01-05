import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from collections import Counter

# --- CONFIGURATION ---
load_dotenv()
st.set_page_config(page_title="Job Radar ID", page_icon="📡", layout="wide")

# --- CONNECT TO SNOWFLAKE ---
@st.cache_data
def load_data():
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        role='DATA_ENGINEER_ROLE'
    )
    
    # --- INTELLIGENT QUERY (OPTION A: DEDUPLICATION ON READ) ---
    # Logic: Group by LINK, Sort by SCRAPED_AT Descending, Take Top 1
    query = """
    SELECT TITLE, COMPANY, EXTRACTED_SKILLS
    FROM (
        SELECT 
            TITLE, 
            COMPANY, 
            EXTRACTED_SKILLS,
            ROW_NUMBER() OVER (PARTITION BY LINK ORDER BY SCRAPED_AT DESC) as rn
        FROM JOB_POSTINGS
        WHERE EXTRACTED_SKILLS IS NOT NULL
    )
    WHERE rn = 1
    """
    
    cur = conn.cursor()
    cur.execute(query)
    df = cur.fetch_pandas_all()
    conn.close()
    return df

# --- MAIN PAGE ---
st.title("📡 Job Radar ID: AI-Powered Market Tracker")
st.markdown("Analyzing real-time Data Engineering job market in Indonesia using **Snowflake Cortex AI**.")

try:
    with st.spinner('Fetching data from Snowflake (Filtering Duplicates)...'):
        df = load_data()
    
    # --- METRICS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Unique Jobs Analyzed", len(df))
    col2.metric("Top Role", df['TITLE'].mode()[0] if not df.empty else "N/A")
    col3.metric("Data Source", "JobStreet via Python Scraper")

    # --- DATA PROCESSING ---
    # Convert CSV string to list -> Flatten -> Count
    all_skills = []
    for skills_str in df['EXTRACTED_SKILLS']:
        if skills_str:
            # Clean and split
            cleaned = [s.strip().upper() for s in skills_str.split(',')]
            all_skills.extend(cleaned)
    
    skill_counts = Counter(all_skills)
    skill_df = pd.DataFrame(skill_counts.items(), columns=['Skill', 'Demand']).sort_values(by='Demand', ascending=False).head(20)

    # --- VISUALIZATION ---
    st.divider()
    
    col_chart, col_raw = st.columns([2, 1])
    
    with col_chart:
        st.subheader("🔥 Top 20 Most Demanded Skills")
        if not skill_df.empty:
            fig = px.bar(
                skill_df, 
                x='Demand', 
                y='Skill', 
                orientation='h',
                color='Demand',
                color_continuous_scale='blues',
                text_auto=True
            )
            fig.update_layout(yaxis=dict(autorange="reversed")) # Top skill on top
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No skill data found. Please run 'src/transformer.py' first!")

    with col_raw:
        st.subheader("📋 Latest Unique Job Extractions")
        st.dataframe(df[['TITLE', 'EXTRACTED_SKILLS']].head(10), hide_index=True)

except Exception as e:
    st.error(f"System Error: {e}")
    st.info("Ensure you have run 'src/transformer.py' and your credentials are correct.")