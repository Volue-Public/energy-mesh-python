from volue.mesh.aio import Connection
from volue.mesh import dot_net_ticks_to_protobuf_timestamp
from volue.mesh.proto.mesh_pb2 import UtcInterval
from volue.mesh.examples.utility.print import get_connection_info
import volue.mesh.examples.utility.test_data as td

import asyncio


async def main(address, port, secure_connection) -> None:

    # First, prepare the connection:
    async_connection = Connection(address, port, secure_connection)

    async with async_connection.create_session() as session:

        # Let's request some timeseries.
        # While we wait for the response, we can
        # and do other stuff (like send new requests).
        interval = UtcInterval(
            start_time=dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.start_time_ticks),
            end_time=dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.end_time_ticks)
        )

        timskey_1 = td.eagle_wind.timskey
        timeseries_1_future = session.read_timeseries_points(
            timskey=timskey_1, interval=interval
        )

        # Do some other work
        await asyncio.sleep(1)

        # Send some other requests
        timskey_2 = td.eagle_wind.timskey
        timeseries_2_future = session.read_timeseries_points(
            timskey=timskey_2, interval=interval
        )

        timskey_3 = td.eagle_wind.timskey
        timeseries_3_future = session.read_timeseries_points(
            timskey=timskey_3, interval=interval
        )

        # Now we actually need the points, so lets make sure we have them:
        timeseries_1 = await timeseries_1_future
        timeseries_2 = await timeseries_2_future
        timeseries_3 = await timeseries_3_future


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()
    asyncio.run(main(address, port, secure_connection))
