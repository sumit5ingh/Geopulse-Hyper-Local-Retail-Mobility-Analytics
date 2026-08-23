"""
GeoPulse - Store-wise Catchment Analysis

Ye script har store ke liye ek complete catchment health-check
banata hai, catchment_rules.py ke RULE-based output
(catchment_data_with_rules.csv) aur footfall data
(footfall_summary.csv) ko combine karke.

Input files (same folder mein ):
  - catchment_data_with_rules.csv   (catchment_rules.py ka output)
  - footfall_summary.csv            (generate_footfall_data.py ka output)

Output files:
  - store_wise_catchment_analysis.csv   -> master store-wise table
  - store_wise_ring_breakdown.csv       -> store x ring matrix
  - store_wise_catchment_chart.png      -> visual summary (2 charts)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# CONFIG

CATCHMENT_CSV = "catchment_data_with_rules.csv"
FOOTFALL_CSV = "footfall_summary.csv"

OUTPUT_MASTER_CSV = "store_wise_catchment_analysis.csv"
OUTPUT_RING_CSV = "store_wise_ring_breakdown.csv"
OUTPUT_CHART_PNG = "store_wise_catchment_chart.png"

STORE_NAMES = {
    "STR001": "Store A - Sitabuldi",
    "STR002": "Store B - Civil Lines",
    "STR003": "Store C - Wardha Road",
}
STORE_IDS = list(STORE_NAMES.keys())

RING_ORDER = ["0-1km (Core)", "1-3km (Primary)", "3-5km (Extended)"]


# STEP 1: Load rule-based catchment data

def load_catchment_data(path=CATCHMENT_CSV):
    df = pd.read_csv(path)
    print(f"Loaded {path} - {len(df)} homes")
    return df


# STEP 2: Core store-wise catchment metrics
#   - primary catchment size (homes jinke liye ye store PRIMARY hai,
#     rule ke hisaab se: nearest AND within 5km)
#   - ring-wise split of that primary catchment
#   - overlap: kitne homes is store ke OVERLAP_RADIUS (3km) ke andar
#     aate hai, chahe primary store koi bhi ho (cannibalization risk)

def build_store_metrics(df):
    rows = []

    for store_id in STORE_IDS:
        primary_mask = df["primary_store_id"] == store_id
        primary_homes = df.loc[primary_mask]

        ring_counts = (
            primary_homes["catchment_ring"]
            .value_counts()
            .reindex(RING_ORDER, fill_value=0)
        )

        # is store ke naam OVERLAP list mein kitni baar aaya (comma
        # separated string mein) - ye cannibalization exposure hai
        overlap_mask = df["overlapping_stores"].fillna("").str.split(",").apply(
            lambda stores: store_id in stores
        )
        overlap_homes = int(overlap_mask.sum())

        rows.append({
            "store_id": store_id,
            "store_name": STORE_NAMES[store_id],
            "primary_catchment_homes": int(primary_mask.sum()),
            "core_0_1km": int(ring_counts["0-1km (Core)"]),
            "primary_1_3km": int(ring_counts["1-3km (Primary)"]),
            "extended_3_5km": int(ring_counts["3-5km (Extended)"]),
            "overlap_exposure_homes": overlap_homes,
            "avg_distance_primary_m": round(
                primary_homes["primary_store_distance_m"].mean(), 1
            ) if len(primary_homes) else 0.0,
        })

    metrics_df = pd.DataFrame(rows)

    # overall out-of-catchment stat (global, store-independent)
    out_of_catchment = int(df["is_out_of_catchment"].sum())
    total_homes = len(df)

    return metrics_df, out_of_catchment, total_homes


# STEP 3: Ring x Store matrix (wide format - reporting ke liye achha)

def build_ring_matrix(df):
    primary_df = df[df["primary_store_id"].notna()]
    matrix = (
        primary_df
        .groupby(["primary_store_id", "catchment_ring"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=RING_ORDER, fill_value=0)
        .reindex(STORE_IDS, fill_value=0)
    )
    matrix.index.name = "store_id"
    matrix = matrix.reset_index()
    matrix["store_name"] = matrix["store_id"].map(STORE_NAMES)
    return matrix[["store_id", "store_name"] + RING_ORDER]


# STEP 4: Footfall / conversion metrics jodo
#   conversion_rate = (unique visitors) / (primary catchment homes)
#   -> is store ke catchment mein rehne wale kitne % log actually
#      visit karke aate hai.

def add_footfall_metrics(metrics_df, footfall_path=FOOTFALL_CSV):
    try:
        footfall_df = pd.read_csv(footfall_path)
    except FileNotFoundError:
        print(f"'{footfall_path}' nahi mili - footfall metrics skip.")
        metrics_df["total_visits"] = np.nan
        metrics_df["unique_visitors"] = np.nan
        metrics_df["avg_dwell_minutes"] = np.nan
        metrics_df["conversion_rate_pct"] = np.nan
        return metrics_df

    store_footfall = (
        footfall_df
        .groupby("store_id")
        .agg(
            total_visits=("total_visits", "sum"),
            unique_visitors=("unique_visitors", "sum"),
            avg_dwell_minutes=("avg_dwell_minutes", "mean"),
        )
        .reset_index()
    )

    metrics_df = metrics_df.merge(store_footfall, on="store_id", how="left")
    metrics_df["total_visits"] = metrics_df["total_visits"].fillna(0)
    metrics_df["unique_visitors"] = metrics_df["unique_visitors"].fillna(0)
    metrics_df["avg_dwell_minutes"] = metrics_df["avg_dwell_minutes"].round(1)

    metrics_df["conversion_rate_pct"] = np.where(
        metrics_df["primary_catchment_homes"] > 0,
        round(
            100 * metrics_df["unique_visitors"] / metrics_df["primary_catchment_homes"],
            1,
        ),
        0.0,
    )

    return metrics_df


# STEP 5: Charts - stacked ring breakdown + conversion rate

def plot_charts(metrics_df, out_path=OUTPUT_CHART_PNG):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # --- Chart 1: Stacked ring breakdown per store ---
    ax1 = axes[0]
    labels = metrics_df["store_name"]
    core = metrics_df["core_0_1km"]
    primary = metrics_df["primary_1_3km"]
    extended = metrics_df["extended_3_5km"]

    x = np.arange(len(labels))
    ax1.bar(x, core, label="0-1km (Core)", color="#2E7D32")
    ax1.bar(x, primary, bottom=core, label="1-3km (Primary)", color="#66BB6A")
    ax1.bar(x, extended, bottom=core + primary, label="3-5km (Extended)", color="#C8E6C9")

    for i, total in enumerate(core + primary + extended):
        ax1.text(i, total + 3, str(int(total)), ha="center", fontweight="bold")

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=15, ha="right")
    ax1.set_ylabel("Homes in Primary Catchment")
    ax1.set_title("Store-wise Primary Catchment (Ring Breakdown)")
    ax1.legend()

    # --- Chart 2: Conversion rate ---
    ax2 = axes[1]
    bars = ax2.bar(labels, metrics_df["conversion_rate_pct"], color="#1565C0")
    for bar, val in zip(bars, metrics_df["conversion_rate_pct"]):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + 0.5, f"{val}%",
                  ha="center", fontweight="bold")
    ax2.set_ylabel("Conversion Rate (%)")
    ax2.set_title("Catchment -> Actual Visit Conversion Rate")
    ax2.set_xticks(np.arange(len(labels)))
    ax2.set_xticklabels(labels, rotation=15, ha="right")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print("Saved chart:", out_path)


# MAIN

if __name__ == "__main__":
    df = load_catchment_data()

    metrics_df, out_of_catchment, total_homes = build_store_metrics(df)
    metrics_df = add_footfall_metrics(metrics_df)

    ring_matrix = build_ring_matrix(df)

    metrics_df.to_csv(OUTPUT_MASTER_CSV, index=False)
    ring_matrix.to_csv(OUTPUT_RING_CSV, index=False)
    print("Saved:", OUTPUT_MASTER_CSV)
    print("Saved:", OUTPUT_RING_CSV)

    plot_charts(metrics_df)

    print()
    print("=" * 70)
    print("STORE-WISE CATCHMENT SUMMARY")
    print("=" * 70)
    print(metrics_df.to_string(index=False))

    print()
    print(f"Total homes analyzed: {total_homes}")
    print(f"Out of catchment (>5km from ALL stores): {out_of_catchment} "
          f"({round(100*out_of_catchment/total_homes,1)}%)")

    print()
    print("Key business flags:")
    for _, row in metrics_df.iterrows():
        if row["primary_catchment_homes"] == 0:
            print(f"  - {row['store_name']}: ZERO primary catchment! "
                  f"Isko urgently review karo (location/radius mismatch ho sakta hai).")
        elif row["overlap_exposure_homes"] > row["primary_catchment_homes"] * 0.3:
            print(f"  - {row['store_name']}: High cannibalization risk - "
                  f"{row['overlap_exposure_homes']} homes overlap zone mein hai.")

    print()
    print("Store-wise Catchment Analysis complete!")