from __future__ import print_function
import logging

import grpc
import logging
import threading
import time
import asyncio

from volue.mesh.proto import mesh_pb2
from volue.mesh.proto import mesh_pb2_grpc
from volue.mesh import mesh_client

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    # Print version info
    logging.info(mesh_client.GetVersionString())

    timskey = 2125
    timeseries = mesh_client.GetTimeseriesPoints(theTimskey = timskey, theStartTime = 637450560000000000, theEndTime = 637451424000000000 )

    n = 0
    for segment in timeseries.segments:
        for point in segment.points:
            logging.info("%s : %s", str(point.timestamp), str(point.value))
            n+=1
    logging.info("Received %s points for timskey %s.", str(n), str(timskey))
    
