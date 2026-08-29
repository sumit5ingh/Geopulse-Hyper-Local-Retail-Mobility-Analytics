# GeoPulse — Schema & Tables
## Data Understanding & Data Type Decisions

---

## Analyze CSV Columns

Two source CSV files were analyzed to understand their structure, columns, and data quality before designing the Snowflake schema.

### File 1: `distance_data.csv`

- **Shape:** 500 rows × 10 columns
- **Missing values:** None (0 nulls in every column)

| Column | Sample Value | Description |
|---|---|---|
| device_id | `00696abc-3e18-4654-b046-796ecebd914b` | Unique device identifier (UUID) |
| persona | `Commuter` | Device movement persona (3 categories: Commuter, Resident, Shopper) |
| home_lat | `21.139401` | Home latitude (derived from GPS pings) |
| home_lon | `79.063988` | Home longitude (derived from GPS pings) |
| dist_to_STR001_m | `2036.3` | Distance from home to Store A, in meters |
| dist_to_STR002_m | `2590.6` | Distance from home to Store B, in meters |
| dist_to_STR003_m | `4400.7` | Distance from home to Store C, in meters |
| nearest_store_id | `STR001` | ID of the closest store |
| nearest_store_name | `Store A - Sitabuldi` | Name of the closest store |
| distance_to_nearest_store_m | `2036.3` | Distance to the nearest store, in meters |

**Key columns identified:**
- ID column → `device_id`
- Latitude/Longitude columns → `home_lat`, `home_lon`
- Categorical column → `persona`
- Store reference columns → `nearest_store_id`, `nearest_store_name`

### File 2: `footfall_summary.csv`

- **Shape:** 3 rows × 8 columns
- **Missing values:** None (0 nulls in every column)

| Column | Sample Value | Description |
|---|---|---|
| store_id | `STR001` | Store identifier |
| store_name | `Store A - Sitabuldi` | Store name |
| category | `Supermarket` | Store category (Supermarket, Mall, Hypermarket) |
| date | `2026-08-10` | Date of footfall summary |
| total_visits | `37` | Total number of visits recorded |
| total_dwell_minutes | `2232.0` | Total dwell time across all visits, in minutes |
| unique_visitors | `34` | Count of unique devices that visited |
| avg_dwell_minutes | `60.3` | Average dwell time per visit, in minutes |

**Key columns identified:**
- ID column → `store_id`
- Date column → `date`
- Numeric metric columns → `total_visits`, `total_dwell_minutes`, `unique_visitors`, `avg_dwell_minutes`

---

## Decide Data Types

Based on the column analysis above, the following Snowflake data types were selected for each column.

### `distance_data`

| Column | Snowflake Data Type | Reason |
|---|---|---|
| device_id | VARCHAR(36) | Fixed-length UUID string |
| persona | VARCHAR(20) | Short categorical text |
| home_lat | NUMBER(9,6) | Latitude needs 6 decimal precision |
| home_lon | NUMBER(9,6) | Longitude needs 6 decimal precision |
| dist_to_STR001_m | NUMBER(10,1) | Distance in meters, 1 decimal precision |
| dist_to_STR002_m | NUMBER(10,1) | Same as above |
| dist_to_STR003_m | NUMBER(10,1) | Same as above |
| nearest_store_id | VARCHAR(10) | Short fixed-format code (e.g., STR001) |
| nearest_store_name | VARCHAR(50) | Variable-length text |
| distance_to_nearest_store_m | NUMBER(10,1) | Same range/precision as distance columns |

### `footfall_summary`

| Column | Snowflake Data Type | Reason |
|---|---|---|
| store_id | VARCHAR(10) | Short fixed-format code |
| store_name | VARCHAR(50) | Variable-length text |
| category | VARCHAR(30) | Short categorical text |
| date | DATE | ISO date value |
| total_visits | NUMBER(6,0) | Whole number (count) |
| total_dwell_minutes | NUMBER(10,1) | Decimal minutes |
| unique_visitors | NUMBER(6,0) | Whole number (count) |
| avg_dwell_minutes | NUMBER(6,1) | Decimal minutes |

---

## Summary

- Both datasets are clean, with **zero missing values** across all columns.
- Data types were chosen to balance precision (for coordinates and distances) with storage efficiency (fixed-length VARCHAR for IDs/codes).
- These decisions were implemented using the `CREATE TABLE` statements in Snowflake (see `schema_and_tables.sql`).
