import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import os
import glob
from dotenv import load_dotenv

load_dotenv()

def get_latest_csv():
    # Get the latest CSV file in the raw folder
    list_of_files = glob.glob('data/raw/*.csv') 
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def create_table_if_not_exists(conn):
    print("🔨 Checking Table Structure...")
    # Updated: Table definition includes columns for AI & Vectors
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
        EXTRACTED_SKILLS TEXT,                 -- Additional Column for AI
        DESCRIPTION_VECTOR VECTOR(FLOAT, 1024) -- Additional Column for Vector
    );
    """
    conn.cursor().execute(create_query)
    print("✅ Table RAW_DATA.JOB_POSTINGS (Full Version) Ready!")

def load_data():
    print("🚀 STARTING OPERATION SKY LIFT...")
    
    csv_file = get_latest_csv()
    if not csv_file:
        print("❌ Error: No CSV file found!")
        return
    
    print(f"📦 Hauling cargo: {csv_file}")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    # Convert column names to UPPERCASE (Required for Snowflake)
    df.columns = [col.upper() for col in df.columns]
    
    print(f"📊 Total Payload: {len(df)} rows")

    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            role='DATA_ENGINEER_ROLE'  # <--- IMPORTANT! Use Engineer Role
        )
        
        create_table_if_not_exists(conn)
        
        # Upload Data (Bulk Insert) - DEFAULT IS APPEND (SAFE FOR HISTORY)
        success, n_chunks, n_rows, _ = write_pandas(
            conn, 
            df, 
            "JOB_POSTINGS", 
            quote_identifiers=False
        )
        
        if success:
            print(f"🎉 SUCCESS! {n_rows} rows landed safely in Snowflake.")
        else:
            print("⚠️ Upload finished but status is doubtful. Check Snowflake.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ MISSION FAILED: {e}")

if __name__ == "__main__":
    load_data()