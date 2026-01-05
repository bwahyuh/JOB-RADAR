import snowflake.connector
import os
from dotenv import load_dotenv

# Load credentials
load_dotenv()

def run_transformation():
    print("🤖 STARTING AI TRANSFORMATION ENGINE...")
    
    try:
        # 1. Connect to Snowflake
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            role='DATA_ENGINEER_ROLE'
        )
        cur = conn.cursor()

        # 2. Read SQL File
        sql_file_path = 'sql/transform_skills.sql'
        print(f"📂 Reading SQL logic from: {sql_file_path}")
        
        with open(sql_file_path, 'r') as file:
            query = file.read()

        # 3. Execute Query
        print("⚡ Sending request to Cortex LLM (This might take a moment)...")
        cur.execute(query)
        
        # 4. Check results
        result = cur.fetchall()
        print("✅ TRANSFORMATION COMPLETE!")
        print(f"Updated Rows: {result[0][0] if result else 'Unknown'}")
        
        conn.close()

    except Exception as e:
        print(f"❌ TRANSFORMATION FAILED: {e}")

if __name__ == "__main__":
    run_transformation()