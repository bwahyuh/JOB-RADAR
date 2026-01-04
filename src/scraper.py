import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os

# --- KONFIGURASI TARGET ---
# Kita cari "Data Engineer" di Indonesia (JobStreet)
BASE_URL = "https://id.jobstreet.com/id/job-search/data-engineer-jobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def extract_jobs():
    print(f"🕵️  Memulai operasi mata-mata ke: {BASE_URL}")
    
    # 1. TEMBAK REQUEST
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        response.raise_for_status() # Cek error (kalau 403/404 dia bakal teriak)
        print("✅ Koneksi Berhasil! Status Code: 200")
    except Exception as e:
        print(f"❌ Gagal connect: {e}")
        return

    # 2. PARSING HTML
    soup = BeautifulSoup(response.content, "html.parser")
    
    # List kosong untuk nampung hasil jarahan
    job_list = []

    # 3. CARI ELEMEN KARTU PEKERJAAN
    # Kita cari semua elemen <article>
    articles = soup.find_all("article")
    
    print(f"📦 Ditemukan {len(articles)} lowongan di halaman pertama.")

    for job in articles:
        try:
            # Ambil Judul
            title_element = job.find("a", attrs={"data-automation": "jobTitle"})
            company_element = job.find("a", attrs={"data-automation": "jobCompany"})
            location_element = job.find("a", attrs={"data-automation": "jobLocation"})
            
            # Bersihkan teks (kalau elemen ketemu)
            title = title_element.text.strip() if title_element else "N/A"
            company = company_element.text.strip() if company_element else "N/A"
            location = location_element.text.strip() if location_element else "N/A"
            link = "https://id.jobstreet.com" + title_element['href'] if title_element else "N/A"

            # Masukkan ke keranjang
            job_data = {
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "scraped_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            job_list.append(job_data)
            
        except Exception as e:
            continue

    # 4. SIMPAN KE CSV (DATA MENTAH)
    if job_list:
        df = pd.DataFrame(job_list)
        
        # Pastikan folder tujuan ada
        output_dir = "data/raw"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{output_dir}/jobs_raw_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"💾 Misi Sukses! Data diamankan di: {filename}")
        print(df.head()) # Tampilkan 5 data pertama di layar
    else:
        print("⚠️ Zonk! Tidak ada data yang berhasil diambil. Cek selector HTML.")

if __name__ == "__main__":
    extract_jobs()