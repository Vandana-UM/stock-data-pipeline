import os
import requests
import json
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values


def get_db_connection():
    """
    Create and return a PostgreSQL connection using environment variables.
    """
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    if not all([db_name, db_user, db_password]):
        raise ValueError("Database credentials are not fully set in environment variables.")

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
    )
    return conn


def ensure_table_exists(conn):
    """
    Create the table if it doesn't already exist.
    Primary key on (symbol, trade_date) so we can upsert.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS daily_stock_prices (
        symbol TEXT NOT NULL,
        trade_date DATE NOT NULL,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        adjusted_close NUMERIC,
        volume BIGINT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (symbol, trade_date)
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_table_sql)
    conn.commit()


def fetch_stock_data():
    """
    Fetch daily stock data from Alpha Vantage API and return the JSON.
    """

    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    symbol = os.getenv("STOCK_SYMBOL", "AAPL")

    if not api_key:
        raise ValueError("ALPHAVANTAGE_API_KEY is not set in environment variables.")

    function = "TIME_SERIES_DAILY_ADJUSTED"

    url = (
        "https://www.alphavantage.co/query"
        f"?function={function}&symbol={symbol}&apikey={api_key}&outputsize=compact"
    )

    print(f"Requesting data for symbol: {symbol}")
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error while calling Alpha Vantage API:", e)
        raise

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        raise

    # Handle API-specific messages
    if "Error Message" in data:
        raise RuntimeError(f"API returned error: {data['Error Message']}")

    if "Note" in data:
        raise RuntimeError(f"API note (likely rate limit): {data['Note']}")

    return data


def extract_latest_daily_record(symbol, data):
    """
    Extract the most recent day's candle from the Alpha Vantage JSON.
    If Time Series is missing, raise a clear error.
    """
    time_series = data.get("Time Series (Daily)")
    if not time_series:
        raise KeyError("Missing 'Time Series (Daily)' in API response.")

    # keys are dates like "2025-11-26"
    all_dates = sorted(time_series.keys())
    latest_date_str = all_dates[-1]
    latest_data = time_series[latest_date_str]

    # Helper to safely convert strings to float
    def to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    trade_date = datetime.strptime(latest_date_str, "%Y-%m-%d").date()

    record = {
        "symbol": symbol,
        "trade_date": trade_date,
        "open": to_float(latest_data.get("1. open")),
        "high": to_float(latest_data.get("2. high")),
        "low": to_float(latest_data.get("3. low")),
        "close": to_float(latest_data.get("4. close")),
        "adjusted_close": to_float(latest_data.get("5. adjusted close")),
        "volume": int(float(latest_data.get("6. volume", 0) or 0)),
    }

    return record


def upsert_record(conn, record):
    """
    Insert or update the record in PostgreSQL.
    Uses ON CONFLICT on (symbol, trade_date).
    """
    upsert_sql = """
    INSERT INTO daily_stock_prices (
        symbol, trade_date, open, high, low, close, adjusted_close, volume
    )
    VALUES %s
    ON CONFLICT (symbol, trade_date)
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        adjusted_close = EXCLUDED.adjusted_close,
        volume = EXCLUDED.volume;
    """

    values = [
        (
            record["symbol"],
            record["trade_date"],
            record["open"],
            record["high"],
            record["low"],
            record["close"],
            record["adjusted_close"],
            record["volume"],
        )
    ]

    with conn.cursor() as cur:
        execute_values(cur, upsert_sql, values)
    conn.commit()


def main():
    """
    Orchestrates the steps:
    - make sure DB and table exist
    - fetch data from API
    - extract latest daily record (if present)
    - insert/update the record
    """
    symbol = os.getenv("STOCK_SYMBOL", "AAPL")

    # 1) Always ensure DB and table exist first
    try:
        conn = get_db_connection()
        ensure_table_exists(conn)
        conn.close()
        print("Verified that table daily_stock_prices exists (or created it).")
    except Exception as e:
        print("\nDatabase setup failed:")
        print(e)
        # If we can't even reach the DB, no point continuing
        return

    # 2) Then try to fetch data and store it
    try:
        data = fetch_stock_data()
        print("\nTop-level keys in response:", list(data.keys()))

        record = extract_latest_daily_record(symbol, data)
        print("\nLatest record extracted:")
        print(record)

        conn = get_db_connection()
        upsert_record(conn, record)
        conn.close()

        print("\nSuccessfully stored data into PostgreSQL.")

    except KeyError as e:
        # This will catch missing 'Time Series (Daily)' etc.
        print("\nKey error while processing data:", e)
    except Exception as e:
        print("\nSomething went wrong in the pipeline:")
        print(e)



if __name__ == "__main__":
    main()
