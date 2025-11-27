# Dockerized Stock Data Pipeline (Dagster + PostgreSQL)

A fully containerized data pipeline that fetches stock market data from the AlphaVantage API, processes it, and stores it in a PostgreSQL database.  
The workflow is orchestrated using **Dagster**, running inside Docker for easy deployment.

This project is built as part of a technical assessment for a Python / Data Engineering internship.

-----------------------------------------------------------------------------------------------------------------------------------------------

## 🚀 Features

- **Dagster orchestration** (jobs + schedules)
- **Docker Compose-based deployment**
- **Automatic data fetching** from AlphaVantage API
- **Daily scheduled pipeline** (via Dagster schedule)
- **PostgreSQL storage**
- **Environment variable–based secrets** (.env file)
- **Graceful error handling** for missing or limited API data
- **Modular Python code (clean structure)**

-----------------------------------------------------------------------------------------------------------------------------------------------

## 📂 Project Structure
    stock-data-pipeline/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
│
└── src/
├── fetch_stock_data.py
├── dagster_defs.py
└── init.py

-----------------------------------------------------------------------------------------------------------------------------------------------

1.yaml
   

    ## 🛠️ Technologies Used

    - **Python 3.11**
    - **Dagster** (orchestration)
    - **PostgreSQL 15**
    - **Docker & Docker Compose**
    - **AlphaVantage API**
    - **psycopg2** (PostgreSQL connector)
    - **requests** (API calls)

   

    ## 🔧 Setup Instructions

    ### 1. Clone the repository
    ```bash
    git clone <your-repo-url>
    cd stock-data-pipeline

-----------------------------------------------------------------------------------------------------------------------------------------------

2. Create a .env file

    API_KEY=YOUR_ALPHA_VANTAGE_KEY
    DB_NAME=stocks
    DB_USER=stock_user
    DB_PASSWORD=stock_pass
    DB_HOST=postgres
    DB_PORT=5432

-----------------------------------------------------------------------------------------------------------------------------------------------

3. Start the pipeline with Docker Compose

bash
    docker compose up --build


This will:

start PostgreSQL

start Dagster webserver

expose Dagster at http://localhost:3000

-----------------------------------------------------------------------------------------------------------------------------------------------

🗂️ Dagster UI

Visit:

    👉 http://localhost:3000

You will see:

    stock_pipeline_job under Jobs
    daily_stock_schedule under Automation

You can trigger a run manually:

    Go to Jobs → stock_pipeline_job
    Click Launchpad
    Click Launch Run

-----------------------------------------------------------------------------------------------------------------------------------------------

📊 Database Schema

Table created: daily_stock_prices

Column	        Type
------         ------
symbol	        TEXT
date	        DATE
open_price	    NUMERIC
high_price	    NUMERIC
low_price	    NUMERIC
close_price	    NUMERIC
volume	        BIGINT

To view data:
bash 
    docker exec -it stock_postgres psql -U stock_user -d stocks
    SELECT * FROM daily_stock_prices LIMIT 10;

-----------------------------------------------------------------------------------------------------------------------------------------------

🛡️ Error Handling

The pipeline includes:

    API timeout handling
    JSON parsing safeguards
    Missing key detection
    Graceful fallback logs when API returns informational messages
    Retry-friendly structure

Dagster logs all events for visibility. 

-----------------------------------------------------------------------------------------------------------------------------------------------

📅 Scheduling

The job is configured to run daily at:
        12:00 AM (GMT+5:30 IST)

You can toggle the schedule in Dagster:

    Go to Automation → daily_stock_schedule
    Use the toggle switch to enable/disable it

-----------------------------------------------------------------------------------------------------------------------------------------------

🧪 Testing the Setup

After running:
bash
    docker compose up --build


Check:

    Dagster UI: http://localhost:3000
    PostgreSQL connection
    Logs of stock_pipeline_job


A successful run will show:

    STEP_SUCCESS: run_pipeline_op
    RUN_SUCCESS: stock_pipeline_job

-----------------------------------------------------------------------------------------------------------------------------------------------

📝 Notes

    Free AlphaVantage API keys sometimes return limited data during high usage periods.

    The pipeline handles such cases and logs the issue cleanly.

    Docker ensures the entire setup works identically on any machine.

-----------------------------------------------------------------------------------------------------------------------------------------------

🙋‍♂️ Author

    Vandana U M

-----------------------------------------------------------------------------------------------------------------------------------------------

📬 Contact

If you have any questions or would like additional details:

Email: vandana13426@gmail.com

-----------------------------------------------------------------------------------------------------------------------------------------------