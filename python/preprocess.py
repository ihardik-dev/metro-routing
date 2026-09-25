import csv

STOPS_FILE = "data/raw/gtfs/stops.txt"
ROUTES_FILE = "data/raw/gtfs/routes.txt"
TRIPS_FILE = "data/raw/gtfs/trips.txt"
STOP_TIMES_FILE = "data/raw/gtfs/stop_times.txt"


def load_stops():
    stops = {}

    with open(STOPS_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            stop_id = int(row["stop_id"])

            stops[stop_id] = {
                "name": row["stop_name"],
                "lat": float(row["stop_lat"]),
                "lon": float(row["stop_lon"])
            }

    return stops


def load_routes():
    routes = {}

    with open(ROUTES_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            route_id = int(row["route_id"])

            routes[route_id] = {
                "short_name": row["route_short_name"],
                "long_name": row["route_long_name"]
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


def find_route(source, target):

    distances = {}
    previous = {}

    for stop_id in graph:
        distances[stop_id] = float("inf")
        previous[stop_id] = None

    distances[source] = 0

    unvisited = set(graph.keys())

    while unvisited:

        current = min(
            unvisited,
            key=lambda station: distances[station]
        )

        unvisited.remove(current)

        # No more reachable stations
        if distances[current] == float("inf"):
            break

        for neighbor, travel_time in graph[current].items():

            new_distance = distances[current] + travel_time

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current

    # Destination unreachable
    if distances[target] == float("inf"):
        return None

    # Reconstruct route
    path = []

    current = target

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    return path, distances[target]

