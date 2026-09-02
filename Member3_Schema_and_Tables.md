# GEOPULSE – Member 3: Schema & Tables

**Tasks:** Day 1 Analyze CSV columns | Day 2 Decide data types | Day 3 Create schema | Day 4 Create tables | Day 5 Test table structure | Day 6–7 Documentation/fixes

**Status: Complete — all 7 days done.**

| Item | Details |
|---|---|
| Schema | GEOPULSE_DB.RETAIL_ANALYTICS |
| Tables | `DISTANCE_DATA` (device-level distances to 3 stores, incl. nearest store + distance), `FOOTFALL_SUMMARY` (store-level daily visit metrics) |

## Table Structures

```sql
CREATE OR REPLACE TABLE GEOPULSE_DB.RETAIL_ANALYTICS.FOOTFALL_SUMMARY (
 STORE_ID VARCHAR,
 STORE_NAME VARCHAR,
 CATEGORY VARCHAR,
 DATE DATE,
 TOTAL_VISITS INTEGER,
 TOTAL_DWELL_MINUTES FLOAT,
 UNIQUE_VISITORS INTEGER,
 AVG_DWELL_MINUTES FLOAT
);

CREATE OR REPLACE TABLE GEOPULSE_DB.RETAIL_ANALYTICS.DISTANCE_DATA (
 DEVICE_ID VARCHAR,
 PERSONA VARCHAR,
 HOME_LAT FLOAT,
 HOME_LON FLOAT,
 DIST_TO_STR001_M FLOAT,
 DIST_TO_STR002_M FLOAT,
 DIST_TO_STR003_M FLOAT,
 NEAREST_STORE_ID VARCHAR,
 NEAREST_STORE_NAME VARCHAR,
 DISTANCE_TO_NEAREST_STORE_M FLOAT
);
```

## Key Findings (from analysis built on these tables)
- Store B: highest conversion rate
- Store A: high cannibalization risk
- Store C (STR003, Wardha Road): zero primary catchment homes — flagged as a key business insight
