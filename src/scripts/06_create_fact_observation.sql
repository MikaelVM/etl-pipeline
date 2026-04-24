CREATE TABLE IF NOT EXISTS fact_observation (
    observation_id SERIAL PRIMARY KEY,
    value FLOAT,

    station_id INT,
    FOREIGN KEY (station_id) REFERENCES dim_station(id),

    parameter_id INT,
    FOREIGN KEY (parameter_id) REFERENCES dim_parameter(type_id),

    location_id INT,
    FOREIGN KEY (location_id) REFERENCES dim_location(location_id),

    created INT,
    observed INT,
    FOREIGN KEY (created) REFERENCES dim_datetime(datetime_id),
    FOREIGN KEY (observed) REFERENCES dim_datetime(datetime_id)
);