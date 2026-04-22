CREATE TABLE IF NOT EXISTS dim_time (
    time_id INT(6) PRIMARY KEY,
    hour INT(2) NOT NULL,
    minute INT(2) NOT NULL,
    second INT(2) NOT NULL
);

