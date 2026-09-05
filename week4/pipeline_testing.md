# Pipeline Testing & Automation

## 1. Objective

The objective of pipeline testing is to ensure that data loaded and transformed through the GeoPulse data pipeline is complete, accurate, consistent, and reliable.

The primary dataset used for pipeline testing is:

**GPS_DATA**

Supporting datasets:

- FOOTFALL_SUMMARY
- DISTANCE_DATA

---

## 2. Pipeline Flow

The GeoPulse data pipeline follows the flow:

```text
Raw GPS Data
     |
     v
Data Ingestion
     |
     v
GPS_DATA
     |
     v
Data Validation
     |
     +------------------+
     |                  |
     v                  v
DISTANCE_DATA     FOOTFALL_SUMMARY
     |                  |
     +--------+---------+
              |
              v
       Pipeline Testing
              |
              v
       PASS / FAIL Results