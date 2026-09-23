import csv

STOPS_FILE = "data/raw/gtfs/stops.txt"
ROUTES_FILE = "data/raw/gtfs/routes.txt"
TRIPS_FILE = "data/raw/gtfs/trips.txt"
STOP_TIMES_FILE = "data/raw/gtfs/stop_times.txt"

def load_stops():
    stops ={}

    with open(STOPS_FILE,newline = "" , encoding = "utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            stop_id = int(row["stop_id"])

            stops[stop_id] = {
                "name" : row["stop_name"],
                "lat" : float(row["stop_lat"]),
                "lon" : float(row["stop_lon"])
            }

    return stops


def load_routes():
    routes = {}

    with open(ROUTES_FILE,newline ="", encoding = "utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            route_id = int(row["route_id"])

            routes[route_id] = {
                "short_name" : row["route_short_name"],
                "long_name" : row["route_long_name"]
            }

    return routes


def load_trips():
    trips = {}

    with open(TRIPS_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            trip_id = int(row["trip_id"])

            trips[trip_id] = {
                "route_id": int(row["route_id"]),
            }

    return trips


def load_stop_times():
    stop_times = {}

    with open(STOP_TIMES_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            trip_id = int(row["trip_id"])

            if trip_id not in stop_times:
                stop_times[trip_id] = []

            stop_times[trip_id].append({
                "stop_id": int(row["stop_id"]),
                "sequence": int(row["stop_sequence"]),
                "arrival": row["arrival_time"],
                "departure": row["departure_time"],
            })

    return stop_times    


def time_to_seconds(time_string):
    hours, minutes, seconds = map(int, time_string.split(":"))

    return hours * 3600 + minutes * 60 + seconds


if __name__ == "__main__":
    stops = load_stops()
    routes = load_routes()
    trips = load_trips()
    stop_times = load_stop_times()

    for i in range(len(stop_times[0]) - 1):
        current = stop_times[0][i]
        next_stop = stop_times[0][i + 1]

        current_station = stops[current["stop_id"]]["name"]
        next_station = stops[next_stop["stop_id"]]["name"]

        departure = time_to_seconds(current["departure"])
        arrival = time_to_seconds(next_stop["arrival"])

        travel_time = arrival - departure

        print(current_station, "->", next_station, travel_time, "sec")

