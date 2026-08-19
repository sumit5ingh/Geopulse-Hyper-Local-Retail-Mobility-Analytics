"""
GeoPulse - Week 2: Data Cleaning
Task: gps_data_final.csv aur store_visits.csv  clean 
      datetime conversion, duplicate removal, range validation,
      and row-count reconciliation (gps_data.csv vs gps_data_final.csv).

Output: gps_data_final_clean.csv, store_visits_clean.csv,
        data_cleaning_report.txt
"""

import pandas as pd
import numpy as np

# STEP 0: Config - Nagpur ke around expected lat/lon bounds.
# generate_gps_data.py ke HOME_ZONE / WORK_ZONES / STORES sab
# isi range ke andar hain, isliye bounding box validation ke
# liye reference bana rahe hai.


LAT_MIN, LAT_MAX = 20.5, 21.6
LON_MIN, LON_MAX = 78.5, 79.6

MIN_DWELL_MINUTES = 5  # generate_footfall_data.py wale threshold se match


# STEP 1: GPS data cleaning


def clean_gps_data(df):
    """gps_data_final.csv ko clean karta hai:
    - timestamp/date ko proper datetime mein convert
    - duplicate rows drop
    - lat/lon/distance/accuracy range validate
    Ek (cleaned_df, issues_dict) tuple return karta hai."""

    issues = {}
    df = df.copy()

    # --- datatype fix: timestamp/date string se datetime ---
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

    bad_timestamps = df["timestamp"].isnull().sum()
    issues["unparseable_timestamps"] = int(bad_timestamps)
    if bad_timestamps > 0:
        df = df[df["timestamp"].notnull()]

    # --- duplicate rows (safety net, expected 0) ---
    dup_count = df.duplicated().sum()
    issues["duplicate_rows_dropped"] = int(dup_count)
    df = df.drop_duplicates()

    # --- duplicate ping_id (har ping unique hona chahiye) ---
    dup_ping_ids = df["ping_id"].duplicated().sum()
    issues["duplicate_ping_ids"] = int(dup_ping_ids)
    df = df.drop_duplicates(subset="ping_id")

    # --- lat/lon bounding box check ---
    out_of_bounds = df[
        (df["lat"] < LAT_MIN) | (df["lat"] > LAT_MAX) |
        (df["lon"] < LON_MIN) | (df["lon"] > LON_MAX)
    ]
    issues["out_of_bounds_coordinates"] = int(len(out_of_bounds))
    df = df.drop(out_of_bounds.index)

    # --- distance_from_home_m aur gps_accuracy_m negative nahi honi chahiye ---
    negative_distance = (df["distance_from_home_m"] < 0).sum()
    issues["negative_distance_from_home"] = int(negative_distance)
    df = df[df["distance_from_home_m"] >= 0]

    negative_accuracy = (df["gps_accuracy_m"] < 0).sum()
    issues["negative_gps_accuracy"] = int(negative_accuracy)
    df = df[df["gps_accuracy_m"] >= 0]

    return df, issues



# STEP 2: Store visits cleaning


def clean_store_visits(df):
    """store_visits.csv ko clean karta hai:
    - entry_time/exit_time ko datetime mein convert
    - exit_time < entry_time wali invalid rows nikaalna
    - dwell_minutes threshold se kam wali rows check karna"""

    issues = {}
    df = df.copy()

    df["entry_time"] = pd.to_datetime(df["entry_time"], errors="coerce")
    df["exit_time"] = pd.to_datetime(df["exit_time"], errors="coerce")

    bad_times = df["entry_time"].isnull().sum() + df["exit_time"].isnull().sum()
    issues["unparseable_visit_times"] = int(bad_times)
    df = df[df["entry_time"].notnull() & df["exit_time"].notnull()]

    invalid_order = df[df["exit_time"] < df["entry_time"]]
    issues["exit_before_entry_rows"] = int(len(invalid_order))
    df = df.drop(invalid_order.index)

    below_threshold = df[df["dwell_minutes"] < MIN_DWELL_MINUTES]
    issues["dwell_below_threshold"] = int(len(below_threshold))
    df = df.drop(below_threshold.index)

    dup_visit_ids = df["visit_id"].duplicated().sum()
    issues["duplicate_visit_ids"] = int(dup_visit_ids)
    df = df.drop_duplicates(subset="visit_id")

    return df, issues



