import os
import sys
import time
import pandas as pd
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_batch
from zoneinfo import ZoneInfo

# ==== Config from environment ====
DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
    "database": os.getenv("PGDATABASE", "postgres"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres")
}

CSV_FILE = sys.argv[1]

# ==== Read CSV ====
df = pd.read_csv(CSV_FILE, sep='|')
df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'])
df['timestamp'] = df['timestamp'].dt.tz_localize(ZoneInfo("Asia/Ho_Chi_Minh"))

df = df.sort_values('timestamp').reset_index(drop=True)

# ==== Connect to DB ====
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# ==== Prepare insert statement ====
insert_sql = """
    INSERT INTO core.transaction (id, date, time, amt, lat, lon, customer_id, merchant_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id)
    DO UPDATE SET
    date = EXCLUDED.date,
    time = EXCLUDED.time,
    amt = EXCLUDED.amt,
    lat = EXCLUDED.lat,
    lon = EXCLUDED.lon,
    customer_id = EXCLUDED.customer_id,
    merchant_id = EXCLUDED.merchant_id;
"""

# ==== Group by timestamp and replay ====
for ts, group in df.groupby('timestamp'):
    now = datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh"))
    wait_sec = (ts - now).total_seconds()
    if wait_sec > 0:
        print(f"[WAIT] {len(group)} rows at {ts} – sleeping {wait_sec:.2f}s")
        time.sleep(wait_sec)

    # Prepare data tuples
    records = [
        (
            row['id'], row['date'], row['time'], row['amt'],
            row['lat'], row['lon'], row['customer_id'], row['merchant_id']
        ) for _, row in group.iterrows()
    ]

    try:
        execute_batch(cursor, insert_sql, records)
        conn.commit()
        print(f"[INSERTED] {len(records)} rows at {datetime.now()}")
    except Exception as e:
        print(f"[ERROR] Failed to insert batch at {ts}: {e}")
        conn.rollback()

cursor.close()
conn.close()
