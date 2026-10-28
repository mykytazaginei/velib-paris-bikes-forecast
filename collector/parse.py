from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def convert_to_bool(s):
    if s is None:
        return None
    return s == 'OUI' 

def parse(records, fetched_at):
    stations_rows, station_status_rows = [], []
    skipped = 0
    first_skipped = None
    for rec in records:
        if not (rec.get('stationcode') and rec.get('name') and rec.get('duedate')):
            skipped +=1
            if first_skipped is None:
                first_skipped = rec
            continue
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
            convert_to_bool(rec.get('is_installed')),
            convert_to_bool(rec.get('is_renting')),
            convert_to_bool(rec.get('is_returning'))
        ))
    logger.warning("skipped %d invalid records, first %r", skipped, first_skipped)
    return stations_rows, station_status_rows