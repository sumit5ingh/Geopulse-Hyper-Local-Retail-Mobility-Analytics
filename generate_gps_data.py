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

HOME_ZONE = {"Wardhaman Nagar": (21.1687,79.1053),
             "Dharampeth":(21.1394, 79.0640),
             "Sadar": (21.1600, 79.0730)}

#Work / office Locations
#Commuter device in locations par work karne jayenge.

WORK_ZONES = {"MIHAN": (21.0400, 79.0100),
              "IT Park": (21.1200,79.0500)}

#Store Locations
#Store A aur Store B paas-pass hai .
#Store C comparatively door hai.

STORES = {
    "Store A - Sitabuldi":(21.1500, 79.0800),
    "Store B - Civil Lines":(21.1520, 79.0850),
    "Store C - Wardha Road":(21.1000, 79.0600)
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
    """ Convert small distance in meters
    into approximate latitude and longitude changes."""

    #Approximately 1 degree lattitude = 111,000 meters
    d_lat = meters_lat / 111000

    #Longitude Conversion depends on latitude
    d_lon = meters_lon / (
        111000 * np.cos(np.radians(lat))
    )

    return d_lat, d_lon

#add small randome GPS error around a Location 

def jitter(lat, lon, radius_m=25):
    """
    Add a small random movement around
    the given latitude and longitude."""

    d_lat, d_lon = meter_to_deg(
        lat,
        np.random.normal(0, radius_m),
        np.random.normal(0, radius_m))

    return lat + d_lat, lon + d_lon

#Create GPS points between two Locations

def interpolate_route(start, end, steps):

    """
    Create multiple Gps point between 
    a starting location and an ending location . """

    lat1, lon1 = start
    lat2, lon2 = end

    route = []

    for i in range(steps):
        #Calculate how far we are between
        #the starting point and ending point.

        fraction = i / max(steps - 1, 1)

        lat = lat1 + (lat2 - lat1)* fraction 
        lon = lon1 + (lon2 - lon1)* fraction

        #Add a small random movement
        #to make the route more realistic.
        d_lat, d_lon = meter_to_deg(
            lat,
            np.random.normal(0, 15),
            np.random.normal(0, 15)
        )

        route.append(
            (lat + d_lat, lon + d_lon)
        )

    return route

#Randomely select one Location from a given dictionary

def pick_zone(zone_dict):
    """
    Randomly choose one location 
    from the provided location .
    """

    name = np.random.choice(
        list(zone_dict.keys())
    )

    return name, zone_dict[name]

#create one complete daily journey for a device

def build_journey(persona):
    """
    create the full-day GPS movement
    for one device."""

    journey = []

    #Device ka starting time 7:00 AM se 7:59 AM ke beech hoga.
    current_time = SIMULATION_DATE.replace(
        hour=7,
        minute=np.random.randint(0, 60)
    )

    #Device ke liye randomly ek home location select karo .
    home_name, home_point = pick_zone(HOME_ZONE)

    # Keep the device at one location for some time.
    def add_stationary(point, minutes, activity):

        nonlocal current_time

        # Calculate when the device should leave this location.
        end_time = current_time + timedelta(
            minutes=minutes
        )

        # Generate one GPS ping every 3 minutes.
        while current_time < end_time:

            # Add a small GPS error to the location.
            lat, lon = jitter(
                *point,
                radius_m=15
            )

            # Save the GPS record in our journey list.
            journey.append(
                (
                    lat,
                    lon,
                    current_time,
                    activity
                )
            )

            # Move the time forward by 3 minutes.
            current_time += timedelta(
                minutes=PING_INTERVAL_MIN
            )

