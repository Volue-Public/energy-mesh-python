from __future__ import print_function
import logging

from volue import mesh
from volue.mesh import mesh_pb2

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    # Print version info
    logging.info(mesh.get_version_string())

    # Prepare a connection
    connection = mesh.connection()

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
            logging.info("%s : %s", str(point.timestamp), str(point.value))
            n += 1
    logging.info("Received %s points for timskey %s.", str(n), str(timskey))
