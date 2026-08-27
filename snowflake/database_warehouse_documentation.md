# GeoPulse – Database & Warehouse Documentation

## Database

Database Name:
GEOPULSE_DB

Purpose:
Stores the GeoPulse project data.

## Warehouse

Warehouse Name:
GEOPULSE_WH

Purpose:
Provides compute resources for executing SQL queries
and processing GeoPulse data.

Warehouse Size:
X-SMALL

Auto Resume:
TRUE

Auto Suspend:
300 seconds

## Database Structure

GEOPULSE_DB
├── RAW
│   └── GPS_PINGS
└── ANALYTICS
    ├── STG_GPS_PINGS
    └── FCT_HOURLY_FOOTFALL

## Validation

The warehouse was successfully used to execute SQL queries
against the GeoPulse database and GPS data.

## Optimization

The warehouse uses auto-suspend and auto-resume to reduce
unnecessary compute usage.