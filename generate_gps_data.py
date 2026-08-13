import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import uuid

#Project Configuration

SIMULATION_DATE = datetime(2026, 8, 10)
NUM_DEVICES = 500
PING_INTERVAL_MIN = 3

#Home Location
#Har device ko in Location me se ek Home Location milegi.

HOME_ZONE = {"Wardhaman Nagar": (21.1687, 79.1053),
             "Dharampeth": (21.1394, 79.0640),
             "Sadar": (21.1600, 79.0730)}

#Work / office Locations
#Commuter device in locations par work karne jayenge.

WORK_ZONES = {"MIHAN": (21.0400, 79.0100),
              "IT Park": (21.1200, 79.0500)}

#Store Locations
#Store A aur Store B paas-pass hai.
#Store C comparatively door hai.

STORES = {
    "Store A - Sitabuldi": (21.1500, 79.0800),
    "Store B - Civil Lines": (21.1520, 79.0850),
    "Store C - Wardha Road": (21.1000, 79.0600)
}

#Device Personas
#Ye decide karte hai k kitane devices
#kis type ka daily movement follow karenge.

PERSONA_WEIGHT = {
    "Resident": 0.40,
    "Commuter": 0.40,
    "Shopper": 0.20
}

#Convert meter distance into latitude and longitude change

def meter_to_deg(lat, meters_lat, meters_lon):
    """Convert small distance in meters
    into approximate latitude and longitude changes."""

    #Approximately 1 degree latitude = 111,000 meters
    d_lat = meters_lat / 111000

    #Longitude conversion depends on latitude
    d_lon = meters_lon / (111000 * np.cos(np.radians(lat)))

    return d_lat, d_lon

#add small random GPS error around a Location

def jitter(lat, lon, radius_m=25):
    """Add a small random movement around
    the given latitude and longitude."""

    d_lat, d_lon = meter_to_deg(
        lat,
        np.random.normal(0, radius_m),
        np.random.normal(0, radius_m))

    return lat + d_lat, lon + d_lon

#Create GPS points between two Locations

def interpolate_route(start, end, steps):
    """Create multiple GPS points between
    a starting location and an ending location."""

    lat1, lon1 = start
    lat2, lon2 = end

    route = []

    for i in range(steps):
        #Calculate how far we are between
        #the starting point and ending point.
        fraction = i / max(steps - 1, 1)

        lat = lat1 + (lat2 - lat1) * fraction
        lon = lon1 + (lon2 - lon1) * fraction

        #Add a small random movement
        #to make the route more realistic.
        d_lat, d_lon = meter_to_deg(
            lat,
            np.random.normal(0, 15),
            np.random.normal(0, 15)
        )

        route.append((lat + d_lat, lon + d_lon))

    return route

#Randomly select one Location from a given dictionary

def pick_zone(zone_dict):
    """Randomly choose one location
    from the provided location dict."""

    name = np.random.choice(list(zone_dict.keys()))

    return name, zone_dict[name]

#create one complete daily journey for a device

