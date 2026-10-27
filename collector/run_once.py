import requests
from parse import parse
from db import get_connection, save_snapshot
from datetime import datetime, timezone

URL = ("https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/exports/json")

def count_rows(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM stations") 
        stations_len = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM station_status") 
        status_len = cur.fetchone()[0]
    return stations_len, status_len

def run_once():
    conn = get_connection()
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
    
        records = response.json()
        fetched_at = datetime.now(timezone.utc)
        stations, station_status = parse(records, fetched_at)
        
        stations_len_before, status_len_before = count_rows(conn)
        save_snapshot(conn, stations, station_status)
        stations_len_after, status_len_after = count_rows(conn)
        return stations_len_after - stations_len_before, status_len_after - status_len_before 
    finally:
        conn.close()

if __name__ == '__main__':
    run_once()