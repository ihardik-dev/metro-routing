TRANSFER_TIME = 5 * 60

TRANSFER_ROUTE = "TRANSFER"


TRANSFERS = [
    # station_a, station_b, line_a, line_b

    # Punjabi Bagh West ↔ Punjabi Bagh
    (176, 33, "P", "G"),

    # Dhaula Kuan ↔ Durgabai Deshmukh South Campus
    (156, 181, "O", "P"),

    # Noida Sector 52 ↔ Noida Sector 51
    (234, 500, "B", "A"),
]


def add_transfers(graph):

    for station_a, station_b, line_a, line_b in TRANSFERS:

        if station_a not in graph:
            graph[station_a] = {}

        if station_b not in graph:
            graph[station_b] = {}

        # A -> B
        graph[station_a][station_b] = {
            f"{TRANSFER_ROUTE}:{line_b}": TRANSFER_TIME
        }

        # B -> A
        graph[station_b][station_a] = {
            f"{TRANSFER_ROUTE}:{line_a}": TRANSFER_TIME
        }

    return graph