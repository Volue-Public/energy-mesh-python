
from volue import mesh

from utility.print import print_timeseries_points
import utility.test_data as td


if __name__ == "__main__":
    # Prepare a connection
    connection = mesh.Connection()

    # Print version info
    version_info = connection.get_version()
    print(version_info.full_version)

    # Start session
    connection.start_session()

    # Preapare the request
    start = mesh.windows_ticks_to_protobuf_timestamp(td.eagle_wind.start_time_ticks)
    end = mesh.windows_ticks_to_protobuf_timestamp(td.eagle_wind.end_time_ticks)
    timskey = td.eagle_wind.timskey
    interval = mesh.mesh_pb2.UtcInterval(
        start_time=start,
        end_time=end)

    # Send request, and wait for reply
    timeseries_reply = connection.read_timeseries_points(
        timskey=timskey,
        interval=interval
    )

    # Lets edit some points:
    #TODO EDIT

    # Lets have a look at what we got
    print("Original timeseries:")
    print_timeseries_points(timeseries_reply, timskey)


    print("\nEdited timeseries points:")
    connection.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=next(mesh.Timeserie.read_timeseries_reply(timeseries_reply)))

    # Let's have a look at the points again
    timeseries_reply = connection.read_timeseries_points(
        timskey=timskey,
        interval=interval)
    print("\nTimeseries after editing:")
    print_timeseries_points(timeseries_reply, timskey)

    # Rollback
    connection.rollback()
    print("\nTimeseries after Rollback:")
    timeseries_reply = connection.read_timeseries_points(
        timskey=timskey,
        interval=interval)
    print_timeseries_points(timeseries_reply, timskey)

    # Edit again, and commit. Now the changes will be stored in database:
    print(
        "\nEdit timeseries again, and commit. Run the example "
        "again, to verify that the changes have been stored in DB.")
    connection.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=next(mesh.Timeserie.read_timeseries_reply(timeseries_reply)))
    connection.commit()

    connection.end_session()
