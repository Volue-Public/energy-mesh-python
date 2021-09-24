from volue.mesh.async_connection import AsyncConnection
from volue.mesh.common import dot_net_ticks_to_protobuf_timestamp
from volue.mesh.proto.mesh_pb2 import UtcInterval
from volue.examples.utility.print import print_timeseries_points
from volue.examples.utility.print import get_connection_info
import volue.examples.utility.test_data as td

import asyncio


async def main(address, port, secure_connection) -> None:

    # First, prepare the connection:
    async_connection = AsyncConnection(address, port, secure_connection)
    await async_connection.start_session()

    # Print version info
    version_info = await async_connection.get_version()
    print(version_info.full_version)

    # Let's request some timeseries.
    # While we wait for the response, we can
    # and do other stuff (like send new requests).
    start = dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.start_time_ticks)
    end = dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.end_time_ticks)
    interval = UtcInterval(
        start_time=start,
        end_time=end
    )

    timskey_1 = td.eagle_wind.timskey

    print(f"Requesting timeseries points for timskey {timskey_1}")
    timeseries_1_future = async_connection.read_timeseries_points(
        timskey=timskey_1, interval=interval
    )

    # Do some other work
    await asyncio.sleep(1)

    # Send some other requests
    timskey_2 = td.eagle_wind.timskey
    print(f"Requesting timeseries points for timskey {timskey_2}")
    timeseries_2_future = async_connection.read_timeseries_points(
        timskey=timskey_2, interval=interval
    )

    timskey_3 = td.eagle_wind.timskey
    print(f"Requesting timeseries points for timskey {timskey_3}")
    timeseries_3_future = async_connection.read_timeseries_points(
        timskey=timskey_3, interval=interval
    )

    # Now we actually need the points, so lets make sure we have them:
    timeseries_1 = await timeseries_1_future
    print_timeseries_points(reply=timeseries_1, name=timskey_1)
    timeseries_2 = await timeseries_2_future
    print_timeseries_points(reply=timeseries_2, name=timskey_2)
    timeseries_3 = await timeseries_3_future
    print_timeseries_points(reply=timeseries_3, name=timskey_3)

    await async_connection.end_session()


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()
    asyncio.run(main(address, port, secure_connection))
