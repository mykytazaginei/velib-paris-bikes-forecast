import json
from datetime import datetime, timezone

def convert_to_bool(s):
    return s == 'OUI' 

def parse(records, fetched_at):
    stations_rows, station_status_rows = [], []
    for rec in records:
        stations_rows.append((
            rec['stationcode'], 
            rec['name'], 
            rec['coordonnees_geo']['lon'],
            rec['coordonnees_geo']['lat'],
            rec.get('nom_arrondissement_communes'),
            rec.get('code_insee_commune'),
            rec.get('capacity')
        ))
        station_status_rows.append((
            rec['stationcode'],
            datetime.fromisoformat(rec['duedate']),
            fetched_at,
            rec.get('numdocksavailable'),
            rec.get('numbikesavailable'),
            rec.get('mechanical'),
            rec.get('ebike'),
            convert_to_bool(rec['is_installed']),
            convert_to_bool(rec['is_renting']),
            convert_to_bool(rec['is_returning'])
        ))
    return stations_rows, station_status_rows
    
if __name__ == '__main__':
    with open("./raw_sample.json", encoding="utf-8") as f:
        records = json.load(f)
    stations, station_status = parse(records, datetime.now(timezone.utc))
    print(len(stations), len(station_status))
    print(stations[0])
    print(station_status[0])
    

   