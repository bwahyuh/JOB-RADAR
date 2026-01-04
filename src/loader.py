import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import os
import glob
from dotenv import load_dotenv

load_dotenv()

def get_latest_csv():
    # Ambil file CSV terbaru di folder raw
    list_of_files = glob.glob('data/raw/*.csv') 
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def create_table_if_not_exists(conn):
    print("🔨 Memeriksa Struktur Tabel...")
    # Kita buat tabel sederhana dulu untuk menampung data
    create_query = """
    CREATE TABLE IF NOT EXISTS RAW_DATA.JOB_POSTINGS (
        TITLE STRING,
        COMPANY STRING,
        LOCATION STRING,
        WORK_TYPE STRING,
        POSTED_DATE DATE,
        SCRAPED_AT TIMESTAMP,
        LINK STRING,
        DESCRIPTION STRING
    );
    """
    conn.cursor().execute(create_query)
    print("✅ Tabel RAW_DATA.JOB_POSTINGS Siap!")

def load_data():
    print("🚀 MEMULAI OPERASI SKY LIFT...")
    
    csv_file = get_latest_csv()
    if not csv_file:
        print("❌ Error: Tidak ada file CSV!")
        return
    
    print(f"📦 Mengangkut kargo: {csv_file}")
    
    # Baca CSV
    df = pd.read_csv(csv_file)
    # Ubah nama kolom jadi KAPITAL (Wajib untuk Snowflake)
    df.columns = [col.upper() for col in df.columns]
    
    print(f"📊 Total Muatan: {len(df)} baris")

    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            role='DATA_ENGINEER_ROLE'  # <--- PENTING! Pakai seragam Engineer
        )
        
        create_table_if_not_exists(conn)
        
        # Upload Data (Bulk Insert)
        success, n_chunks, n_rows, _ = write_pandas(
            conn, 
            df, 
            "JOB_POSTINGS", 
            quote_identifiers=False
        )
        
        if success:
            print(f"🎉 SUKSES BESAR! {n_rows} baris data berhasil mendarat di Snowflake.")
        else:
            print("⚠️ Upload selesai tapi status meragukan. Cek Snowflake.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ MISI GAGAL: {e}")

if __name__ == "__main__":
    load_data()