# STEP 3: Row-count reconciliation - gps_data.csv (raw) vs
# gps_data_final.csv (enriched). Row count kam hona expected
# hai agar koi pings enrichment stage pe drop hue hai; ye sirf
# uska size document karta hai taaki analysis stage pe surprise
# na ho.


def reconcile_row_counts(raw_df, final_df_clean):
    return {
        "raw_gps_rows": len(raw_df),
        "final_gps_rows_before_clean": None,  # caller fill karega
        "final_gps_rows_after_clean": len(final_df_clean),
        "rows_missing_vs_raw": len(raw_df) - len(final_df_clean),
    }


# STEP 4: Report likhna - GeoPulse documentation style



def write_report(gps_issues, visits_issues, reconciliation, path="data_cleaning_report.txt"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("GEOPULSE - DATA CLEANING REPORT\n")
        f.write("Week 2: Catchment Area Analysis - Data Cleaning\n")
        f.write("=" * 60 + "\n\n")

        f.write("1. GPS DATA (gps_data_final.csv)\n")
        f.write("-" * 40 + "\n")
        for k, v in gps_issues.items():
            f.write(f"{k}: {v}\n")
        f.write("\n")

        f.write("2. STORE VISITS (store_visits.csv)\n")
        f.write("-" * 40 + "\n")
        for k, v in visits_issues.items():
            f.write(f"{k}: {v}\n")
        f.write("\n")

        f.write("3. ROW COUNT RECONCILIATION (raw vs final GPS data)\n")
        f.write("-" * 40 + "\n")
        for k, v in reconciliation.items():
            f.write(f"{k}: {v}\n")
        f.write("\n")

        f.write("4. NOTES\n")
        f.write("-" * 40 + "\n")
        f.write("- catchment_data.csv mein har home ka catchment_ring sirf\n")
        f.write("  '1-3km' ya '3-5km' hi aaya - koi bhi home '0-1km' ya '5km+'\n")
        f.write("  mein nahi hai. Ye data bug nahi hai (ring mismatch = 0), balki\n")
        f.write("  ek possible business finding hai - analysis stage pe flag karo.\n")

# MAIN


if __name__ == "__main__":

    print("Reading raw files...")
    gps_raw = pd.read_csv("gps_data.csv")
    gps_final = pd.read_csv("gps_data_final.csv")
    visits = pd.read_csv("store_visits.csv")

    print("Cleaning gps_data_final.csv...")
    gps_final_clean, gps_issues = clean_gps_data(gps_final)
    print("  Issues found:", gps_issues)

    print("Cleaning store_visits.csv...")
    visits_clean, visits_issues = clean_store_visits(visits)
    print("  Issues found:", visits_issues)

    print("Reconciling row counts (raw gps_data vs cleaned gps_data_final)...")
    reconciliation = reconcile_row_counts(gps_raw, gps_final_clean)
    reconciliation["final_gps_rows_before_clean"] = len(gps_final)
    print("  ", reconciliation)

    gps_final_clean.to_csv("gps_data_final_clean.csv", index=False)
    print("Saved: gps_data_final_clean.csv -", len(gps_final_clean), "rows")

    visits_clean.to_csv("store_visits_clean.csv", index=False)
    print("Saved: store_visits_clean.csv -", len(visits_clean), "rows")

    write_report(gps_issues, visits_issues, reconciliation)
    print("Saved: data_cleaning_report.txt")

    print()
    print("Data cleaning complete!")