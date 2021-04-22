from __future__ import print_function
import logging

from volue import mesh

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    # Print version info
    logging.info(mesh.get_version_string())

    timskey = 2125
    timeseries = mesh.get_timeseries_points(
        timskey=timskey,
        start_time=637450560000000000,
        end_time=637451424000000000,
    )

    n = 0
    for segment in timeseries.segments:
        for point in segment.points:
            logging.info("%s : %s", str(point.timestamp), str(point.value))
            n += 1
    logging.info("Received %s points for timskey %s.", str(n), str(timskey))