def build_journey(persona):
    """create the full-day GPS movement
    for one device."""

    journey = []

    #Device ka starting time 7:00 AM se 7:59 AM ke beech hoga.
    current_time = SIMULATION_DATE.replace(
        hour=7,
        minute=np.random.randint(0, 60)
    )

    #Device ke liye randomly ek home location select karo.
    home_name, home_point = pick_zone(HOME_ZONE)

    #Keep the device at one location for some time.
    #Har 3 minute pe ek GPS ping generate hoga jab tak time khatam nahi hota.
    def add_stationary(point, minutes, activity):
        nonlocal current_time

        #Calculate when the device should leave this location.
        end_time = current_time + timedelta(minutes=minutes)

        #Generate one GPS ping every 3 minutes.
        while current_time < end_time:
            #Add a small GPS error to the location.
            lat, lon = jitter(*point, radius_m=15)

            #Save the GPS record as a dictionary
            #(dict isliye kyunki baad me device_id add karna hai).
            journey.append({
                "lat": lat,
                "lon": lon,
                "timestamp": current_time,
                "activity": activity
            })

            #Move the time forward by 3 minutes.
            current_time += timedelta(minutes=PING_INTERVAL_MIN)

    #Device apne home location par subah rukega.
    add_stationary(home_point, np.random.randint(60, 180), "Home")

    #Ab persona ke hisaab se decide karo device kahan jayega.
    #NOTE: PERSONA_WEIGHT ke keys "Resident","Commuter","Shopper" hain
    #(capital letter) isliye yahan bhi same spelling use karo,
    #warna condition kabhi match nahi hogi.

    if persona == "Resident":
        #Resident ek nearby local location visit karega.
        zone_name, zone_point = pick_zone(HOME_ZONE)

        #Home se local location tak ka route.
        route = interpolate_route(home_point, zone_point, 20)
        for lat, lon in route:
            journey.append({
                "lat": lat, "lon": lon,
                "timestamp": current_time,
                "activity": "Local Movement"
            })
            current_time += timedelta(minutes=PING_INTERVAL_MIN)

        #Local location par kuch time rukna.
        add_stationary(zone_point, np.random.randint(30, 90), "Local Activity")

        #Wapas home ka route.
        return_route = interpolate_route(zone_point, home_point, 20)
        for lat, lon in return_route:
            journey.append({
                "lat": lat, "lon": lon,
                "timestamp": current_time,
                "activity": "Return Home"
            })
            current_time += timedelta(minutes=PING_INTERVAL_MIN)

        #Wapas aane ke baad ghar par ruk jayega.
        add_stationary(home_point, np.random.randint(120, 240), "Home")

    elif persona == "Commuter":
        #Commuter office/work zone jayega.
        work_name, work_point = pick_zone(WORK_ZONES)

        #Home se work tak ka route.
        work_route = interpolate_route(home_point, work_point, 60)
        for lat, lon in work_route:
            journey.append({
                "lat": lat, "lon": lon,
                "timestamp": current_time,
                "activity": "Commute to Work"
            })
            current_time += timedelta(minutes=PING_INTERVAL_MIN)

        #Office mein pura din rukna.
        add_stationary(work_point, np.random.randint(300, 420), "Work")

        #Wapas ghar ka route.
        home_route = interpolate_route(work_point, home_point, 60)
        for lat, lon in home_route:
            journey.append({
                "lat": lat, "lon": lon,
                "timestamp": current_time,
                "activity": "Commute to Home"
            })
            current_time += timedelta(minutes=PING_INTERVAL_MIN)

        #Ghar wapas aane ke baad rukna.
        add_stationary(home_point, np.random.randint(120, 240), "Home")

    elif persona == "Shopper":
        #Shopper koi ek store visit karega.
        store_name, store_point = pick_zone(STORES)

        #Home se store tak ka route.
        store_route = interpolate_route(home_point, store_point, 40)
        for lat, lon in store_route:
            journey.append({
                "lat": lat, "lon": lon,
                "timestamp": current_time,
                "activity": "Travel to Store"
            })
            current_time += timedelta(minutes=PING_INTERVAL_MIN)

        #Store mein shopping karna.
        add_stationary(store_point, np.random.randint(30, 90), "Shopping")

        #Wapas ghar ka route.
        return_store_route = interpolate_route(store_point, home_point, 40)
        for lat, lon in return_store_route:
            journey.append({
                "lat": lat, "lon": lon,
                "timestamp": current_time,
                "activity": "Return Home"
            })
            current_time += timedelta(minutes=PING_INTERVAL_MIN)

        #Wapas aane ke baad ghar par rukna.
        add_stationary(home_point, np.random.randint(120, 240), "Home")

    #Poore din ka journey wapas bhejo.
    return journey


#store all GPS records from all devices.
all_records = []

#generate GPS data for each device.
for device_number in range(1, NUM_DEVICES + 1):
    device_id = str(uuid.uuid4())

    #persona randomly choose karo, weight ke hisaab se.
    persona = np.random.choice(
        list(PERSONA_WEIGHT.keys()),
        p=list(PERSONA_WEIGHT.values())
    )

    journey = build_journey(persona)

    #har record mein device_id aur persona add karo.
    for record in journey:
        record["device_id"] = device_id
        record["persona"] = persona

    all_records.extend(journey)

#saare devices ka data collect hone ke baad hi CSV save karo (loop ke bahar).
df = pd.DataFrame(all_records)
df.to_csv("gps_data.csv", index=False)

print("CSV generated successfully!")
print("Total records:", len(all_records))
print("Total devices:", NUM_DEVICES)