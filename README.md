# GeoPulse — Hyper-Local Retail Mobility Analytics

Hyper-local retail mobility analytics project built for 3 sample stores in Nagpur. The pipeline simulates device GPS pings, derives each device's home location and persona (Commuter / Resident / Shopper), calculates distance to each store, detects store visits/footfall, loads everything into Snowflake, and finally visualizes it as an interactive Power BI dashboard.

**Organization:** Infotact Solutions
**Contributor:** Priti Sivakumar Molukwan — Member 3 (Schema & Tables / Dashboard)

---

## Pipeline Overview

```
GPS ping generation
      ↓
Metadata enrichment (persona, home location)
      ↓
Footfall / visit detection
      ↓
Haversine distance-to-store calculation
      ↓
Catchment rules (ring classification)
      ↓
Data cleaning
      ↓
Snowflake load (schema & tables)
      ↓
Power BI dashboard
```

- **Distance calculation:** Haversine formula — earth-curvature-aware great-circle distance between two lat/lon points, standard for short local distances.
- **Data type:** Fully simulated/synthetic — 500 devices with generated GPS movement patterns across three personas, built to demonstrate an end-to-end retail mobility analytics pipeline without using real customer data.

---

## Week 1–2 (context)

- GPS ping data generation, metadata enrichment, footfall/visit detection, and Haversine distance-to-store calculation scripts (`generate_gps_data.py`, `generate_gps_metadata.py`, `generate_footfall_data.py`, `generate_distance_data.py`).
- Store-wise catchment analysis completed and merged via PR into the main branch.

---

## Week 3 — Schema & Tables (Snowflake)

**Role:** Member 3 — Schema & Tables
**Database / Schema:** `GEOPULSE_DB.RETAIL_ANALYTICS`

| Day | Task |
|---|---|
| 1 | Analyzed source CSVs — `distance_data.csv` (500 rows × 10 cols, 0 nulls), `footfall_summary.csv` (3 rows × 8 cols, 0 nulls) |
| 2 | Decided Snowflake data types for every column |
| 3 | Created schema `geopulse_db.retail_analytics` |
| 4 | Created tables `distance_data` and `footfall_summary` |
| 5 | Verified table structure with `DESC TABLE` |
| 6–7 | Documentation + corrected Member 1/Member 2 docs (wrong database/schema names) so Week 4 could start without delay |

### Table: `distance_data` (500 rows — one per device)

| Column | Data Type | Reason |
|---|---|---|
| device_id | VARCHAR(36) | Fixed-length UUID string |
| persona | VARCHAR(20) | Short categorical text |
| home_lat / home_lon | NUMBER(9,6) | 6-decimal precision needed for GPS coordinates |
| dist_to_STR00x_m | NUMBER(10,1) | Distance in metres, 1-decimal precision |
| nearest_store_id | VARCHAR(10) | Short fixed-format code, e.g. STR001 |
| nearest_store_name | VARCHAR(50) | Variable-length text |
| distance_to_nearest_store_m | NUMBER(10,1) | Same range/precision as distance columns |

### Table: `footfall_summary` (store-level daily visit metrics)

| Column | Data Type | Reason |
|---|---|---|
| store_id | VARCHAR(10) | Short fixed-format code |
| store_name | VARCHAR(50) | Variable-length text |
| category | VARCHAR(30) | Short categorical text (Supermarket / Mall / Hypermarket) |
| date | DATE | ISO date value |
| total_visits / unique_visitors | NUMBER(6,0) | Whole-number counts |
| total_dwell_minutes / avg_dwell_minutes | NUMBER(10,1) / NUMBER(6,1) | Decimal minutes |

---

## Week 4 — Final Interactive Dashboard (Power BI)

Connected Power BI to Snowflake (`geopulse_db.retail_analytics`), built the data model, and delivered a two-page dashboard: KPI + charts view, and a residential-zone map view.

### KPI Cards

