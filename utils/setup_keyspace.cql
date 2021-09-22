CREATE KEYSPACE IF NOT EXISTS wvi WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 3};

CREATE TABLE IF NOT EXISTS wvi.images (
    ts int,
    json_data text,
    PRIMARY KEY (ts)
);

CREATE TABLE IF NOT EXISTS wvi.air_quality (
    ts int,
    json_data text,
    PRIMARY KEY (ts)
);
