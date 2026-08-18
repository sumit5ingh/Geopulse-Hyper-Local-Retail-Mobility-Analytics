"""
GeoPulse - Week 2: Data Understanding
Task: GPS dataset aur store dataset ke columns, lat/long, timestamp 
      and data structure document ."""



import pandas as pd

# STEP 0: Apne file paths 

gps_file = "gps_data_final.csv"          # GPS enriched/final data
store_file = "store_catchment_summary.csv"  # Store-level summary data


# STEP 1: Data Load 

gps_data = pd.read_csv(gps_file)
store_data = pd.read_csv(store_file)

print("=" * 60)
print("GPS DATA OVERVIEW")
print("=" * 60)
print("Shape (rows, columns):", gps_data.shape)
print("\nColumn Names:")
print(gps_data.columns.tolist())
print("\nFirst 5 rows:")
print(gps_data.head())
print("\nData types:")
print(gps_data.dtypes)
print("\nMissing values per column:")
print(gps_data.isnull().sum())

print("\n" + "=" * 60)
print("STORE DATA OVERVIEW")
print("=" * 60)
print("Shape (rows, columns):", store_data.shape)
print("\nColumn Names:")
print(store_data.columns.tolist())
print("\nFirst 5 rows:")
print(store_data.head())
print("\nData types:")
print(store_data.dtypes)
print("\nMissing values per column:")
print(store_data.isnull().sum())


# STEP 2: Key columns auto-detect  (lat/long/timestamp/id)

def find_matching_columns(df, keywords):
    """Column names mein diye gaye keywords dhoondta hai (case-insensitive)."""
    matches = []
    for col in df.columns:
        for kw in keywords:
            if kw.lower() in col.lower():
                matches.append(col)
                break
    return matches

print("\n" + "=" * 60)
print("KEY COLUMN DETECTION")
print("=" * 60)

gps_lat_cols = find_matching_columns(gps_data, ["lat"])
gps_lon_cols = find_matching_columns(gps_data, ["lon", "lng"])
gps_time_cols = find_matching_columns(gps_data, ["time", "date", "timestamp"])
gps_id_cols = find_matching_columns(gps_data, ["user", "device", "id"])

store_lat_cols = find_matching_columns(store_data, ["lat"])
store_lon_cols = find_matching_columns(store_data, ["lon", "lng"])
store_id_cols = find_matching_columns(store_data, ["store", "id"])

print("GPS Data -> Latitude columns:", gps_lat_cols)
print("GPS Data -> Longitude columns:", gps_lon_cols)
print("GPS Data -> Timestamp columns:", gps_time_cols)
print("GPS Data -> ID columns:", gps_id_cols)

print("\nStore Data -> Latitude columns:", store_lat_cols)
print("Store Data -> Longitude columns:", store_lon_cols)
print("Store Data -> ID columns:", store_id_cols)


# STEP 3: Documentation file 

with open("data_structure_documentation.txt", "w", encoding="utf-8") as f:
    f.write("GEOPULSE - DATA STRUCTURE DOCUMENTATION\n")
    f.write("Week 2: Catchment Area Analysis - Data Understanding\n")
    f.write("=" * 60 + "\n\n")

    f.write("1. GPS DATASET\n")
    f.write("-" * 40 + "\n")
    f.write(f"File: {gps_file}\n")
    f.write(f"Shape: {gps_data.shape[0]} rows, {gps_data.shape[1]} columns\n")
    f.write(f"Columns: {gps_data.columns.tolist()}\n")
    f.write(f"Detected Latitude column(s): {gps_lat_cols}\n")
    f.write(f"Detected Longitude column(s): {gps_lon_cols}\n")
    f.write(f"Detected Timestamp column(s): {gps_time_cols}\n")
    f.write(f"Detected ID column(s): {gps_id_cols}\n")
    f.write(f"Missing values:\n{gps_data.isnull().sum().to_string()}\n\n")

    f.write("2. STORE DATASET\n")
    f.write("-" * 40 + "\n")
    f.write(f"File: {store_file}\n")
    f.write(f"Shape: {store_data.shape[0]} rows, {store_data.shape[1]} columns\n")
    f.write(f"Columns: {store_data.columns.tolist()}\n")
    f.write(f"Detected Latitude column(s): {store_lat_cols}\n")
    f.write(f"Detected Longitude column(s): {store_lon_cols}\n")
    f.write(f"Detected Store ID column(s): {store_id_cols}\n")
    f.write(f"Missing values:\n{store_data.isnull().sum().to_string()}\n\n")

    f.write("3. NOTES / NEXT STEPS\n")
    f.write("-" * 40 + "\n")
    f.write("- Confirm auto-detected columns are correct (manually verify above).\n")
    f.write("- Next: use lat/long of GPS points + store locations to calculate\n")
    f.write("  Haversine distance for catchment area definition.\n")

print("\n" + "=" * 60)
print("Documentation saved to: data_structure_documentation.txt")
print("=" * 60)


# Naya check - catchment_data.csv 
catchment = pd.read_csv("catchment_data.csv")
print("\n" + "=" * 60)
print("CATCHMENT DATA OVERVIEW")
print("=" * 60)
print(catchment.columns.tolist())
print(catchment.head())