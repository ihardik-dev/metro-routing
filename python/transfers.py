TRANSFER_TIME = 5 * 60

TRANSFER_ROUTE = "TRANSFER"


TRANSFERS = [
    # Punjabi Bagh West ↔ Punjabi Bagh
    (176, 33),

    # Dhaula Kuan ↔ Durgabai Deshmukh South Campus
    (156, 181),

    # Noida Sector 52 ↔ Noida Sector 51
    (234, 500),
]


def add_transfers(graph):

    for station_a, station_b in TRANSFERS:

        if station_a not in graph:
            graph[station_a] = {}

        if station_b not in graph:
            graph[station_b] = {}

        graph[station_a][station_b] = {
            TRANSFER_ROUTE: TRANSFER_TIME
        }

        graph[station_b][station_a] = {
            TRANSFER_ROUTE: TRANSFER_TIME
        }

    return graph