from volue.mesh.aio import Connection
from volue.mesh import Timeserie, dot_net_ticks_to_protobuf_timestamp
from volue.mesh.proto.mesh_pb2 import UtcInterval
import volue.examples.utility.test_data as td
from volue.examples.utility.print import get_connection_info
from volue.examples.utility.print import print_timeseries_points

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

    start = dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.start_time_ticks)
    end = dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.end_time_ticks)
    timskey = td.eagle_wind.timskey
    interval = UtcInterval(
        start_time=start,
        end_time=end)

    # Send request, and wait for reply
    timeseries_reply = await session.read_timeseries_points(
        timskey=timskey, interval=interval
    )

    # Lets have a look at what we got
    print("Original timeseries:")
    print_timeseries_points(timeseries_reply, timskey)

    # Lets edit some points:
    # TODO EDIT

    print("\nEdited timeseries points:")
    await session.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=next(Timeserie.read_timeseries_reply(timeseries_reply)))

    # Let's have a look at the points again
    timeseries_reply = await session.read_timeseries_points(
        timskey=timskey,
        interval=interval)
    print("\nTimeseries after editing:")
    print_timeseries_points(timeseries_reply, timskey)

    # Rollback
    await session.rollback()
    print("\nTimeseries after Rollback:")
    timeseries = await session.read_timeseries_points(
        timskey=timskey,
        interval=interval)
    print_timeseries_points(timeseries, timskey)

    # Edit again, and commit. Now the changes will be stored in database:
    print(
        "\nEdit timeseries again, and commit. Run the example "
        "again, to verify that the changes have been stored in DB.")
    await session.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=next(Timeserie.read_timeseries_reply(timeseries_reply)))
    await session.commit()

    await session.close()


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()
    asyncio.run(main(address, port, secure_connection))
