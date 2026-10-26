CREATE TABLE IF NOT EXISTS stations(
    stationcode TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    lon DOUBLE PRECISION,
    lat DOUBLE PRECISION,
    commune TEXT,
    code_insee TEXT,
    capacity INTEGER,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS station_status(
    stationcode TEXT NOT NULL REFERENCES stations(stationcode),
    duedate TIMESTAMPTZ NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    numdocksavailable INTEGER,
    numbikesavailable INTEGER,
    mechanical INTEGER, 
    ebike INTEGER,
    is_installed BOOLEAN,
    is_renting BOOLEAN,
    is_returning BOOLEAN, 
    PRIMARY KEY(stationcode, duedate)
);

CREATE INDEX IF NOT EXISTS idx_status_duedate ON station_status(duedate);