CREATE TABLE IF NOT EXISTS dim_datetime (
    datetime_id int PRIMARY KEY,
    year smallint,
    month smallint,
    day smallint,
    hour smallint,
    minute smallint,
    second smallint,
    microsecond smallint,
    datetime TIMESTAMP
);