import urllib.request
import urllib.parse
import json
import geocoder
from geopy import distance

station_information_url = "https://gbfs.baywheels.com/gbfs/en/station_information.json"
station_status_url = "https://gbfs.baywheels.com/gbfs/en/station_status.json"

station_information_json = urllib.request.urlopen(station_information_url)
station_status_json = urllib.request.urlopen(station_status_url)

station_information_dict = json.loads(
    station_information_json.read()
)  # contains station_id, name, lat, lon, region_id
station_status_dict = json.loads(
    station_status_json.read()
)  # contains station_id, last_reported, num_ebikes_available, num_bikes_available, station_status

STATIONS_IN_SF = []
FREE_EBIKE_STATIONS = []


for station in station_information_dict["data"]["stations"]:
    if (
        "region_id" in station
        and station["region_id"] == "3"
        and station["station_id"] not in ["74", "361", "572"]
    ):
        STATIONS_IN_SF.append(station["station_id"])


for station in station_status_dict["data"]["stations"]:
    if (
        station["station_id"] in STATIONS_IN_SF
        and station["station_status"] == "active"
        and station["station_id"] not in ["74", "361", "572"]
        and station["num_ebikes_available"] == station["num_bikes_available"]
    ):
        for id in station_information_dict["data"]["stations"]:
            if id["station_id"] == station["station_id"]:
                temp = {}
                temp["name"] = id["name"]
                temp["coords"] = str(id["lat"]) + ", " + str(id["lon"])
                FREE_EBIKE_STATIONS.append(temp)


user_geolocation = (geocoder.ip("me")).latlng


for station in FREE_EBIKE_STATIONS:
    station["distance"] = distance.distance(user_geolocation, station["coords"]).miles

    station[
        "maps_link"
    ] = f"http://maps.apple.com/?daddr={urllib.parse.quote_plus(station['name'])}&dirflg=w"
    print(station, "\n")
