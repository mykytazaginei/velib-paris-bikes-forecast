import time
from run_once import run_once
import logging

logging.basicConfig(level = logging.INFO, format="%(asctime)s %(levelname)s %(message)s",)
logger = logging.getLogger(__name__)
INTERVAL = 300

def loop():
    while True:
        start = time.monotonic()
        try:
            stations_added, status_added = run_once()
            logger.info("snapshot saved: +%d stations, +%d status", stations_added, status_added)
        except Exception:
            logger.exception('snapshot failed')
        elapsed = time.monotonic() - start
        time.sleep(max(0, INTERVAL - elapsed))

if __name__ == '__main__':
    loop()
    