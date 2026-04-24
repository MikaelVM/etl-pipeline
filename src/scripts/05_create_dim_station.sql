CREATE TABLE IF NOT EXISTS dim_station (
    id SERIAL PRIMARY KEY,

    name VARCHAR(255),
    country VARCHAR(255),
    country_code VARCHAR(4),
    status VARCHAR(255),
    owner VARCHAR(255),
    station_id VARCHAR(5),
    wmo_station_id VARCHAR(5),
    wmo_country_code VARCHAR(4),
    region_id VARCHAR(4),
    station_height FLOAT,
    anemometer_height FLOAT,
    barometer_height FLOAT,
    parameter_id VARCHAR(255)[],

    created INT,
    operated_from INT,
    operated_to INT,
    valid_from INT,
    valid_to INT,
    updated INT,
    FOREIGN KEY (created) REFERENCES dim_datetime(datetime_id),
    FOREIGN KEY (operated_from) REFERENCES dim_datetime(datetime_id),
    FOREIGN KEY (operated_to) REFERENCES dim_datetime(datetime_id),
    FOREIGN KEY (valid_from) REFERENCES dim_datetime(datetime_id),
    FOREIGN KEY (valid_to) REFERENCES dim_datetime(datetime_id),
    FOREIGN KEY (updated) REFERENCES dim_datetime(datetime_id),

    location_id INT,
    FOREIGN KEY (location_id) REFERENCES dim_location(location_id)
);