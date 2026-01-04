# 📡 Job Radar ID: Data Engineering Market Tracker

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Status](https://img.shields.io/badge/Status-Active_Development-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Job Radar ID** is an automated **ELT (Extract, Load, Transform)** pipeline designed to monitor the Data Engineering job market in Indonesia. This project aims to provide real-time insights into high-demand technologies (e.g., AWS vs. GCP, Spark vs. Flink) by analyzing job descriptions from major job portals.

---

## 🏗️ Architecture Blueprint

This system utilizes a modern **ELT approach** where raw data is ingested directly into Snowflake before transformation, ensuring data lineage and flexibility.

```mermaid
graph LR
    %% Style Definition
    classDef source fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#bbf,stroke:#333,stroke-width:2px;
    classDef db fill:#bfb,stroke:#333,stroke-width:2px;

    %% Nodes
    A[Job Portals]:::source -->|Scrape HTML| B(Python Scraper):::process
    B -->|Raw CSV/JSON| C[(Snowflake RAW)]:::db
    C -->|SQL Transformation| D[(Snowflake ANALYTICS)]:::db
    D -->|Visualize Trends| E[Streamlit Dashboard]:::process
    
    %% Orchestration
    F{Apache Airflow}:::process -.->|Schedule Daily| B
