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

def PrintTimeseriesPoints(theTimeseries, theTimskey, verbose):
    n = 0
    for segment in theTimeseries.segments:
        for point in segment.points:
            if (verbose):
                logging.info("%s : %s", str(point.timestamp), str(point.value))
            n+=1
    logging.info("Received %s points for timskey %s.", str(n), str(theTimskey))

async def DoSomeWork() -> None:
    # Let's request some timeseries. We can send the request, and do other stuff (like send new requests)
    # while we wait for the response.
    interval = mesh_pb2.UtcInterval( start_time = 637450560000000000, end_time = 637451424000000000 )

    timskey_1 = 2125
    
    logging.info("Requesting timeseries points for timskey %s", str(timskey_1))
    timeseries_1_future = mesh_client.AsyncGetTimeseriesPoints(theTimskey = timskey_1, theInterval = interval)
    
    # Do some other work
    await asyncio.sleep(1)

    # Send some other requests
    timskey_2 = 2122
    logging.info("Requesting timeseries points for timskey %s", str(timskey_2))
    timeseries_2_future = mesh_client.AsyncGetTimeseriesPoints(theTimskey = timskey_2, theInterval = interval)

    timskey_3 = 2123
    logging.info("Requesting timeseries points for timskey %s", str(timskey_3))
    timeseries_3_future = mesh_client.AsyncGetTimeseriesPoints(theTimskey = timskey_3, theInterval = interval)

    # Now we actually need the points for timskey1, so lets make sure we have them:
    timeseries_1 = await timeseries_1_future
    PrintTimeseriesPoints(theTimeseries = timeseries_1, theTimskey = timskey_1, verbose = False)
    timeseries_2 = await timeseries_2_future
    PrintTimeseriesPoints(theTimeseries = timeseries_2, theTimskey = timskey_2, verbose = False)
    timeseries_3 = await timeseries_3_future
    PrintTimeseriesPoints(theTimeseries = timeseries_3, theTimskey = timskey_3, verbose = False)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    # Print version info
    logging.info(mesh_client.GetVersionString())

    asyncio.run(DoSomeWork())
   


    
