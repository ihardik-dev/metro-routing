import csv

STOPS_FILE = "data/raw/gtfs/stops.txt"
ROUTES_FILE = "data/raw/gtfs/routes.txt"
TRIPS_FILE = "data/raw/gtfs/trips.txt"

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

if __name__ == "__main__":
    stops = load_stops()
    routes = load_routes()
    trips = load_trips()

    print(f"Total stations: {len(stops)}")
    print(f"Total routes: {len(routes)}")
    print(f"Total trips: {len(trips)}")

    print(trips[0])