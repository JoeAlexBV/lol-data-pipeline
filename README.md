# Automated Telemetry Pipeline & Analytics Dashboard

## Overview
This project is an end-to-end Data Engineering pipeline that extracts deeply nested match telemetry data from the Riot Games REST API.
Then transforms it into a relational Star Schema, and eventually serves it to a Power BI dashboard for time-intelligence reporting and KPI tracking.

The goal of this project is to demonstrate handling complex JSON hierarchies, implementing rate-limiting/retry logic, and building scalable ETL processes using Python.

## Architecture
*(Note: Architecture diagram coming soon!)*
1. **Ingestion (`src/extract_riot_data.py`):** Python script authenticates with the Riot API, handles `429 Too Many Requests` rate limits via exponential backoff, and extracts raw JSON payloads.
2. **Transformation (`src/transform_riot_data.py`):** Pandas-based ETL script that parses 10,000+ line JSON files, flattens the hierarchy, and models the data into a relational Fact Table (`fact_match_participant`) optimized for BI tools.
3. **Storage:** *(WIP)* AWS S3 for Data Lake storage.
4. **Visualization:** *(WIP)* Power BI for DAX-driven insights (win-rate rolling averages, resource generation KPIs).

## Tech Stack
* **Language:** Python 3.x
* **Libraries:** `pandas`, `requests`, `python-dotenv`
* **Future AWS Integration:** S3, Boto3
* **BI Tool:** Power BI

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/lol_data_pipeline.git
   cd lol_data_pipeline