-- ==========================================
-- 1. ENVIRONMENT SETUP
-- Building Role, Warehouse, and Database from scratch
-- ==========================================

-- Use the highest privilege role for initial setup
USE ROLE ACCOUNTADMIN;

-- Create a custom role for Data Engineer (Best Practice: RBAC)
CREATE ROLE IF NOT EXISTS DATA_ENGINEER_ROLE;
GRANT ROLE SYSADMIN TO ROLE DATA_ENGINEER_ROLE;

-- Create a Cost-Efficient Warehouse (Compute)
CREATE OR REPLACE WAREHOUSE JOB_RADAR_WH 
    WITH WAREHOUSE_SIZE = 'X-SMALL' 
    AUTO_SUSPEND = 60           -- Auto-suspend after 60 seconds of inactivity
    AUTO_RESUME = TRUE          -- Auto-resume when a query is executed
    INITIALLY_SUSPENDED = TRUE;

-- Setup Database & Schema
CREATE OR REPLACE DATABASE JOB_RADAR_DB;
CREATE SCHEMA JOB_RADAR_DB.RAW_DATA;   -- Staging area for scraped data
CREATE SCHEMA JOB_RADAR_DB.ANALYTICS;  -- Cleaned/Processed data

-- Grant usage rights to the Data Engineer Role
GRANT USAGE ON WAREHOUSE JOB_RADAR_WH TO ROLE DATA_ENGINEER_ROLE;
GRANT OWNERSHIP ON DATABASE JOB_RADAR_DB TO ROLE DATA_ENGINEER_ROLE COPY CURRENT GRANTS;
GRANT OWNERSHIP ON ALL SCHEMAS IN DATABASE JOB_RADAR_DB TO ROLE DATA_ENGINEER_ROLE COPY CURRENT GRANTS;

-- Assign Role to your specific User (Replace <YOUR_USERNAME> with your actual username)
GRANT ROLE DATA_ENGINEER_ROLE TO USER <YOUR_USERNAME>;

-- ==========================================
-- 2. TABLE INITIALIZATION
-- Create the staging table for job postings
-- ==========================================

USE ROLE DATA_ENGINEER_ROLE;
USE WAREHOUSE JOB_RADAR_WH;
USE SCHEMA JOB_RADAR_DB.RAW_DATA;

CREATE OR REPLACE TABLE JOB_POSTINGS (
    job_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    description STRING, -- Using STRING to support long text descriptions
    posted_date DATE,
    job_url STRING,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ==========================================
-- 3. DATA QUALITY & EVOLUTION
-- Cleaning data and preparing schema for AI features
-- ==========================================

-- A. Filter: Remove irrelevant job titles (Non-Data Engineering roles)
DELETE FROM JOB_POSTINGS
WHERE NOT (
    UPPER(TITLE) LIKE '%DATA ENGINEER%' OR
    UPPER(TITLE) LIKE '%BIG DATA%' OR
    UPPER(TITLE) LIKE '%ETL%' OR
    UPPER(TITLE) LIKE '%DATA WAREHOUSE%' OR
    UPPER(TITLE) LIKE '%ANALYTICS ENGINEER%'
);

-- B. Schema Evolution: Add column for LLM extraction results
-- (Prepared for future implementation of automated skill extraction)
ALTER TABLE JOB_POSTINGS ADD COLUMN IF NOT EXISTS EXTRACTED_SKILLS TEXT;

-- C. (Optional) Vector Column for Semantic Search capabilities
ALTER TABLE JOB_POSTINGS ADD COLUMN IF NOT EXISTS DESCRIPTION_VECTOR VECTOR(FLOAT, 1024);

-- Data Verification
SELECT COUNT(*) as TOTAL_CLEAN_DATA FROM JOB_POSTINGS;
SELECT * FROM JOB_POSTINGS LIMIT 10;