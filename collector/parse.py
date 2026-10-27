from datetime import datetime

def convert_to_bool(s):
    return s == 'OUI' 

def parse(records, fetched_at):
    stations_rows, station_status_rows = [], []
    for rec in records:
        geo = rec.get('coordonnees_geo') or {}
        stations_rows.append((
            rec['stationcode'], 
            rec['name'], 
            geo.get('lon'),
            geo.get('lat'),
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