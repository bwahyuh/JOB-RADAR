import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import os
import glob
from dotenv import load_dotenv

load_dotenv()

def get_latest_csv():
    # Get the latest CSV file from the raw data folder
    list_of_files = glob.glob('data/raw/*.csv') 
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def create_table_if_not_exists(conn):
    print("🔨 Checking Table Structure...")
    # Ensure table exists. LINK column is used for deduplication logic.
    create_query = """
    CREATE TABLE IF NOT EXISTS RAW_DATA.JOB_POSTINGS (
        TITLE STRING,
        COMPANY STRING,
        LOCATION STRING,
        WORK_TYPE STRING,
        POSTED_DATE DATE,
        SCRAPED_AT TIMESTAMP,
        LINK STRING,
        DESCRIPTION STRING,
        EXTRACTED_SKILLS TEXT,                 
        DESCRIPTION_VECTOR VECTOR(FLOAT, 1024) 
    );
    """
    conn.cursor().execute(create_query)

def get_existing_links(conn):
    """
    Fetch existing Job Links from Snowflake to prevent duplicates.
    """
    print("🔍 Checking existing jobs in Warehouse...")
    try:
        cur = conn.cursor()
        # Select all LINKS currently in storage
        cur.execute("SELECT LINK FROM RAW_DATA.JOB_POSTINGS")
        # Convert to a Set for O(1) lookup performance
        existing_links = set(row[0] for row in cur.fetchall())
        print(f"   ↳ Found {len(existing_links)} existing jobs.")
        return existing_links
    except Exception as e:
        # If table doesn't exist or is empty, return empty set
        return set()

def load_data():
    print("🚀 STARTING OPERATION SKY LIFT (INCREMENTAL)...")
    
    csv_file = get_latest_csv()
    if not csv_file:
        print("❌ Error: No CSV file found in data/raw/ !")
        return
    
    print(f"📦 Source Data: {csv_file}")
    
    # 1. READ CSV
    df = pd.read_csv(csv_file)
    df.columns = [col.upper() for col in df.columns] # Snowflake requires UPPERCASE columns
    
    original_count = len(df)
    
    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            role='DATA_ENGINEER_ROLE'
        )
        
        # 2. CHECK TABLE STRUCTURE
        create_table_if_not_exists(conn)
        
        # 3. DEDUPLICATION LOGIC (Incremental Load)
        existing_links = get_existing_links(conn)
        
        # Filter: Keep only rows where 'LINK' is NOT in 'existing_links'
        if not df.empty and 'LINK' in df.columns:
            df_new = df[~df['LINK'].isin(existing_links)]
        else:
            df_new = pd.DataFrame() 
            
        new_count = len(df_new)
        print(f"📊 Filter Report: {original_count} Raw -> {new_count} New Unique Jobs")
        
        # 4. UPLOAD ONLY NEW DATA
        if new_count > 0:
            print("🚚 Uploading new data to Snowflake...")
            success, n_chunks, n_rows, _ = write_pandas(
                conn, 
                df_new, 
                "JOB_POSTINGS", 
                quote_identifiers=False
            )
            if success:
                print(f"🎉 SUCCESS! Added {n_rows} new jobs to Warehouse.")
            else:
                print("⚠️ Upload finished but status is doubtful.")
        else:
            print("zzz... No new jobs to upload today. Warehouse is up to date.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ MISSION FAILED: {e}")

if __name__ == "__main__":
    load_data()