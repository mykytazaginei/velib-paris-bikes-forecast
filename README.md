# velib-paris-bikes-forecast

Short-term forecast of bike availability at Vélib' stations in Paris. The project collects station snapshots from the open data API into PostgreSQL, analyses them, trains forecasting models and (later) serves the forecast through an API and a dashboard.

## Status

| Stage | Status |
|---|---|
| Data collector (API → Postgres) |  done |
| Containerisation (Docker Compose) |  done |
| Deployment on an always-on server (Windows + Docker Desktop) |  done |
| Automatic weekly backups |  done |
| EDA and data cleaning |  in progress |
| Feature engineering |  planned |
| Baseline model |  planned |
| LightGBM / Prophet, time-based split, rolling backtest |  planned |
| Quality vs. history length analysis |  planned |
| FastAPI service + Docker image |  planned |
| Dashboard |  planned |
| CI, experiment tracking (MLflow) |  planned |

## Architecture

```
opendata.paris.fr API
        │  every 5 min
        ▼
   collector (Python, container)
        │
        ▼
   PostgreSQL 16 (container, named volume)
        │
        ├── weekly pg_dump backups (Task Scheduler on the server)
        ▼
   analysis / models (pandas, notebooks)   ⏳
        │
        ▼
   FastAPI  →  dashboard                   ⏳
```

## Data

Source: the real-time availability dataset `velib-disponibilite-en-temps-reel` on [opendata.paris.fr](https://opendata.paris.fr).

Collection started on 2026-10-26. The collector requests the full snapshot every 5 minutes and stores one row per station update.

Schema ([sql/schema.sql](sql/schema.sql)):

- `stations`: static metadata (`stationcode` PK, name, lon, lat, commune, code_insee, capacity, updated_at).
- `station_status`: availability over time (`stationcode` FK, `duedate`, `fetched_at`, docks, bikes, mechanical, ebike, `is_installed`, `is_renting`, `is_returning`).
  The primary key is `(stationcode, duedate)`, so a station that has not updated between two requests does not create a duplicate (`ON CONFLICT DO NOTHING`).

Key facts about the data:

- **Stations update about once an hour** (around minutes 15-22 UTC), not every 5 minutes. The 5-minute polling only catches the update sooner. Realistic forecast horizons are therefore 1-3 hours.
- `duedate` is the time the station reported its state; `fetched_at` is when the collector received it. Both are stored as `TIMESTAMPTZ` in UTC. Calendar features (hour, weekday, holidays) must be computed in `Europe/Paris`.
- Some stations have a stale `duedate` (as old as 2017). They are excluded from training.
- Closed stations (`is_renting` / `is_returning` = false) are excluded from training.

## Repository layout

```
collector/     parse.py, db.py, run_once.py, loop.py: the collector
sql/           schema.sql
scripts/       backup.ps1: weekly backup for the Windows server
notebooks/     01_eda.ipynb: exploratory analysis
Dockerfile     collector image
docker-compose.yml   db + collector
```

## Running it

Requirements: Docker with Compose.

1. Create `.env` from the example and set a password:

   ```bash
   cp .env.example .env
   ```

2. Start the database and apply the schema (the schema is not applied automatically):

   ```bash
   docker compose up -d db
   docker compose exec -T db psql -U velib -d velib < sql/schema.sql
   ```

3. Start the collector:

   ```bash
   docker compose up -d --build collector
   docker compose logs -f collector
   ```

   Each snapshot is logged as `snapshot saved: +N stations, +M status`.

Note: the database password is fixed when the data volume is first created. Changing `POSTGRES_PASSWORD` in `.env` afterwards does not change it. `docker compose down -v` deletes all data.

## Operations

- The collector runs on a Windows machine with Docker Desktop (WSL2), autologin and power settings that prevent sleep. Both containers use `restart: unless-stopped`; logs are rotated (`json-file`, 10 MB x 3).
- The Postgres port is bound to `127.0.0.1` only.
- **Backups:** [scripts/backup.ps1](scripts/backup.ps1) runs weekly from Task Scheduler. It makes a `pg_dump -Fc`, copies it to `backups/`, checks that the file is not empty, deletes dumps older than 28 days and appends a line to `backups/backup.log`.
- **Restore** into a separate analysis database:

  ```bash
  docker compose up -d db
  docker compose exec db createdb -U velib velib_analysis
  docker compose cp backups/<dump> db:/tmp/velib.dump
  docker compose exec db pg_restore -U velib -d velib_analysis --no-owner /tmp/velib.dump
  docker compose exec db rm /tmp/velib.dump
  ```

  Analysis runs on this copy, not on the live database the collector writes to.

## Problems and solutions

| Problem | Cause | Solution |
|---|---|---|
| Collector crashed with `NoneType` / `NotNullViolation` | The API returns records with missing fields (no coordinates, no name, no station code) | `parse` skips incomplete records and logs one warning per snapshot with the count and the first skipped record |
| New stations appear without metadata (e.g. 1022) | The station shows up in the feed before its name is published | Such records are skipped until the name appears |
| `password authentication failed` | The password is set only at first volume init; a typo in `.env` had already been used | Recreate the volume (`down -v`) or fix the password inside Postgres |
| Collector could not reach the database in Docker | `localhost` inside a container is the container itself | `POSTGRES_HOST=db`, the service name |
| 18-minute gap in the data | The Mac went to sleep | `caffeinate -s`, then moved to an always-on server with sleep disabled |
| Duplicate rows for stations that update hourly | Polling every 5 minutes returns the same `duedate` | Primary key `(stationcode, duedate)` with `ON CONFLICT DO NOTHING` |
| Occasional `JSONDecodeError` | The API sometimes returns a non-JSON response | The error is caught and logged in the loop; the next snapshot is taken as usual |
| Container logs stopped appearing | Output went to a stopped/recreated container's log | Use `docker compose logs -f collector` after recreation |
| Merging Mac and server data | Two databases with overlapping time ranges | `pg_dump --data-only --inserts --on-conflict-do-nothing` and restore on the server |

## Next steps

-  EDA: stale and closed stations, coverage by hour, `fetched_at - duedate` delay, daily profile by weekday/weekend.
-  Choose the time grid for features (hourly, given the update frequency).
-  Features: hour/weekday in Europe/Paris, holidays, weather, neighbouring stations, lags.
-  Baselines (last value, same hour last week), then LightGBM and Prophet with a time-based split and rolling backtest after 3-4 weeks of data.
-  FastAPI service, Docker image, dashboard.
