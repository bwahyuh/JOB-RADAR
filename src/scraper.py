import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os
import time
import random

# --- KONFIGURASI TARGET ---
BASE_URL = "https://id.jobstreet.com/id/job-search/data-engineer-jobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_job_details(job_url):
    """
    Fungsi mata-mata khusus untuk masuk ke halaman detail lowongan
    dan mengambil Deskripsi lengkap + Tipe Pekerjaan.
    """
    try:
        # Jeda manusiawi (biar gak dikira robot jahat)
        sleep_time = random.uniform(1, 3)
        time.sleep(sleep_time)
        
        print(f"   ↳ 🕵️ Mengintip detail... (tunggu {sleep_time:.1f}s)")
        response = requests.get(job_url, headers=HEADERS)
        
        if response.status_code != 200:
            return "Gagal akses", "Gagal akses"

        soup = BeautifulSoup(response.content, "html.parser")
        
        # 1. AMBIL DESKRIPSI (Biasanya ada di data-automation="jobAdDetails")
        # Kita ambil teks-nya saja, lalu bersihkan spasi berlebih
        desc_element = soup.find("div", attrs={"data-automation": "jobAdDetails"})
        description = desc_element.get_text(separator="\n").strip() if desc_element else "Deskripsi tidak ditemukan"
        
        # 2. AMBIL TIPE PEKERJAAN (Full time / Contract)
        # Biasanya ada di list bagian atas
        type_element = soup.find("span", attrs={"data-automation": "job-detail-work-type"})
        job_type = type_element.text.strip() if type_element else "Tidak disebutkan"

        return description, job_type

    except Exception as e:
        print(f"   ❌ Error detail: {e}")
        return "Error", "Error"

def extract_jobs():
    print(f"🚀 MEMULAI MISI V2: DEEP DIVE SCRAPING")
    print(f"🎯 Target: {BASE_URL}\n")
    
    # --- TAHAP 1: SCOUTING (Cari Link di Halaman Depan) ---
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Gagal koneksi awal: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("article")
    
    print(f"📦 Ditemukan {len(articles)} kandidat lowongan. Memulai ekstraksi detail...\n")
    
    job_list = []

    # --- TAHAP 2: INFILTRATION (Masuk satu per satu) ---
    for i, job in enumerate(articles):
        try:
            # Ambil data dasar (Kulitnya)
            title_element = job.find("a", attrs={"data-automation": "jobTitle"})
            company_element = job.find("a", attrs={"data-automation": "jobCompany"})
            location_element = job.find("a", attrs={"data-automation": "jobLocation"})
            
            if not title_element:
                continue

            title = title_element.text.strip()
            company = company_element.text.strip() if company_element else "N/A"
            location = location_element.text.strip() if location_element else "N/A"
            link = "https://id.jobstreet.com" + title_element['href']

            print(f"[{i+1}/{len(articles)}] Memproses: {title} ({company})")

            # PANGGIL FUNGSI DETAIL (Masuk ke dalam link)
            full_description, work_type = get_job_details(link)

            # Simpan data lengkap
            job_data = {
                "title": title,
                "company": company,
                "location": location,
                "work_type": work_type, # <--- DATA BARU
                "posted_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "scraped_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "link": link,
                "description": full_description # <--- DATA BARU (HARTA KARUN)
            }
            job_list.append(job_data)
            
        except Exception as e:
            print(f"⚠️ Gagal memproses item {i}: {e}")
            continue

    # --- TAHAP 3: SAVE REPORT ---
    if job_list:
        df = pd.DataFrame(job_list)
        
        output_dir = "data/raw"
        os.makedirs(output_dir, exist_ok=True)
        
        # Simpan CSV
        filename = f"{output_dir}/jobs_v2_full_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=False)
        
        print(f"\n✅ MISI SELESAI!")
        print(f"💾 Data lengkap (dengan deskripsi) tersimpan di: {filename}")
        print(f"📊 Total Data: {len(df)} baris")
        print("Sampel Data Terakhir:")
        print(df[['title', 'work_type']].tail()) # Cek apakah work_type masuk
    else:
        print("⚠️ Zonk! Tidak ada data.")

if __name__ == "__main__":
    extract_jobs()