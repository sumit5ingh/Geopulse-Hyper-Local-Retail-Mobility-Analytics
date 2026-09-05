

import pandas as pd
import numpy as np
import uuid
from math import radians, sin, cos, sqrt, atan2


#Haversine distance - 2 GPS points ke beech
#distance meters mein nikalta hai (store-proximity
#check ke liye chahiye).


def haversine_distance(lat1, lon1, lat2, lon2):
    """2 GPS points ke beech distance meters mein."""
    R = 6371000  # Earth ka radius meters mein

    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c



#STORE CATALOG - Part 1/2 wale STORES dict se
#match karke banaya hai.


STORE_CATALOG = [
    {"store_id": "STR001", "store_name": "Store A - Sitabuldi", "category": "Supermarket", "lat": 21.1500, "lon": 79.0800},
    {"store_id": "STR002", "store_name": "Store B - Civil Lines", "category": "Mall", "lat": 21.1520, "lon": 79.0850},
    {"store_id": "STR003", "store_name": "Store C - Wardha Road", "category": "Hypermarket", "lat": 21.1000, "lon": 79.0600},
]


#STEP 1: Har GPS ping ke liye nearest store dhoondo
#aur agar wo kisi store ke visit_radius ke andar hai
#to us ping ko "near_store" mark kar do.


def find_nearest_store(lat, lon, store_catalog, visit_radius_m=50):
    """Given a GPS point, closest store dhoondta hai.
    Agar closest store visit_radius ke andar hai to
    store details return karta hai, warna None."""

    nearest_store = None
    min_dist = float("inf")

    for store in store_catalog:
        dist = haversine_distance(lat, lon, store["lat"], store["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest_store = store

    if nearest_store is not None and min_dist <= visit_radius_m:
        return nearest_store, round(min_dist, 1)

    return None, None



#STEP 2: Stay-point detection
#Consecutive pings jo same store ke paas hai unko
#group karke ek "visit" bana (entry_time, exit_time,
#dwell_minutes). Ye hi footfall ka core logic hai.


def detect_store_visits(all_records, store_catalog,
                         visit_radius_m=50, min_dwell_minutes=5):
    """all_records (list of dicts - device_id, timestamp,
    lat, lon wale records) leta hai aur store visits
    (footfall events) ki list return karta hai."""

    records_by_device = {}
    for record in all_records:
        records_by_device.setdefault(record["device_id"], []).append(record)

    for device_id in records_by_device:
        records_by_device[device_id].sort(key=lambda r: r["timestamp"])

    visits = []

    for device_id, records in records_by_device.items():
        current_store = None
        run_records = []

        for record in records:
            store, dist_m = find_nearest_store(
                record["lat"], record["lon"], store_catalog, visit_radius_m
            )
            store_id = store["store_id"] if store else None

            if store_id == current_store and store_id is not None:
                #Same store ke paas continue hai, run badhao.
                run_records.append(record)
            else:
                #Pichla run close karo (agar valid visit bana hai).
                if current_store is not None and run_records:
                    visit = _build_visit_record(
                        device_id, run_records, store_catalog,
                        min_dwell_minutes
                    )
                    if visit:
                        visits.append(visit)

                #Naya run start karo (agar ye point kisi store ke paas hai).
                if store_id is not None:
                    current_store = store_id
                    run_records = [record]
                else:
                    current_store = None
                    run_records = []

        #Loop khatam hone par last run bhi check karo.
        if current_store is not None and run_records:
            visit = _build_visit_record(
                device_id, run_records, store_catalog, min_dwell_minutes
            )
            if visit:
                visits.append(visit)

    return visits


def _build_visit_record(device_id, run_records, store_catalog, min_dwell_minutes):
    """Ek continuous run of pings (same store ke paas) se
    ek visit record banata hai, agar dwell time threshold
    se zyada hai."""

    entry_time = run_records[0]["timestamp"]
    exit_time = run_records[-1]["timestamp"]
    dwell_minutes = round((exit_time - entry_time).total_seconds() / 60, 1)

    if dwell_minutes < min_dwell_minutes:
        return None  #Sirf passing-by hai, actual visit nahi.

    store_id = None
    for record in run_records:
        store, _ = find_nearest_store(record["lat"], record["lon"], store_catalog)
        if store:
            store_id = store["store_id"]
            break

    store_info = next(s for s in store_catalog if s["store_id"] == store_id)

    return {
        "visit_id": str(uuid.uuid4()),
        "device_id": device_id,
        "persona": run_records[0].get("persona"),
        "store_id": store_info["store_id"],
        "store_name": store_info["store_name"],
        "category": store_info["category"],
        "entry_time": entry_time,
        "exit_time": exit_time,
        "dwell_minutes": dwell_minutes,
        "ping_count": len(run_records),
        "date": entry_time.date(),
        "day_of_week": entry_time.strftime("%A"),
    }


#STEP 3: Footfall summary - store-wise aur date-wise
#kitne unique visits + total dwell time hua.


def build_footfall_summary(visits):
    """Store aur date ke hisaab se aggregate footfall summary."""

    summary = {}

    for visit in visits:
        key = (visit["store_id"], visit["date"])

        if key not in summary:
            summary[key] = {
                "store_id": visit["store_id"],
                "store_name": visit["store_name"],
                "category": visit["category"],
                "date": visit["date"],
                "total_visits": 0,
                "unique_devices": set(),
                "total_dwell_minutes": 0.0,
            }

        summary[key]["total_visits"] += 1
        summary[key]["unique_devices"].add(visit["device_id"])
        summary[key]["total_dwell_minutes"] += visit["dwell_minutes"]

    #unique_devices set ko count mein convert karo .
    summary_rows = []
    for row in summary.values():
        row["unique_visitors"] = len(row["unique_devices"])
        row["avg_dwell_minutes"] = round(
            row["total_dwell_minutes"] / row["total_visits"], 1
        )
        del row["unique_devices"]
        summary_rows.append(row)

    return summary_rows




if __name__ == "__main__":

    INPUT_CSV = "gps_data_final.csv"

    print("Reading:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

   
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    #DataFrame ko list of dicts mein convert karo
    
    all_records = df.to_dict(orient="records")

    print("Total records loaded:", len(all_records))

    print("Detecting store visits...")
    visits = detect_store_visits(
        all_records, STORE_CATALOG,
        visit_radius_m=50, min_dwell_minutes=5
    )

    footfall_summary = build_footfall_summary(visits)

    visits_df = pd.DataFrame(visits)
    visits_df.to_csv("store_visits.csv", index=False)
    print("Saved: store_visits.csv -", len(visits), "visits detected")

    summary_df = pd.DataFrame(footfall_summary)
    summary_df.to_csv("footfall_summary.csv", index=False)
    print("Saved: footfall_summary.csv -", len(footfall_summary), "summary rows")

    print()
    print("Part 4 complete!")