# Week 4 Data Validation Results

## GPS_DATA

| Test | Expected | Actual | Status |
|---|---:|---:|---|
| Row Count | > 0 | 500 | PASS |
| NULL Device ID | 0 | 0 | PASS |
| Invalid Coordinates | 0 | 0 | PASS |
| Future Timestamps | 0 | 0 | PASS |
| Duplicate Records | 0 | 0 | PASS |

## DISTANCE_DATA

| Test | Expected | Actual | Status |
|---|---:|---:|---|
| Row Count | > 0 | ... | PASS |
| Invalid Coordinates | 0 | ... | PASS |
| Negative Distance | 0 | ... | PASS |

## FOOTFALL_SUMMARY

| Test | Expected | Actual | Status |
|---|---:|---:|---|
| Row Count | > 0 | ... | PASS |
| Negative Footfall | 0 | ... | PASS |
| Duplicate Records | 0 | ... | PASS |

## Overall Result

PASS