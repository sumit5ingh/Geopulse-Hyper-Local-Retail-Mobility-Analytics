# GEOPULSE – Member 2: Database & Warehouse

**Tasks:** Day 1 Create warehouse | Day 2 Create database | Day 3 Configure warehouse | Day 4 Test SQL execution | Day 5–7 Optimization/documentation

**Status: Already built and confirmed** — this documents the live infra.

| Item | Details |
|---|---|
| Database | GEOPULSE_DB |
| Warehouse | GEOPULSE_WH |
| Warehouse size | X-SMALL |
| Auto-resume | TRUE |
| Auto-suspend | 300 seconds |
| Existing schemas | `RAW` (table: GPS_PINGS), `ANALYTICS` (tables: STG_GPS_PINGS, FCT_HOURLY_FOOTFALL) — managed via dbt |

**Note:** `RETAIL_ANALYTICS` (Member 3's schema) sits alongside `RAW` and `ANALYTICS` intentionally — it is a separate, additional schema for the catchment/footfall analysis work, not a naming conflict.

## Test SQL Execution

```sql
USE DATABASE GEOPULSE_DB;
USE WAREHOUSE GEOPULSE_WH;
SHOW SCHEMAS IN DATABASE GEOPULSE_DB;
SHOW TABLES IN SCHEMA GEOPULSE_DB.RAW;
SHOW TABLES IN SCHEMA GEOPULSE_DB.ANALYTICS;
SHOW TABLES IN SCHEMA GEOPULSE_DB.RETAIL_ANALYTICS;
```
GEOPULSE – Member 2: Database & Warehouse

Tasks:
Day 1 Create warehouse
Day 2 Create database
Day 3 Configure warehouse
Day 4 Test SQL execution
Day 5–7 Optimization/documentation

Status:
Already built and confirmed

Member 1 Account & Access Confirmation:
Member 1 has confirmed that the Snowflake Account & Access
setup, including the required roles and access permissions,
has been verified and no changes are required.

Database:
GEOPULSE_DB

Warehouse:
GEOPULSE_WH

Warehouse size:
X-SMALL

Auto-resume:
TRUE

Auto-suspend:
300 seconds