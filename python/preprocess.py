import csv
from transfers import add_transfers

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

            short_name = row["route_short_name"]

            line = short_name.split("_")[0]

            routes[route_id] = {
                "short_name": short_name,
                "long_name": row["route_long_name"],
                "line": line
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


def build_graph(stop_times, trips, routes):
    graph = {}

    for trip_id, trip_stops in stop_times.items():

        trip_stops.sort(key=lambda stop: stop["sequence"])

        route_id = trips[trip_id]["route_id"]
        line = routes[route_id]["line"]

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
                graph[current_id][next_id] = {}

            if line not in graph[current_id][next_id]:
                graph[current_id][next_id][line] = []

            graph[current_id][next_id][line].append(travel_time)

    # Average travel times
    for current_id in graph:

        for next_id in graph[current_id]:

            for line in graph[current_id][next_id]:

                times = graph[current_id][next_id][line]

                average_time = sum(times) / len(times)

                graph[current_id][next_id][line] = round(average_time)

    return graph


def find_route(graph, source, target):

    distances = {}
    previous = {}

    # State = (station, current line)
    for station in graph:
        distances[station] = {}

    distances[source]["START"] = 0

    unvisited = [(source, "START")]

    while unvisited:

        current_station, current_line = min(
            unvisited,
            key=lambda state: distances[state[0]][state[1]]
        )

        unvisited.remove((current_station, current_line))

        current_distance = distances[current_station][current_line]

        if current_station == target:
            break

        for neighbor, route_data in graph[current_station].items():

            for edge_line, travel_time in route_data.items():

                new_distance = current_distance + travel_time

                # Manual transfer
                if edge_line.startswith("TRANSFER:"):

                    # Extract destination line
                    new_line = edge_line.split(":")[1]

                else:

                    new_line = edge_line

                    # Normal metro line change
                    if (
                        current_line != "START"
                        and new_line != current_line
                    ):
                        new_distance += 5 * 60

                if (
                    new_line not in distances[neighbor]
                    or new_distance < distances[neighbor][new_line]
                ):
                    distances[neighbor][new_line] = new_distance

                    previous[(neighbor, new_line)] = (
                        current_station,
                        current_line,
                        edge_line
                    )

                    if (neighbor, new_line) not in unvisited:
                        unvisited.append((neighbor, new_line))

    # No route
    if not distances[target]:
        return None

    target_line = min(
        distances[target],
        key=distances[target].get
    )

    travel_time = distances[target][target_line]

    # Reconstruct route
    path = []

    current_state = (target, target_line)

    while current_state[0] != source:

        station, line = current_state

        previous_station, previous_line, edge_line = previous[current_state]

        path.append({
            "station": station,
            "line": line,
            "edge": edge_line
        })

        current_state = (previous_station, previous_line)

    path.append({
        "station": source,
        "line": "START",
        "edge": "START"
    })

    path.reverse()

    # Count actual manual transfers
    transfers = 0

    for step in path:

        if step["edge"].startswith("TRANSFER:"):
            transfers += 1

    return path, travel_time, transfers


def find_route_fewest_stations(graph, source, target):
    distances = {}
    previous = {}

    # State = (station, current line)
    for station in graph:
        distances[station] = {}

    distances[source]["START"] = 0
    unvisited = [(source, "START")]

    while unvisited:
        current_station, current_line = min(
            unvisited,
            key=lambda state: distances[state[0]][state[1]]
        )
        unvisited.remove((current_station, current_line))

        current_distance = distances[current_station][current_line]

        if current_station == target:
            break

        for neighbor, route_data in graph[current_station].items():
            for edge_line in route_data:

                if edge_line.startswith("TRANSFER:"):
                    new_line = edge_line.split(":")[1]
                    station_cost = 1
                else:
                    new_line = edge_line
                    station_cost = 1

                new_distance = current_distance + station_cost

                if (
                    new_line not in distances[neighbor]
                    or new_distance < distances[neighbor][new_line]
                ):
                    distances[neighbor][new_line] = new_distance
                    previous[(neighbor, new_line)] = (
                        current_station,
                        current_line,
                        edge_line
                    )

                    if (neighbor, new_line) not in unvisited:
                        unvisited.append((neighbor, new_line))

    if not distances[target]:
        return None

    target_line = min(
        distances[target],
        key=distances[target].get
    )

    station_count = distances[target][target_line]

    # Reconstruct route
    path = []
    current_state = (target, target_line)

    while current_state[0] != source:
        station, line = current_state

        previous_station, previous_line, edge_line = previous[current_state]

        path.append({
            "station": station,
            "line": line,
            "edge": edge_line
        })

        current_state = (previous_station, previous_line)

    path.append({
        "station": source,
        "line": "START",
        "edge": "START"
    })

    path.reverse()

    transfers = sum(
        1 for step in path
        if step["edge"].startswith("TRANSFER:")
    )

    return path, station_count, transfers


def find_route_fewest_transfers(graph, source, target):
    distances = {}
    previous = {}

    for station in graph:
        distances[station] = {}

    distances[source]["START"] = 0
    unvisited = [(source, "START")]

    while unvisited:
        current_station, current_line = min(
            unvisited,
            key=lambda state: distances[state[0]][state[1]]
        )

        unvisited.remove((current_station, current_line))

        current_distance = distances[current_station][current_line]

        if current_station == target:
            break

        for neighbor, route_data in graph[current_station].items():
            for edge_line, travel_time in route_data.items():

                if edge_line.startswith("TRANSFER:"):
                    new_line = edge_line.split(":")[1]
                    transfer_cost = 1
                else:
                    new_line = edge_line

                    if (
                        current_line != "START"
                        and new_line != current_line
                    ):
                        transfer_cost = 1
                    else:
                        transfer_cost = 0

                new_distance = current_distance + transfer_cost

                if (
                    new_line not in distances[neighbor]
                    or new_distance < distances[neighbor][new_line]
                ):
                    distances[neighbor][new_line] = new_distance

                    previous[(neighbor, new_line)] = (
                        current_station,
                        current_line,
                        edge_line
                    )

                    if (neighbor, new_line) not in unvisited:
                        unvisited.append((neighbor, new_line))

    if not distances[target]:
        return None

    target_line = min(
        distances[target],
        key=distances[target].get
    )

    transfer_count = distances[target][target_line]

    # Reconstruct route
    path = []
    current_state = (target, target_line)

    while current_state[0] != source:
        station, line = current_state

        previous_station, previous_line, edge_line = previous[current_state]

        path.append({
            "station": station,
            "line": line,
            "edge": edge_line
        })

        current_state = (previous_station, previous_line)

    path.append({
        "station": source,
        "line": "START",
        "edge": "START"
    })

    path.reverse()

    return path, transfer_count, transfer_count


def print_route(result, mode):
    if result is None:
        print("No route found.")
        return

    path, cost, transfers = result

    print(f"\n{mode} route:")
    print("-" * 30)

    for step in path:
        station_name = stops[step["station"]]["name"]

        if step["edge"] == "START":
            print(station_name)
        elif step["edge"].startswith("TRANSFER:"):
            print(f"{station_name} [TRANSFER]")
        else:
            print(f"{station_name} [{step['line']}]")

    if mode == "Fastest":
        print("Travel time:", cost, "seconds")
    elif mode == "Fewest stations":
        print("Stations:", cost)

    print("Transfers:", transfers)

if __name__ == "__main__":
    stops = load_stops()
    stop_times = load_stop_times()
    trips = load_trips()
    routes = load_routes()

    graph = build_graph(stop_times, trips, routes)
    graph = add_transfers(graph)

    source = 175
    target = 30

    fastest = find_route(graph, source, target)
    fewest_stations = find_route_fewest_stations(graph, source, target)

    print_route(fastest, "Fastest")
    print_route(fewest_stations, "Fewest stations")
