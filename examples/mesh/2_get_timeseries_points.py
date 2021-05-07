from volue import mesh
from volue.mesh import mesh_pb2

if __name__ == "__main__":
    # Prepare a connection
    connection = mesh.Connection()
    # Print version info
    version_info = connection.get_version()
    print(version_info.full_version)

    # Start session
    connection.start_session()

    # Preapare the request
    timskey = 2125
    interval = mesh_pb2.UtcInterval(
        start_time=637450560000000000, end_time=637451424000000000
    )

    # Send request, and wait for reply
    timeseries = connection.get_timeseries_points(
        timskey, interval
    )

    # Lets have a look at what we got
    n = 0
    for segment in timeseries.segments:
        for point in segment.points:
            print(f"{point.timestamp} : {point.value}")
            n += 1
    print(f"Received {n} points for timskey {timskey}")

    connection.end_session()
