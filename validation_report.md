# Week 2 — Integration and Validation

## Member
Member 4

## Dataset
catchment_data.csv

## Snowflake Table
CATCHMENT_DATA

## Validation Results

| Validation | Result |
|---|---|
| CSV row count | 500 |
| Snowflake row count | 500 |
| Row count match | PASS |
| NULL check | PASS |
| Duplicate device IDs | PASS |
| Latitude validation | PASS |
| Longitude validation | PASS |
| Sample row verification | PASS |
| Snowflake load errors | PASS |
| Store ID integration | PASS/FAIL |
| Footfall integration | PASS/FAIL |
| dbt output integration | PASS/FAIL |

## Integration Summary

The catchment data was loaded into Snowflake and validated.
The catchment, footfall and dbt outputs were checked for
consistent keys and compatible data required for downstream analysis.