| KPI | Value | Meaning |
|---|---|---|
| Total Device | 500 | Total unique devices tracked across the simulation |
| Total Stores | 3 | Store A – Sitabuldi, Store B – Civil Lines, Store C – Wardha Road |
| Total Footfall | 132 | Total store-visit events (count of `visit_id`) across all 3 stores |
| Average Footfall | 44.00 | Total Footfall ÷ Total Stores = 132 / 3 |
| Peak Hour | 11 | Hour of day with the highest number of visits |

### Charts

1. **Count of visit_id by Hour** — Visits peak sharply at 11 AM, stay strong at 10 AM/12 PM, drop off by 1 PM. Footfall is concentrated in a narrow late-morning window.
2. **Store Visits by Persona** — Shows 100% Shopper (85 visits), by design: visit-detection logic only tags an event as a store visit when movement matches shopping behaviour, so Commuter/Resident don't generate visit records yet (they do appear on the home-location map).
3. **Sum of homes_in_ring** (by store & catchment ring — Core 0–1km, Primary 1–3km, Extended 3–5km, Out of Range 5km+):
   - Store A – Sitabuldi: 338 homes Primary, 162 Extended
   - Store B – Civil Lines: all 500 homes in Primary — strongest, most concentrated catchment
   - Store C – Wardha Road: 0 homes in Core/Primary; 176 Extended, 324 Out-of-Range
4. **Total Footfall by Day** — Currently a single-day snapshot (~130 visits, dated 2026-08-10), not yet a multi-day trend.
5. **Total Footfall by Store** — Store C (~152) > Store B (~130) > Store A (~120). Store C has the highest footfall despite the weakest nearby catchment — it behaves like a **destination store** (people travel from far), while Store B has a perfect local catchment but only mid-tier footfall (nearby homes aren't fully converting yet).
6. **Filters/Slicers** — Interactive persona and store_name slicers filter every visual live.

### Map — Device Homes by Residential Zone

Plots average `home_lat`/`home_lon` grouped by `device_id` and persona:
- 🟢 Green — near Bijli Nagar / Mohan Nagar (west-central Nagpur)
- 🔵 Blue — near Ganesh Wadi / Taj Nagar (north-east Nagpur)
- 🟡 Orange/yellow — near Bhagwaghar Layout / Dharampeth (south-west Nagpur)

The 500 simulated devices were generated around three distinct home clusters (one per persona) rather than scattered randomly — confirming personas genuinely live in different parts of town, and explaining why only Shopper converts to visits in this dataset.

---

## Business Insights

- **Store B (Civil Lines):** Strong, fully local catchment — best candidate for loyalty/nearby-offer campaigns.
- **Store C (Wardha Road):** Destination-store pattern — highest footfall despite near-zero local catchment; worth a deeper look at where its customers are actually traveling from.
- **Store A (Sitabuldi):** 162 homes in the Extended ring — a good target for promotions to pull them into the Primary catchment.

---

## Known Limitations / Next Steps

- Footfall data currently covers a single day — needs a multi-day time series.
- Visit-detection logic currently only fires for the Shopper persona — Commuter/Resident visit-triggering logic still to be added.
- Persona pie chart total (85) vs. Total Footfall KPI (132) — a known data-consistency gap to reconcile in the next iteration (likely a null/non-null persona filtering difference).

---

## Git Workflow

- Separate branch per week: `priti-project` (Week 1–3), `priti-week4-dashboard` (Week 4).
- Selective staging, PR-based merges into `main`.
- Feature branches deleted after successful merge/review.

---

## Glossary

| Term | Meaning |
|---|---|
| Footfall | A store-visit event — when a device shows a 'visit' pattern near a store |
| Catchment ring | Distance-based zone around a store — Core (0–1km), Primary (1–3km), Extended (3–5km), Out of Range (5km+) |
| Cannibalization risk | When two stores share the same customer catchment, one store eats into the other's business |
| Destination store | A store where customers travel from far rather than from the immediate neighbourhood |
| Persona | Customer type derived from device movement pattern — Commuter, Resident, or Shopper |
| Haversine distance | Earth-curvature-aware real-world distance between two GPS coordinates |
