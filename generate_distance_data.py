"""
GeoPulse - Day 3: Distance Calculation
Task: Haversine formula use karke har GPS point/home se
      har store tak ki distance calculate karna, aur ek
      distance table banake save karna.
"""

import pandas as pd
from math import radians, sin, cos, sqrt, atan2


# STEP 1: Haversine Distance Function

# 2 GPS points (lat, lon) ke beech ki distance meters mein
# nikalta hai - Earth ki curved surface ko account karte hue
# (seedha Euclidean/Pythagoras formula galat hoga, kyunki
# lat/lon flat plane pe nahi, sphere pe hai).

def haversine_distance(lat1, lon1, lat2, lon2):
    """2 GPS points ke beech great-circle distance meters mein."""
    R = 6371000  # Earth ka average radius, meters mein

    # Step A: degrees ko radians mein convert karo (math functions
    # radians expect karte hai, degrees nahi).
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)      # latitude ka difference
    d_lambda = radians(lon2 - lon1)   # longitude ka difference

    # Step B: Haversine formula
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Step C: radius se multiply karke actual distance milta hai
    return R * c


# STEP 2: Store Catalog (same as Day 4/5 scripts - consistent
# rakhna zaroori hai warna store_id mismatch ho jayega)


STORE_CATALOG = [
    {"store_id": "STR001", "store_name": "Store A - Sitabuldi", "lat": 21.1500, "lon": 79.0800},
    {"store_id": "STR002", "store_name": "Store B - Civil Lines", "lat": 21.1520, "lon": 79.0850},
    {"store_id": "STR003", "store_name": "Store C - Wardha Road", "lat": 21.1000, "lon": 79.0600},
]


# STEP 3: Har device ka home location nikaalo

# gps_data_final.csv mein raw home point save nahi hai, sirf
# "Home" activity wale (jittered) pings hai. Unka average lekar
# asli home location ke kaafi paas pahunch jaate hai.

def get_home_locations(df):
    """Har device ke 'Home' activity wale pings ka average
    lat/lon nikaal kar home location table banata hai."""

    home_df = df[df["activity"] == "Home"]

    home_locations = (
        home_df.groupby("device_id")
        .agg(
            home_lat=("lat", "mean"),
            home_lon=("lon", "mean"),
            persona=("persona", "first"),
        )
        .reset_index()
    )

    return home_locations

# STEP 4: Har home se har store tak ki distance nikaalo


def build_distance_table(home_locations, store_catalog):
    """Har home ke liye, har store se Haversine distance
    nikaal kar ek wide-format distance table banata hai."""

    rows = []

    for _, home in home_locations.iterrows():

        row = {
            "device_id": home["device_id"],
            "persona": home["persona"],
            "home_lat": round(home["home_lat"], 6),
            "home_lon": round(home["home_lon"], 6),
        }

        distances = {}
        for store in store_catalog:
            dist_m = haversine_distance(
                home["home_lat"], home["home_lon"],
                store["lat"], store["lon"]
            )
            distances[store["store_id"]] = dist_m

            # Har store ki distance apna column banati hai
            col_name = f"dist_to_{store['store_id']}_m"
            row[col_name] = round(dist_m, 1)

        # Sabse paas wala store bhi nikaal do (quick reference ke liye)
        nearest_store_id = min(distances, key=distances.get)
        nearest_store = next(
            s for s in store_catalog if s["store_id"] == nearest_store_id
        )
        row["nearest_store_id"] = nearest_store_id
        row["nearest_store_name"] = nearest_store["store_name"]
        row["distance_to_nearest_store_m"] = round(distances[nearest_store_id], 1)

        rows.append(row)

    return pd.DataFrame(rows)


# MAIN


if __name__ == "__main__":

    INPUT_CSV = "gps_data_final.csv"

    print("Reading:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

    print("Extracting home locations from 'Home' activity pings...")
    home_locations = get_home_locations(df)
    print("Total unique devices (homes):", len(home_locations))

    print("Calculating Haversine distance from each home to each store...")
    distance_df = build_distance_table(home_locations, STORE_CATALOG)

    distance_df.to_csv("distance_data.csv", index=False)
    print("Saved: distance_data.csv -", len(distance_df), "rows")

    # ------------------------------------------------------------
    # Quick sanity check - pehle 5 rows aur basic stats print karo
    # ------------------------------------------------------------
    print()
    print("Sample rows:")
    print(distance_df.head())

    print()
    print("Distance to nearest store - summary stats (meters):")
    print(distance_df["distance_to_nearest_store_m"].describe())

    print()
    print("Day 3 - Distance calculation complete!")