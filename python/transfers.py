# Extra real-world transfer connections
# not represented in the GTFS snapshot.

TRANSFER_TIME = 4 * 60  # 4 minutes

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

        graph[station_a][station_b] = TRANSFER_TIME
        graph[station_b][station_a] = TRANSFER_TIME

    return graph