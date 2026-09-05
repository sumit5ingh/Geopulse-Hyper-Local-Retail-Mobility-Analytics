"""
GeoPulse - Store Catchment Area Analysis
CATCHMENT RULE MODULE
==============================================================
Ye module define karta hai ki kaunse business rules follow karke
har home ko store ke catchment area mein assign kiya jata hai.

Ye jaan-boojh kar generate_catchment_data.py se ALAG rakha gaya hai:
  - generate_catchment_data.py -> simulated GPS data se distances banata hai
  - catchment_rules.py (ye file) -> sirf RULE define karta hai, kisi bhi
    distance table (real ya simulated) pe apply ho sakta hai

Isse rule ko team review/tune kar sakti hai bina data-generation
code touch kiye.
"""

import pandas as pd



# RULE 1: PRIMARY CATCHMENT RADIUS

# Agar nearest store bhi is radius se door hai, to home ko
# "Out of Catchment" maana jata hai - koi store realistically
# use serve nahi kar raha. (Pehle wale code mein ye rule missing
# tha - har home ko forcefully nearest store assign ho jaata tha,
# chahe wo 9km door kyun na ho.)
PRIMARY_CATCHMENT_RADIUS_M = 5000


# RULE 2: CATCHMENT RINGS
# 
# Distance-based segmentation - reporting/visualization ke liye.
# "Core" customers zyada convert karte hai, "Extended" kam.
CATCHMENT_RINGS = [
    (0,    1000,          "0-1km (Core)"),
    (1000, 3000,           "1-3km (Primary)"),
    (3000, 5000,           "3-5km (Extended)"),
    (5000, float("inf"),   "5km+ (Out of Range)"),
]


# RULE 3: OVERLAP / CANNIBALIZATION RADIUS

# Agar 2+ stores is radius ke andar hai, to home dono ke
# "competing catchment" mein maana jata hai - cannibalization risk.
OVERLAP_RADIUS_M = 3000


# RULE FUNCTIONS


def classify_ring(distance_m):
    """Distance (meters) ko catchment ring label mein convert karta hai."""
    for low, high, label in CATCHMENT_RINGS:
        if low <= distance_m < high:
            return label
    return CATCHMENT_RINGS[-1][2]


def assign_primary_store(distances: dict):
    """
    Har home ke liye primary store assign karta hai.

    RULE: Sabse nearest store primary hai, LEKIN sirf tab jab wo
    PRIMARY_CATCHMENT_RADIUS_M ke andar ho. Warna None (out of catchment).
    """
    nearest_store_id = min(distances, key=distances.get)
    nearest_dist = distances[nearest_store_id]

    if nearest_dist <= PRIMARY_CATCHMENT_RADIUS_M:
        return nearest_store_id, nearest_dist
    return None, nearest_dist


def get_overlapping_stores(distances: dict, radius_m=OVERLAP_RADIUS_M):
    """RULE: OVERLAP_RADIUS_M ke andar aane wale saare stores return karta hai."""
    return [store_id for store_id, d in distances.items() if d <= radius_m]


def apply_catchment_rules(distance_df: pd.DataFrame, store_ids: list) -> pd.DataFrame:
    """
    Poore distance_df (jisme har store ke liye dist_to_<store_id>_m
    column ho) pe upar wale saare rules apply karta hai.

    Naye columns add karta hai:
      - primary_store_id            (None agar out of catchment)
      - primary_store_distance_m
      - catchment_ring
      - overlapping_stores          (comma-separated)
      - catchment_overlap_count
      - is_out_of_catchment         (True/False)
    """
    primary_ids, primary_dists = [], []
    rings, overlaps, overlap_counts, out_flags = [], [], [], []

    for _, row in distance_df.iterrows():
        distances = {sid: row[f"dist_to_{sid}_m"] for sid in store_ids}

        primary_id, primary_dist = assign_primary_store(distances)
        overlap_list = get_overlapping_stores(distances)

        primary_ids.append(primary_id)
        primary_dists.append(round(primary_dist, 1))
        rings.append(classify_ring(primary_dist))
        overlaps.append(",".join(overlap_list))
        overlap_counts.append(len(overlap_list))
        out_flags.append(primary_id is None)

    distance_df["primary_store_id"] = primary_ids
    distance_df["primary_store_distance_m"] = primary_dists
    distance_df["catchment_ring"] = rings
    distance_df["overlapping_stores"] = overlaps
    distance_df["catchment_overlap_count"] = overlap_counts
    distance_df["is_out_of_catchment"] = out_flags

    return distance_df


def build_store_catchment_summary(catchment_df: pd.DataFrame, store_ids: list,
                                   store_names: dict) -> pd.DataFrame:
    """Har store ke har ring mein kitne homes hai, uska summary table."""
    summary_rows = []

    for store_id in store_ids:
        col = f"dist_to_{store_id}_m"
        for low, high, label in CATCHMENT_RINGS:
            mask = (catchment_df[col] >= low) & (catchment_df[col] < high)
            homes_in_ring = catchment_df.loc[mask, "device_id"].nunique()
            summary_rows.append({
                "store_id": store_id,
                "store_name": store_names.get(store_id, store_id),
                "catchment_ring": label,
                "homes_in_ring": homes_in_ring,
            })

    return pd.DataFrame(summary_rows)



# MAIN - existing distance_data.csv pe rules apply karo


if __name__ == "__main__":
    INPUT_CSV = "distance_data.csv"
    OUTPUT_CSV = "catchment_data_with_rules.csv"
    SUMMARY_CSV = "store_catchment_summary_with_rules.csv"

    STORE_IDS = ["STR001", "STR002", "STR003"]
    STORE_NAMES = {
        "STR001": "Store A - Sitabuldi",
        "STR002": "Store B - Civil Lines",
        "STR003": "Store C - Wardha Road",
    }

    print("Reading:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

    print("Applying catchment rules...")
    df = apply_catchment_rules(df, STORE_IDS)
    df.to_csv(OUTPUT_CSV, index=False)
    print("Saved:", OUTPUT_CSV, "-", len(df), "rows")

    print()
    print("Primary store distribution (None = out of catchment):")
    print(df["primary_store_id"].value_counts(dropna=False))

    print()
    print("Catchment ring distribution:")
    print(df["catchment_ring"].value_counts())

    print()
    print("Homes out of catchment:", df["is_out_of_catchment"].sum(), "/", len(df))

    print()
    print("Overlap count distribution (cannibalization risk):")
    print(df["catchment_overlap_count"].value_counts().sort_index())

    print()
    print("Building store-level catchment summary...")
    summary_df = build_store_catchment_summary(df, STORE_IDS, STORE_NAMES)
    summary_df.to_csv(SUMMARY_CSV, index=False)
    print("Saved:", SUMMARY_CSV)
    print(summary_df)

    print()
    print("Catchment Rule task complete!")