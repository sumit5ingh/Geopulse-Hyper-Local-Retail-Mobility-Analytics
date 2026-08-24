


import pandas as pd
import numpy as np
from datetime import datetime


# CONFIG - Part 1/2/3/4/5 wali values se match hai


SIMULATION_DATE = datetime(2026, 8, 10).date()

PERSONA_WEIGHT = {
    "Resident": 0.40,
    "Commuter": 0.40,
    "Shopper": 0.20
}

# Nagpur ke aas-paas ka rough bounding box (thoda buffer ke saath,
# taaki work zones MIHAN/IT Park bhi cover ho jaye).
LAT_MIN, LAT_MAX = 20.90, 21.30
LON_MIN, LON_MAX = 78.90, 79.25

MIN_DWELL_MINUTES = 5
PERSONA_TOLERANCE = 0.05  # 5% tak ka deviation allowed hai random sampling ki wajah se

FILES = {
    "gps": "gps_data_final.csv",
    "visits": "store_visits.csv",
    "footfall": "footfall_summary.csv",
    "catchment": "catchment_data.csv",
    "catchment_summary": "store_catchment_summary.csv",
}

REPORT_LINES = []


def log(line=""):
    """Print bhi karo aur report mein bhi save karo."""
    print(line)
    REPORT_LINES.append(line)


def section(title):
    log()
    log("=" * 60)
    log(title)
    log("=" * 60)



# STEP 1: Load all files (agar missing hai to flag karo)


def load_files():
    dfs = {}
    section("STEP 1: FILE EXISTENCE CHECK")

    for key, filename in FILES.items():
        try:
            df = pd.read_csv(filename)
            dfs[key] = df
            log(f"[OK]   {filename:35s} -> {len(df):,} rows")
        except FileNotFoundError:
            dfs[key] = None
            log(f"[FAIL] {filename:35s} -> FILE NOT FOUND")

    return dfs



# STEP 2: Null / missing value check


def check_nulls(dfs):
    section("STEP 2: NULL / MISSING VALUE CHECK")

    critical_cols = {
        "gps": ["device_id", "lat", "lon", "timestamp", "persona", "ping_id"],
        "visits": ["visit_id", "device_id", "store_id", "entry_time", "exit_time", "dwell_minutes"],
        "footfall": ["store_id", "date", "total_visits", "unique_visitors"],
        "catchment": ["device_id", "home_lat", "home_lon", "nearest_store_id", "catchment_ring"],
        "catchment_summary": ["store_id", "catchment_ring", "homes_in_ring"],
    }

    for key, cols in critical_cols.items():
        df = dfs.get(key)
        if df is None:
            continue

        for col in cols:
            if col not in df.columns:
                log(f"[FAIL] {key}.{col} -> column missing hi nahi hai")
                continue

            null_count = df[col].isna().sum()
            if null_count == 0:
                log(f"[OK]   {key}.{col:30s} -> 0 nulls")
            else:
                log(f"[FAIL] {key}.{col:30s} -> {null_count} nulls found")



# STEP 3: Duplicate / uniqueness check


def check_duplicates(dfs):
    section("STEP 3: DUPLICATE / UNIQUENESS CHECK")

    checks = [
        ("gps", "ping_id", "har GPS ping ki unique ID honi chahiye"),
        ("visits", "visit_id", "har visit ki unique ID honi chahiye"),
        ("catchment", "device_id", "har device ka ek hi catchment record hona chahiye"),
    ]

    for key, col, note in checks:
        df = dfs.get(key)
        if df is None or col not in df.columns:
            continue

        dupes = df[col].duplicated().sum()
        if dupes == 0:
            log(f"[OK]   {key}.{col:15s} -> no duplicates ({note})")
        else:
            log(f"[FAIL] {key}.{col:15s} -> {dupes} duplicates found ({note})")



# STEP 4: Persona distribution check (40/40/20)


def check_persona_distribution(dfs):
    section("STEP 4: PERSONA DISTRIBUTION CHECK (Expected 40/40/20)")

    df = dfs.get("gps")
    if df is None:
        return

    device_persona = df.drop_duplicates("device_id")[["device_id", "persona"]]
    total = len(device_persona)
    actual_dist = device_persona["persona"].value_counts(normalize=True)

    for persona, expected_pct in PERSONA_WEIGHT.items():
        actual_pct = actual_dist.get(persona, 0.0)
        diff = abs(actual_pct - expected_pct)
        status = "OK" if diff <= PERSONA_TOLERANCE else "FAIL"
        log(f"[{status}]   {persona:10s} -> expected {expected_pct:.0%}, "
            f"actual {actual_pct:.1%} (devices: {int(actual_pct * total)})")

    log(f"Total unique devices: {total}")


# STEP 5: Date range sanity check


def check_date_range(dfs):
    section("STEP 5: DATE RANGE SANITY CHECK")

    df = dfs.get("gps")
    if df is None:
        return

    timestamps = pd.to_datetime(df["timestamp"])
    dates = timestamps.dt.date
    unique_dates = dates.unique()

    if len(unique_dates) == 1 and unique_dates[0] == SIMULATION_DATE:
        log(f"[OK]   Saare pings {SIMULATION_DATE} date ke andar hai")
    else:
        log(f"[FAIL] Expected sirf {SIMULATION_DATE}, mila: {sorted(unique_dates)}")

    log(f"Earliest ping: {timestamps.min()}")
    log(f"Latest ping:   {timestamps.max()}")



