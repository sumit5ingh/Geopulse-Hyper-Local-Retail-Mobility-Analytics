import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2


#Haversine distance - 2 GPS points ke beech
#distance meters mein nikalta hai.

def haversine_distance(lat1, lon1, lat2, lon2):
    """2 GPS points ke beech distance meters mein."""
    R = 6371000  # Earth ka radius meters mein

    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


#STORE CATALOG - Part 1/2 wale STORES dict aur Day 4
#wale STORE_CATALOG se match karke banaya hai.

STORE_CATALOG = [
    {"store_id": "STR001", "store_name": "Store A - Sitabuldi", "category": "Supermarket", "lat": 21.1500, "lon": 79.0800},
    {"store_id": "STR002", "store_name": "Store B - Civil Lines", "category": "Mall", "lat": 21.1520, "lon": 79.0850},
    {"store_id": "STR003", "store_name": "Store C - Wardha Road", "category": "Hypermarket", "lat": 21.1000, "lon": 79.0600},
]

#Catchment rings - kitni distance pe kaunsa ring aata hai.

#near catchment sabse zyada convert hota hai, far catchment kam.

CATCHMENT_RINGS = [
    (0, 1000, "0-1km"),
    (1000, 3000, "1-3km"),
    (3000, 5000, "3-5km"),
    (5000, float("inf"), "5km+"),
]

#Kis distance tak "overlap" maana jaye - yaani agar do stores
#dono is radius ke andar hai to wo home dono ke catchment mein hai.

OVERLAP_RADIUS_M = 3000


#STEP 1: Har device ka home location reconstruct karo.
#gps_data_final.csv mein raw home coordinate save nahi hai,
#sirf "Home" activity wale jittered pings hai. Unka average
#lekar asli home point ke kaafi paas pahunch jaate hai
#(jitter random hai, isliye average karne se cancel ho jaata hai).

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


#STEP 2: Distance ko catchment ring label mein convert karo.

def classify_ring(distance_m):
    """Given distance meters mein, kaunsa catchment ring
    (0-1km, 1-3km, etc.) usme aata hai wo return karta hai."""

    for low, high, label in CATCHMENT_RINGS:
        if low <= distance_m < high:
            return label

    return "5km+"


#STEP 3: Har home ke liye har store se distance nikalo,

def build_catchment_data(home_locations, store_catalog):
   
    rows = []

    for _, home in home_locations.iterrows():

        #Is home se har store tak ki distance nikalo.
        distances = {}
        for store in store_catalog:
            dist = haversine_distance(
                home["home_lat"], home["home_lon"],
                store["lat"], store["lon"]
            )
            distances[store["store_id"]] = dist

        #Sabse paas wala store dhoondo.
        nearest_store_id = min(distances, key=distances.get)
        nearest_store = next(
            s for s in store_catalog if s["store_id"] == nearest_store_id
        )
        nearest_dist = distances[nearest_store_id]

        row = {
            "device_id": home["device_id"],
            "persona": home["persona"],
            "home_lat": round(home["home_lat"], 6),
            "home_lon": round(home["home_lon"], 6),
            "nearest_store_id": nearest_store_id,
            "nearest_store_name": nearest_store["store_name"],
            "distance_to_nearest_store_m": round(nearest_dist, 1),
            "catchment_ring": classify_ring(nearest_dist),
        }

        overlapping_stores = []
        for store in store_catalog:
            col_name = f"dist_to_{store['store_id']}_m"
            dist = distances[store["store_id"]]
            row[col_name] = round(dist, 1)

            if dist <= OVERLAP_RADIUS_M:
                overlapping_stores.append(store["store_id"])

        #Kitne stores ke catchment mein ye home simultaneously aata hai.
        #Store A aur B paas-paas hai, isliye unke beech overlap
        #expected hai - ye cannibalization risk dikhata hai.
        row["catchment_overlap_count"] = len(overlapping_stores)
        row["overlapping_stores"] = ",".join(overlapping_stores)

        rows.append(row)

    return pd.DataFrame(rows)


#STEP 4: Store-level summary - har store ke har ring mein
#kitne unique homes/devices aate hai.

def build_store_catchment_summary(catchment_df, store_catalog):
    """Store aur catchment ring ke hisaab se kitne homes
    hai, uska summary table banata hai."""

    summary_rows = []

    for store in store_catalog:
        col = f"dist_to_{store['store_id']}_m"

        for low, high, label in CATCHMENT_RINGS:
            mask = (catchment_df[col] >= low) & (catchment_df[col] < high)
            devices_in_ring = catchment_df.loc[mask, "device_id"].nunique()

            summary_rows.append({
                "store_id": store["store_id"],
                "store_name": store["store_name"],
                "catchment_ring": label,
                "homes_in_ring": devices_in_ring,
            })

    return pd.DataFrame(summary_rows)




def add_conversion_metrics(catchment_df, visits_csv="store_visits.csv"):
    """store_visits.csv se check karta hai ki catchment
    table mein har device ne kabhi koi store visit kiya
    ya nahi."""

    try:
        visits_df = pd.read_csv(visits_csv)
    except FileNotFoundError:
        print(f"'{visits_csv}' nahi mili - conversion metrics skip kar rahe hai.")
        catchment_df["visited_any_store"] = np.nan
        return catchment_df

    visited_devices = set(visits_df["device_id"].unique())
    catchment_df["visited_any_store"] = catchment_df["device_id"].isin(visited_devices)

    return catchment_df


if __name__ == "__main__":

    INPUT_CSV = "gps_data_final.csv"

    print("Reading:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

    print("Extracting home locations from 'Home' activity pings...")
    home_locations = get_home_locations(df)
    print("Total unique devices (homes):", len(home_locations))

    print("Building catchment data (distance + ring + overlap)...")
    catchment_df = build_catchment_data(home_locations, STORE_CATALOG)

    print("Adding conversion metrics (agar store_visits.csv available hai)...")
    catchment_df = add_conversion_metrics(catchment_df)

    catchment_df.to_csv("catchment_data.csv", index=False)
    print("Saved: catchment_data.csv -", len(catchment_df), "rows")

    print("Building store-level catchment summary...")
    store_summary_df = build_store_catchment_summary(catchment_df, STORE_CATALOG)
    store_summary_df.to_csv("store_catchment_summary.csv", index=False)
    print("Saved: store_catchment_summary.csv -", len(store_summary_df), "rows")

    #Quick sanity check - overlap count distribution print kar do.
    print()
    print("Catchment overlap distribution:")
    print(catchment_df["catchment_overlap_count"].value_counts().sort_index())

    print()
    print("Day 5 - Catchment/spatial data generation complete!")