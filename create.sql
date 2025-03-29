CREATE TABLE IF NOT EXISTS weather (
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    base TEXT NOT NULL,
    description TEXT NOT NULL,
    time TIMESTAMP NOT NULL,
    temperature FLOAT NOT NULL,
    min_temp FLOAT NOT NULL,
    max_temp FLOAT NOT NULL,
    pressure INT NOT NULL,
    humidity INT NOT NULL,
    visibility INT NOT NULL,
    wind_speed FLOAT NOT NULL,
    wind_deg INT NOT NULL
);

CREATE TABLE IF NOT EXISTS pollution (
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    time TIMESTAMP NOT NULL,
    aqi INT NOT NULL,
    co FLOAT NOT NULL,
    no FLOAT NOT NULL,
    no2 FLOAT NOT NULL,
    o3 FLOAT NOT NULL,
    so2 FLOAT NOT NULL,
    pm2_5 FLOAT NOT NULL,
    pm10 FLOAT NOT NULL,
    nh3 FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    timezone INT NOT NULL
);