# STEP 6: Lat/lon bounding box check


def check_bounding_box(dfs):
    section("STEP 6: LAT/LON BOUNDING BOX CHECK (Nagpur region)")

    df = dfs.get("gps")
    if df is None:
        return

    out_of_bounds = df[
        (df["lat"] < LAT_MIN) | (df["lat"] > LAT_MAX) |
        (df["lon"] < LON_MIN) | (df["lon"] > LON_MAX)
    ]

    if len(out_of_bounds) == 0:
        log(f"[OK]   Saare {len(df):,} points bounding box "
            f"({LAT_MIN}-{LAT_MAX}, {LON_MIN}-{LON_MAX}) ke andar hai")
    else:
        log(f"[FAIL] {len(out_of_bounds)} points bounding box se bahar hai")
        log(out_of_bounds[["device_id", "lat", "lon", "activity"]].head().to_string())



# STEP 7: Dwell time threshold check


def check_dwell_time(dfs):
    section("STEP 7: DWELL TIME THRESHOLD CHECK")

    df = dfs.get("visits")
    if df is None:
        return

    invalid = df[df["dwell_minutes"] < MIN_DWELL_MINUTES]

    if len(invalid) == 0:
        log(f"[OK]   Saare {len(df):,} visits ka dwell_minutes >= {MIN_DWELL_MINUTES} hai")
    else:
        log(f"[FAIL] {len(invalid)} visits mein dwell_minutes < {MIN_DWELL_MINUTES} "
            f"(detect_store_visits logic mein bug ho sakta hai)")

    log(f"Avg dwell time: {df['dwell_minutes'].mean():.1f} min")
    log(f"Max dwell time: {df['dwell_minutes'].max():.1f} min")



# STEP 8: Cross-file device_id consistency


def check_cross_file_consistency(dfs):
    section("STEP 8: CROSS-FILE DEVICE_ID CONSISTENCY")

    gps_df = dfs.get("gps")
    visits_df = dfs.get("visits")
    catchment_df = dfs.get("catchment")

    if gps_df is None or catchment_df is None:
        return

    gps_devices = set(gps_df["device_id"].unique())
    catchment_devices = set(catchment_df["device_id"].unique())

    if gps_devices == catchment_devices:
        log(f"[OK]   gps_data_final aur catchment_data ke device_ids exactly match "
            f"karte hai ({len(gps_devices)} devices)")
    else:
        missing_in_catchment = gps_devices - catchment_devices
        extra_in_catchment = catchment_devices - gps_devices
        log(f"[FAIL] Mismatch! Missing in catchment: {len(missing_in_catchment)}, "
            f"Extra in catchment: {len(extra_in_catchment)}")

    if visits_df is not None:
        visit_devices = set(visits_df["device_id"].unique())
        not_in_gps = visit_devices - gps_devices

        if len(not_in_gps) == 0:
            log(f"[OK]   store_visits ke saare device_ids gps_data_final mein maujood hai "
                f"({len(visit_devices)} devices ne visit kiya)")
        else:
            log(f"[FAIL] store_visits mein {len(not_in_gps)} device_ids hai "
                f"jo gps_data_final mein nahi hai")


# STEP 9: Store-level logical sanity checks


def check_store_level_sanity(dfs):
    section("STEP 9: STORE-LEVEL SANITY CHECK")

    footfall_df = dfs.get("footfall")
    visits_df = dfs.get("visits")

    if footfall_df is not None and visits_df is not None:
        total_visits_summary = footfall_df["total_visits"].sum()
        total_visits_raw = len(visits_df)

        if total_visits_summary == total_visits_raw:
            log(f"[OK]   footfall_summary ka total_visits ({total_visits_summary}) "
                f"store_visits row count ({total_visits_raw}) se match karta hai")
        else:
            log(f"[FAIL] Mismatch: footfall_summary total_visits = {total_visits_summary}, "
                f"but store_visits.csv rows = {total_visits_raw}")

        log()
        log("Store-wise visit counts:")
        log(visits_df["store_name"].value_counts().to_string())

    catchment_summary_df = dfs.get("catchment_summary")
    if catchment_summary_df is not None:
        log()
        log("Catchment ring distribution (per store):")
        pivot = catchment_summary_df.pivot(
            index="store_name", columns="catchment_ring", values="homes_in_ring"
        )
        log(pivot.to_string())


# MAIN


def main():
    log("GEOPULSE - DAY 6 DATA VALIDATION REPORT")
    log(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    dfs = load_files()
    check_nulls(dfs)
    check_duplicates(dfs)
    check_persona_distribution(dfs)
    check_date_range(dfs)
    check_bounding_box(dfs)
    check_dwell_time(dfs)
    check_cross_file_consistency(dfs)
    check_store_level_sanity(dfs)

    section("VALIDATION COMPLETE")
    log("Report saved to: validation_report.txt")

    with open("validation_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(REPORT_LINES))


if __name__ == "__main__":
    main()