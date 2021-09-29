from volue.mesh import Connection, Timeserie, dot_net_ticks_to_protobuf_timestamp
from volue.mesh.proto.mesh_pb2 import UtcInterval
from volue.mesh.examples.utility.print import print_timeseries_points, get_connection_info
import volue.mesh.examples.utility.test_data as td


def main(address, port, secure_connection):

    # Prepare a connection
    connection = Connection(address, port, secure_connection)
    # Print version info
    version_info = connection.get_version()
    print(version_info.full_version)
    # Start session
    session = connection.create_session()
    session.open()
    # Preapare the request
    start = dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.start_time_ticks)
    end = dot_net_ticks_to_protobuf_timestamp(td.eagle_wind.end_time_ticks)
    timskey = td.eagle_wind.timskey
    interval = UtcInterval(
        start_time=start,
        end_time=end)
    # Send request, and wait for reply
    timeseries_reply = session.read_timeseries_points(
        timskey=timskey,
        interval=interval
    )
    # Lets edit some points:
    # TODO EDIT
    # Lets have a look at what we got
    print("Original timeseries:")
    print_timeseries_points(timeseries_reply, timskey)
    print("\nEdited timeseries points:")
    session.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=next(Timeserie.read_timeseries_reply(timeseries_reply)))
    # Let's have a look at the points again
    timeseries_reply = session.read_timeseries_points(
        timskey=timskey,
        interval=interval)
    print("\nTimeseries after editing:")
    print_timeseries_points(timeseries_reply, timskey)
    # Rollback
    session.rollback()
    print("\nTimeseries after Rollback:")
    timeseries_reply = session.read_timeseries_points(
        timskey=timskey,
        interval=interval)
    print_timeseries_points(timeseries_reply, timskey)
    # Edit again, and commit. Now the changes will be stored in database:
    print(
        "\nEdit timeseries again, and commit. Run the example "
        "again, to verify that the changes have been stored in DB.")
    session.write_timeseries_points(
        timskey=timskey,
        interval=interval,
        timeserie=next(Timeserie.read_timeseries_reply(timeseries_reply)))
    session.commit()
    session.close()


if __name__ == "__main__":
    address, port, secure_connection = get_connection_info()

    main(address, port, secure_connection)
