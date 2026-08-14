import numpy as np
import pandas as pd
import uuid
from math import radians, sin , cos, sqrt, atan2

from generate_gps_data import(HOME_ZONE, WORK_ZONES,STORES, 
                              PERSONA_WEIGHT,
                              NUM_DEVICES,pick_zone,build_journey)
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between
    two gps coordianates."""

    R = 6371000 #Earth ka radius meter mein

    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

#device metadata generation and create os and GPS accuracy.

DEVICE_OS_WEIGHT = {"Android": 0.65,
                    "ios": 0.35}

def generate_device_metadata():
    """Randomly generate device-level metadata 
jo pure din same rahega us device keliye"""

    device_os = np.random.choice(
        list(DEVICE_OS_WEIGHT.keys()),
             p=list(DEVICE_OS_WEIGHT.values()))
    #GPS accuracy device/OS ka vary the accuracy point.

    gps_accuracy_m = round(np.random.uniform(3, 12), 1)

    return device_os, gps_accuracy_m

#now creating final dataset.

def enrich_and_build_dataset(all_records, home_points_by_device):
    """taking all recording list (lat, lon, timestamp,
    activity, device_id, persona ) and create extra metadata column
    added and return final list"""

    #every device need to sequence counter.

    sequence_counter = {}

    for record in all_records:
        device_id = record["device_id"]

        if device_id not in sequence_counter:
            sequence_counter[device_id] = 0

        #unique ping ID -every row having own id.

        record["ping_id"] = str(uuid.uuid4())

        #is device ke andar ye kitni number ki ping hai.

        record["sequence_no"] = sequence_counter[device_id]
        sequence_counter[device_id] +=1

        #Timestam se sate aur day_od_week nikal lo.
        ts = record["timestamp"]
        record["date"] = ts.date()
        record["day_of_week"] = ts.strftime("%A")

        #Home se distance nikalna (meters mein).
        home_lat, home_lon = home_points_by_device[device_id]
        record["distance_from_home_m"] = round(
            haversine_distance(home_lat, home_lon, record["lat"],
                               record["lon"]),1
        )
    return all_records
#main loop - generate all datadevicec

all_records = []
home_points_by_device = {}

for device_number in range(1, NUM_DEVICES + 1):
    device_id = str(uuid.uuid4())

    #persona randomly choose karo, weigt ke hisaab se.

    persona = np.random.choice(list(PERSONA_WEIGHT.keys()),
                               p=list(PERSONA_WEIGHT.values()))

    #device ka home point yaad rakhna hai baad me 
    #distance_from_home nikalne ke liye .

    home_name, home_point = pick_zone(HOME_ZONE)
    home_points_by_device[device_id] = home_point
 
    #device-level metadata (OS, accuracy)
    device_os, gps_accuracy_m = generate_device_metadata()
 
    journey = build_journey(persona)
 
    #har record mein device_id, persona, device metadata add karo.
    for record in journey:
        record["device_id"] = device_id
        record["persona"] = persona
        record["device_os"] = device_os
        record["gps_accuracy_m"] = gps_accuracy_m
 
    all_records.extend(journey)
 
#Ab metadata enrich karo (ping_id, sequence_no, date, distance_from_home)
all_records = enrich_and_build_dataset(all_records, home_points_by_device)
 
#Final DataFrame banake CSV save karo.
df = pd.DataFrame(all_records)
df.to_csv("gps_data_final.csv", index=False)
 
print("Final dataset generated successfully!")
print("Total records:", len(all_records))
print("Total devices:", NUM_DEVICES)
print("Columns:", list(df.columns))
 
             
    