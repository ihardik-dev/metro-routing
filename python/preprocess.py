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
                "route_id": int(row["route_id"])
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
                "departure": row["departure_time"]
            })

    return stop_times


def time_to_seconds(time_string):
    hours, minutes, seconds = map(int, time_string.split(":"))

    return hours * 3600 + minutes * 60 + seconds


def build_graph(stop_times):
    graph = {}

    # Build graph from consecutive stops
    for trip_id, trip_stops in stop_times.items():

        for i in range(len(trip_stops) - 1):

            current = trip_stops[i]
            next_stop = trip_stops[i + 1]

            current_id = current["stop_id"]
            next_id = next_stop["stop_id"]

            departure = time_to_seconds(current["departure"])
            arrival = time_to_seconds(next_stop["arrival"])

            travel_time = arrival - departure

            if current_id not in graph:
                graph[current_id] = {}

            if next_id not in graph[current_id]:
                graph[current_id][next_id] = []

            graph[current_id][next_id].append(travel_time)

    # Average travel times
    for current_id in graph:

        for next_id in graph[current_id]:

            times = graph[current_id][next_id]

            average_time = sum(times) / len(times)

            graph[current_id][next_id] = round(average_time)

    return graph


def find_route(graph, source, target):

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

        if distances[current] == float("inf"):
            break

        for neighbor, travel_time in graph[current].items():

            new_distance = distances[current] + travel_time

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current

    if distances[target] == float("inf"):
        return None

    path = []

    current = target

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    return path, distances[target]


if __name__ == "__main__":

    stops = load_stops()
    stop_times = load_stop_times()

    graph = build_graph(stop_times)

    source = 33
    target = 176

    result = find_route(graph, source, target)

    if result is None:
        print("No route found.")

    else:
        path, travel_time = result

        print("Route:")

        for stop_id in path:
            print(stops[stop_id]["name"])

        print("Travel time:", travel_time, "seconds")