import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()
print("📡 Menghubungi Markas Snowflake...")

try:
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )
    cur = conn.cursor()
    cur.execute("SELECT CURRENT_VERSION()")
    print(f"✅ KONEKSI SUKSES! Versi: {cur.fetchone()[0]}")
    conn.close()
except Exception as e:
    print(f"❌ GAGAL: {e}")