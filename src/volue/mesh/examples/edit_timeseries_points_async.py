from volue.mesh.aio import Connection
from volue.mesh import Timeseries, dot_net_ticks_to_protobuf_timestamp
from volue.mesh.proto.mesh_pb2 import UtcInterval
import volue.mesh.examples.utility.test_data as td
from volue.mesh.examples.utility.print import get_connection_info

import asyncio


async def main(address, port, secure_connection) -> None:
    # Prepare a connection
    connection = Connection(address, port, secure_connection)

    # Print version info
    version_info = await connection.get_version()
    print(version_info.full_version)

    # Start session
    session = connection.create_session()
    await session.open()

    timskey = td.eagle_wind.timskey
    interval = UtcInterval(
        start_time=dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.start_time_ticks),
        end_time=dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.end_time_ticks))

    # Send request, and wait for reply
    timeserie = await session.read_timeseries_points(
        timskey=timskey, interval=interval
    )

    # TODO Create new points to write back

    await session.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=timeserie
    )

    # Let's have a look at the points again
    timeserie = await session.read_timeseries_points(
        timskey=timskey,
        interval=interval)

    # Rollback
    await session.rollback()
    timeseries = await session.read_timeseries_points(
        timskey=timskey,
        interval=interval)

    # Edit again, and commit. Now the changes will be stored in database:
    await session.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=timeseries
    )
    await session.commit()

    await session.close()


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()
    asyncio.run(main(address, port, secure_connection))
