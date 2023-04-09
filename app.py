import urllib.request
import urllib.parse
import json
from geopy import distance
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
	return render_template("/index.html")


@app.route("/location", methods=['POST'])
def location():

	user_geolocation = (request.form.get("lat"), request.form.get("long"))

	station_information_url = (
	 "https://gbfs.baywheels.com/gbfs/en/station_information.json")
	station_status_url = "https://gbfs.baywheels.com/gbfs/en/station_status.json"

	station_information_json = urllib.request.urlopen(station_information_url)
	station_status_json = urllib.request.urlopen(station_status_url)

	# contains station_id, name, lat, lon, region_id
	station_information_dict = json.loads(station_information_json.read())

	# contains station_id, last_reported, num_ebikes_available, num_bikes_available, station_status
	station_status_dict = json.loads(station_status_json.read())

	stations_in_sf = []
	free_ebike_stations = []

	for station in station_information_dict["data"]["stations"]:
		if ("region_id" in station and station["region_id"] == "3"
		    and station["station_id"] not in ["74", "361", "572"]):

			stations_in_sf.append(station["station_id"])

	for station in station_status_dict["data"]["stations"]:
		if (station["station_id"] in stations_in_sf
		    and station["station_status"] == "active"
		    and station["station_id"] not in ["74", "361", "572"]
		    and station["num_ebikes_available"] == station["num_bikes_available"]):

			for id in station_information_dict["data"]["stations"]:
				if id["station_id"] == station["station_id"]:

					temp = {}
					temp["name"] = id["name"]
					temp["coords"] = (id["lat"], id["lon"])
					free_ebike_stations.append(temp)

	for station in free_ebike_stations:
		station["distance"] = round(
		 distance.distance(user_geolocation, station["coords"]).miles, 2)

		station[
		 "maps_link"] = f"http://maps.apple.com/?daddr={urllib.parse.quote_plus(station['name'])}&dirflg=w"

	def get_distance(station):
		return station["distance"]

	free_ebike_stations = sorted(free_ebike_stations, key=get_distance)

	free_ebike_stations = free_ebike_stations[0]

	return render_template(
	 "/location.html",
	 free_ebike_stations=free_ebike_stations,
	 user_geolocation=user_geolocation,
	)


app.run(host='0.0.0.0', port=81)
