import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os
import time
import random

# --- TARGET CONFIGURATION ---
BASE_URL = "https://id.jobstreet.com/id/job-search/data-engineer-jobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 🛡️ GATEKEEPER CONFIGURATION
# Only pass if title contains ONE of these keywords:
VALID_KEYWORDS = [
    "DATA ENGINEER", 
    "BIG DATA", 
    "ETL", 
    "DATA WAREHOUSE", 
    "DATA ARCHITECT", 
    "DATABASE ADMINISTRATOR",
    "DATA PLATFORM",
    "ANALYTICS ENGINEER"
]

# REJECT if title contains any of these keywords (even if it has 'engineer'):
BLACKLIST_KEYWORDS = [
    "SALES", 
    "MARKETING", 
    "INTERN",
    "FRONTEND",
    "CIVIL", 
    "MECHANICAL"
]

def is_relevant_role(title):
    """
    Gatekeeper Function: Checks if the job title matches Data Engineering criteria.
    Returns: (bool, reason)
    """
    title_upper = title.upper()
    
    # 1. Check Blacklist first
    for bad_word in BLACKLIST_KEYWORDS:
        if bad_word in title_upper:
            return False, f"Blacklisted ({bad_word})"
            
    # 2. Check Whitelist (Must contain at least one DE keyword)
    for key in VALID_KEYWORDS:
        if key in title_upper:
            return True, "OK"
            
    return False, "Not Relevant"

def get_job_details(job_url):
    """
    Spy function to visit each job link and extract
    Full Description + Work Type.
    """
    try:
        # Human-like delay to avoid getting blocked
        sleep_time = random.uniform(1, 3)
        time.sleep(sleep_time)
        
        print(f"   ↳ 🕵️ Fetching details... (wait {sleep_time:.1f}s)")
        response = requests.get(job_url, headers=HEADERS)
        
        if response.status_code != 200:
            return "Access Failed", "Access Failed"

        soup = BeautifulSoup(response.content, "html.parser")
        
        # 1. EXTRACT DESCRIPTION (Look for data-automation="jobAdDetails")
        desc_element = soup.find("div", attrs={"data-automation": "jobAdDetails"})
        description = desc_element.get_text(separator="\n").strip() if desc_element else "Description not found"
        
        # 2. EXTRACT WORK TYPE (Full time / Contract)
        type_element = soup.find("span", attrs={"data-automation": "job-detail-work-type"})
        job_type = type_element.text.strip() if type_element else "Not specified"

        return description, job_type

    except Exception as e:
        print(f"   ❌ Detail error: {e}")
        return "Error", "Error"

def extract_jobs():
    print(f"🚀 STARTING MISSION V3: PRECISION STRIKE")
    print(f"🎯 Target: {BASE_URL}\n")
    
    # --- PHASE 1: SCOUTING (Find Links on Front Page) ---
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Initial connection failed: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("article")
    
    print(f"📦 Found {len(articles)} job candidates. Starting filtering process...\n")
    
    job_list = []

    # --- PHASE 2: INFILTRATION (Visit one by one) ---
    for i, job in enumerate(articles):
        try:
            # Extract Basic Info
            title_element = job.find("a", attrs={"data-automation": "jobTitle"})
            company_element = job.find("a", attrs={"data-automation": "jobCompany"})
            location_element = job.find("a", attrs={"data-automation": "jobLocation"})
            
            if not title_element:
                continue

            title = title_element.text.strip()
            
            # --- 🛑 FILTERING GATE ---
            is_valid, reason = is_relevant_role(title)
            if not is_valid:
                print(f"[{i+1}/{len(articles)}] 🚫 SKIPPING: {title} -> {reason}")
                continue
            # -------------------------

            company = company_element.text.strip() if company_element else "N/A"
            location = location_element.text.strip() if location_element else "N/A"
            link = "https://id.jobstreet.com" + title_element['href']

            print(f"[{i+1}/{len(articles)}] ✅ ACCEPTED: {title} ({company})")

            # CALL DETAIL FUNCTION
            full_description, work_type = get_job_details(link)

            # Store Data
            job_data = {
                "title": title,
                "company": company,
                "location": location,
                "work_type": work_type,
                "posted_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "scraped_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "link": link,
                "description": full_description
            }
            job_list.append(job_data)
            
        except Exception as e:
            print(f"⚠️ Failed to process item {i}: {e}")
            continue

    # --- PHASE 3: SAVE REPORT ---
    if job_list:
        df = pd.DataFrame(job_list)
        
        output_dir = "data/raw"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save CSV
        filename = f"{output_dir}/jobs_v3_filtered_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=False)
        
        print(f"\n✅ MISSION COMPLETE!")
        print(f"💾 Clean Data Saved to: {filename}")
        print(f"📊 Total Relevant Jobs: {len(df)}")
    else:
        print("⚠️ No relevant data found. Check selectors or keywords.")

if __name__ == "__main__":
    extract_jobs()