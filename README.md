# 📡 Job Radar ID: Indonesian Data Engineering Market Tracker

![Python Badge](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat&logo=python)
![Snowflake Badge](https://img.shields.io/badge/Storage-Snowflake_Data_Warehouse-0093F5.svg?style=flat&logo=snowflake)
![Airflow Badge](https://img.shields.io/badge/Orchestration-Apache_Airflow-017CEE.svg?style=flat&logo=apacheairflow)
![Status Badge](https://img.shields.io/badge/Status-Active_Development-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📖 Project Overview

The Data Engineering landscape in Indonesia is evolving rapidly. Job descriptions are the single source of truth for understanding what skills companies actually demand versus hype.

**Job Radar ID** is an end-to-end Data Engineering project designed to bring transparency to this market. It automates the collection of job postings from major portals (e.g., JobStreet, LinkedIn), ingests the raw data into a cloud data warehouse, and transforms it into actionable insights.

**Primary Objectives:**
1.  **Trend Analysis:** Identify real-time demand for specific technologies (e.g., Is demand for *Spark* growing faster than *Flink* in Jakarta?).
2.  **Skill Gap Detection:** Help engineers align their learning paths with actual market needs.
3.  **ELT Demonstration:** Serve as a proof-of-concept for a modern, scalable **Extract, Load, Transform (ELT)** pipeline using industry-standard tools.

---

## 🏗️ Architecture Blueprint

The system follows a modern **ELT paradigm**, prioritizing the secure storage of raw data before any transformation occurs. This ensures data lineage and allows for reprocessing historic data as business logic evolves.

```mermaid
graph LR
    %% Node Definitions with Styles
    classDef source fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b;
    classDef ingestion fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef storage fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#1b5e20;
    classDef serving fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#4a148c;

    %% The Flow
    subgraph Sources ["1. Data Sources"]
        A[JobPortals (Web)]:::source
    end

    subgraph Ingestion ["2. Extraction Layer"]
        B(Python Scraper Container):::ingestion
    end

    subgraph Warehouse ["3. Storage & Transformation (Snowflake)"]
        C[(RAW_DB Stage)]:::storage
        D[(ANALYTICS_DB Tables)]:::storage
    end

    subgraph Serving ["4. Serving Layer"]
        E[Streamlit Dashboard]:::serving
    end
    
    %% Orchestration Node
    F{Apache Airflow}:::ingestion

    %% Connections
    A -->|HTML/JSON| B
    B -->|Load RAW Data| C
    C -->|dbt/SQL Transform| D
    D -->|Query Insights| E
    F -.->|Trigger Schedule| B
    F -.->|Trigger Schedule| D

```

### 🔄 Data Flow Description

1. **Extraction (The Scout):** A Python-based scraper (utilizing `requests` and `BeautifulSoup`) navigates target job portals, extracting job titles, companies, locations, and full descriptions.
2. **Load (The Transport):** The raw, unprocessed data is immediately loaded into the **Snowflake Data Warehouse** into a staging area (`RAW_DB`). This preserves the original state of the data for auditability.
3. **Transform (The Refinery):** Using SQL within Snowflake’s powerful compute engine, the raw data is cleaned, deduplicated, and enriched. Keywords (technologies, soft skills) are extracted from descriptions to create structured analytics tables (`ANALYTICS_DB`).
4. **Orchestration (The Commander):** Apache Airflow manages the workflow dependencies, ensuring the scraper runs on a schedule and transformations only trigger after data is successfully loaded.

---

## 🛠️ Tech Stack

| Domain | Technology | Justification |
| --- | --- | --- |
| **Ingestion Language** | Python 3.9+ | The standard for web scraping and data manipulation libraries. |
| **Containerization** | Docker | Ensures the scraper runs consistently across local and cloud environments. |
| **Data Warehouse** | Snowflake | Separates storage and compute, allowing scalable processing of raw JSON/text data. |
| **Orchestration** | Apache Airflow | Industry standard for defining complex data pipelines as code (DAGs). |
| **Visualization** | Streamlit | Rapid development of interactive data apps using pure Python. |

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites

* Python 3.9+
* Docker Desktop (Optional for containerization)
* Snowflake Account (Trial or Standard)

### 2. Installation

Clone the repository and set up the environment:

```bash
# Clone repository
git clone [https://github.com/yourusername/job-radar-id.git](https://github.com/yourusername/job-radar-id.git)

# Create Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Usage

Run the scraper to fetch the latest job listings:

```bash
python src/scraper.py

```

The raw data will be saved locally in the `data/raw/` directory as a CSV file before being loaded into Snowflake.

---

## 👨‍💻 Author

[**Bagas Wahyu Herdiansyah**](https://www.google.com/search?q=https://www.linkedin.com/in/bagas-wahyu-herdiansyah/)
