-- =========================================================
-- FILE: sql/transform_skills.sql
-- PURPOSE: Extract ALL skills (Hard & Soft) using Snowflake Cortex
-- MODEL: claude-3-5-sonnet (Highly recommended for context understanding)
-- =========================================================

UPDATE RAW_DATA.JOB_POSTINGS
SET EXTRACTED_SKILLS = SNOWFLAKE.CORTEX.COMPLETE(
    'claude-3-5-sonnet',
    CONCAT(
        'You are an expert Technical Recruiter. Your task is to extract ALL relevant skills from the job description below.',
        '\n\nRules:',
        '\n1. Extract Technical Skills (Python, SQL, AWS, etc.).',
        '\n2. Extract Soft Skills (Communication, Leadership, Problem Solving, etc.).',
        '\n3. Extract Domain Knowledge (ETL, Data Warehousing, Banking, Finance, etc.).',
        '\n4. COMBINE all of them into a single comma-separated list.',
        '\n5. Output MUST be CLEAN. Just the list. No labels like "Hard Skills:" or "Soft Skills:".',
        '\n6. If the text is in Indonesian, translate the skill concept to standard English terms if possible (e.g., "Bisa kerjasama" -> "Teamwork"), otherwise keep as is.',
        '\n\nJob Description:\n', 
        DESCRIPTION -- <--- CRITICAL: Reading full text description
    )
)
-- Process rows that haven't been processed OR process again to update existing bad results
WHERE (EXTRACTED_SKILLS IS NULL OR EXTRACTED_SKILLS = '')
  AND DESCRIPTION IS NOT NULL;