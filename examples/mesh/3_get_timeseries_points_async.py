import asyncio
from volue import mesh
from volue.mesh import mesh_pb2


def print_timeseries_points(timeseries, timskey, verbose=False):
    n = 0
    for segment in timeseries.segments:
        for point in segment.points:
            if (verbose):
                print(str(point.timestamp) + ": " + str(point.value))
            n += 1
    print("Received " + str(n) + " points for timskey " + str(timskey))


async def do_some_async_work() -> None:
    # First, prepare the connection:
    async_connection = mesh.AsyncConnection()

    # Print version info
    version_info = await async_connection.get_version()
    print(version_info.full_version)

    # Let's request some timeseries.
    # While we wait for the response, we can
    # and do other stuff (like send new requests).
    interval = mesh_pb2.UtcInterval(
        start_time=637450560000000000, end_time=637451424000000000
    )

    timskey_1 = 2125

    print("Requesting timeseries points for timskey " + str(timskey_1))
    timeseries_1_future = async_connection.get_timeseries_points(
        timskey=timskey_1, interval=interval
    )

    # Do some other work
    await asyncio.sleep(1)

    # Send some other requests
    timskey_2 = 2122
    print("Requesting timeseries points for timskey " + str(timskey_2))
    timeseries_2_future = async_connection.get_timeseries_points(
        timskey=timskey_2, interval=interval
    )

    timskey_3 = 2123
    print("Requesting timeseries points for timskey " + str(timskey_3))
    timeseries_3_future = async_connection.get_timeseries_points(
        timskey=timskey_3, interval=interval
    )

    # Now we actually need the points, so lets make sure we have them:
    timeseries_1 = await timeseries_1_future
    print_timeseries_points(timeseries=timeseries_1, timskey=timskey_1)
    timeseries_2 = await timeseries_2_future
    print_timeseries_points(timeseries=timeseries_2, timskey=timskey_2)
    timeseries_3 = await timeseries_3_future
    print_timeseries_points(timeseries=timeseries_3, timskey=timskey_3)


if __name__ == "__main__":
    # Do some meaningful and important work
    asyncio.run(do_some_async_work())
