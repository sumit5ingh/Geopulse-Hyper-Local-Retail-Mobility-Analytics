# GeoPulse — Hyper-Local Retail Mobility Analytics

Synthetic GPS mobility data generator that simulates realistic device movement
across Nagpur (Wardhaman Nagar, Dharampeth, Sadar) to support hyper-local
retail catchment, footfall, and cannibalization analysis for three stores.

This project was built collaboratively as a 7-day internship-style pipeline.

---

## Project Objective

Simulate a full day of GPS pings for 500 synthetic devices (Resident /
Commuter / Shopper personas), detect store visits from raw location pings,
and analyze store catchment areas — including overlap ("cannibalization")
risk between nearby stores.

---

## Pipeline Overview (Day-by-Day)

| Day | Script | Output | Description |
|-----|--------|--------|-------------|
| 1–2 | `generate_gps_data.py` | `gps_data.csv` | Core GPS journey simulation: home/work/store zones, personas, stationary + route interpolation logic |
| 3 | `generate_gps_metadata.py` | `gps_data_final.csv` | Enriches raw pings with `ping_id`, `sequence_no`, `date`, `day_of_week`, `distance_from_home_m`, device OS, GPS accuracy |
| 4 | `generate_footfall_data.py` | `store_visits.csv`, `footfall_summary.csv` | Stay-point detection (50m radius, 5-min dwell threshold) to identify store visits, then aggregates store-level footfall |
| 5 | `generate_catchment_data.py` | `catchment_data.csv`, `store_catchment_summary.csv` | Reconstructs home locations, computes Haversine distance to every store, assigns catchment ring (0–1km / 1–3km / 3–5km / 5km+), and flags catchment overlap between stores |
| 6 | `validate_data.py` | `validation_report.txt` | Runs 9 automated QA checks across all generated files: nulls, duplicates, persona distribution, date range, bounding box, dwell-time threshold, cross-file consistency, store-level sanity |
| 7 | — | This README + folder cleanup | Finalizes structure and documentation |

Run in order: `generate_gps_data.py` → `generate_gps_metadata.py` → `generate_footfall_data.py` → `generate_catchment_data.py` → `validate_data.py`
(or use `run_pipeline.py` to run all steps automatically — see below).

---

## Folder Structure (current)

All scripts and generated CSVs currently live in the project root, since
each script reads/writes files using relative filenames (e.g.
`"gps_data_final.csv"`). This keeps the pipeline simple and avoids path
issues between steps.

```
GeoPulse-Hyper-Local-Retail-Mobility-Analytics/
├── generate_gps_data.py
├── generate_gps_metadata.py
├── generate_footfall_data.py
├── generate_catchment_data.py
├── validate_data.py
├── run_pipeline.py
├── requirements.txt
├── README.md
├── gps_data.csv
├── gps_data_final.csv
├── store_visits.csv
├── footfall_summary.csv
├── catchment_data.csv
├── store_catchment_summary.csv
└── validation_report.txt
```

> **Future improvement (not yet done):** moving scripts into `/scripts` and
> data into `/data/raw` + `/data/processed` would need each script's
> hardcoded filenames updated to relative paths (e.g.
> `"../data/raw/gps_data.csv"`) first — deferred to avoid breaking the
> already-working, already-merged pipeline.

---

## How to Run

```bash
pip install -r requirements.txt
python run_pipeline.py
```

This runs all five pipeline steps in order (root folder, same as today)
and prints progress for each stage. To run a single step manually instead:

```bash
python generate_gps_data.py
python generate_gps_metadata.py
python generate_footfall_data.py
python generate_catchment_data.py
python validate_data.py
```

---

## Key Design Details

- **Personas**: Resident (40%), Commuter (40%), Shopper (20%) — each with
  distinct daily movement patterns (local errands, office commute, store trip).
- **Store visit detection**: A GPS ping counts as "near a store" within a
  50m radius. Consecutive near-store pings are grouped into a visit only if
  total dwell time is ≥ 5 minutes (filters out pass-by pings).
- **Catchment rings**: Distance from each device's reconstructed home location
  to each store, bucketed into 0–1km, 1–3km, 3–5km, and 5km+ rings.
- **Cannibalization signal**: `catchment_overlap_count` flags homes that fall
  within 3km of more than one store — Store A (Sitabuldi) and Store B
  (Civil Lines) show heavy overlap since they are geographically close,
  while Store C (Wardha Road) is largely independent.

---

## Known Behavior / Limitations

- **Next-day rollover**: Some devices (mostly Commuters with long work
  dwell times) have journeys that extend past midnight into the next
  calendar date. This is expected — journeys are built from realistic
  dwell-time ranges (e.g. 300–420 min at work) rather than clipped to a
  single calendar day, so a small number of pings land on `2026-08-11`
  even though the simulation's primary date is `2026-08-10`. Documented
  in the Day 6 validation report as a known behavior, not a data quality bug.
- **Synthetic data**: All GPS coordinates are simulated (not real user data)
  and are meant purely to demonstrate a hyper-local retail analytics pipeline.

---

## Tech Stack

- Python (pandas, numpy)
- Haversine formula for geospatial distance calculations
- Git / GitHub for collaborative version control

---

## Contributors

- Sumit Singh — Project Lead
- Priti — Day 5 (Catchment/Spatial Analysis) & Day 6 (Data Validation)