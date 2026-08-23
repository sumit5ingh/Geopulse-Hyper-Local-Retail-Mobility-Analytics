# GeoPulse - Week 1 Snowflake Setup

## Overview

Week 1 focused on setting up Snowflake as the geospatial data lakehouse for the GeoPulse project.

## Snowflake Setup

- Database: GEOPULSE_DB
- Schema: RAW
- Warehouse: GEOPULSE_WH

## Tables

### GPS_PINGS_RAW
Stores the generated raw GPS data.

### GPS_PINGS
Stores processed GPS data with Snowflake GEOGRAPHY points.

## Dataset

- Total GPS pings: 100,000
- Unique anonymized devices: 9,999
- GPS attributes:
  - DEVICE_ID
  - LATITUDE
  - LONGITUDE
  - EVENT_TIMESTAMP
  - LOCATION

## Geospatial Processing

Latitude and longitude coordinates were converted into Snowflake's native GEOGRAPHY data type using POINT geometry.

## Data Validation

The following validations were performed:

- Total record count
- NULL value check
- Latitude range validation
- Longitude range validation
- Duplicate record check
- Timestamp range validation
- Unique device count
- Geographic boundary validation
- GEOGRAPHY point validation
- Hourly footfall aggregation

## Week 1 Outcome

The GPS dataset was successfully stored and validated in Snowflake and is ready for further spatial processing in the next phase of the GeoPulse project.
