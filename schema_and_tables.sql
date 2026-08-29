-- GeoPulse — Member 3: Schema & Tables
-- Day 3: Create Schema | Day 4: Create Tables

-- Database (created once)
CREATE DATABASE IF NOT EXISTS geopulse_db;

-- Day 3: Schema
CREATE SCHEMA IF NOT EXISTS geopulse_db.retail_analytics;
USE SCHEMA geopulse_db.retail_analytics;

-- Day 4: Tables

CREATE OR REPLACE TABLE distance_data (
    device_id                   VARCHAR(36),
    persona                     VARCHAR(20),
    home_lat                    NUMBER(9,6),
    home_lon                    NUMBER(9,6),
    dist_to_STR001_m            NUMBER(10,1),
    dist_to_STR002_m            NUMBER(10,1),
    dist_to_STR003_m            NUMBER(10,1),
    nearest_store_id            VARCHAR(10),
    nearest_store_name          VARCHAR(50),
    distance_to_nearest_store_m NUMBER(10,1)
);

CREATE OR REPLACE TABLE footfall_summary (
    store_id             VARCHAR(10),
    store_name           VARCHAR(50),
    category             VARCHAR(30),
    date                 DATE,
    total_visits         NUMBER(6,0),
    total_dwell_minutes  NUMBER(10,1),
    unique_visitors      NUMBER(6,0),
    avg_dwell_minutes    NUMBER(6,1)
);

-- Day 5: Test table structure (verification)
DESC TABLE distance_data;
DESC TABLE footfall_summary;
