from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from parse import parse
import json
from datetime import datetime, timezone
import os

stations_sql = """
INSERT INTO stations (stationcode, name, lon, lat, commune, code_insee, capacity)
VALUES %s
ON CONFLICT (stationcode) DO UPDATE SET
    name = EXCLUDED.name,
    lon = EXCLUDED.lon,
    lat = EXCLUDED.lat,
    commune = EXCLUDED.commune,
    code_insee = EXCLUDED.code_insee,
    capacity = EXCLUDED.capacity,
    updated_at = now();
"""
status_sql = """
INSERT INTO station_status (stationcode, duedate, fetched_at, numdocksavailable, numbikesavailable, mechanical, ebike, is_installed, is_renting, is_returning)
VALUES %s
ON CONFLICT (stationcode, duedate) DO NOTHING;
"""

load_dotenv()
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

def get_connection():
    return psycopg2.connect(host='localhost', port=5432, dbname='velib', user='velib', password=POSTGRES_PASSWORD)

def save_snapshot(conn, stations_rows, status_rows):
    with conn:
        with conn.cursor() as cur:
            execute_values(cur, stations_sql, stations_rows)
            execute_values(cur, status_sql, status_rows)
            
if __name__ == '__main__':

    with open("./raw_sample.json", encoding="utf-8") as f:
        records = json.load(f)
    stations, station_status = parse(records, datetime.now(timezone.utc))

    conn = get_connection()
    try:
        save_snapshot(conn, stations, station_status)
        with conn.cursor() as cur:
           cur.execute("SELECT count(*) FROM stations") 
           print(cur.fetchone())
           cur.execute("SELECT count(*) FROM station_status") 
           print(cur.fetchone())
    finally:
        conn.close()