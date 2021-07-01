import asyncio

from volue import mesh

import utility.test_data as td
from utility.print import print_timeseries_points


async def do_some_async_work() -> None:
    # Prepare a connection
    connection = mesh.AsyncConnection()

    # Print version info
    version_info = await connection.get_version()
    print(version_info.full_version)

    # Start session
    await connection.start_session()

    start_time = td.eagle_wind.start_time
    end_time = td.eagle_wind.end_time
    timskey = td.eagle_wind.timskey
    interval = mesh.mesh_pb2.UtcInterval(
        start_time=start_time,
        end_time=end_time)

    # Send request, and wait for reply
    timeseries_reply = await connection.read_timeseries_points(
        timskey=timskey, interval=interval
    )

    # Lets have a look at what we got
    print("Original timeseries:")
    print_timeseries_points(timeseries_reply, timskey, True)

    # Lets edit some points:
    #TODO EDIT

    print("\nEdited timeseries points:")
    await connection.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=next(mesh.Timeserie.read_timeseries_reply(timeseries_reply)))

    # Let's have a look at the points again
    timeseries_reply = await connection.read_timeseries_points(
        timskey=timskey,
        interval=interval)
    print("\nTimeseries after editing:")
    print_timeseries_points(timeseries_reply, timskey, True)

    # Rollback
    await connection.rollback()
    print("\nTimeseries after Rollback:")
    timeseries = await connection.read_timeseries_points(
        timskey=timskey,
        interval=interval)
    print_timeseries_points(timeseries, timskey, True)

    # Edit again, and commit. Now the changes will be stored in database:
    print(
        "\nEdit timeseries again, and commit. Run the example "
        "again, to verify that the changes have been stored in DB.")
    await connection.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=next(mesh.Timeserie.read_timeseries_reply(timeseries_reply)))
    await connection.commit()

    await connection.end_session()


if __name__ == "__main__":
    asyncio.run(do_some_async_work())
