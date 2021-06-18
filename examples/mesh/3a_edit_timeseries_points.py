from volue import mesh
from volue.mesh import mesh_pb2
import random


def print_timeseries_points(timeseries, timskey, verbose=False):
    n = 0
    for segment in timeseries.segments:
        for point in segment.points:
            if verbose:
                print(f"{point.timestamp} : {point.value}")
            n += 1
    print(f"Received {n} points for timskey {timskey}")


if __name__ == "__main__":
    # Prepare a connection
    connection = mesh.Connection()
    # Print version info
    version_info = connection.get_version()
    print(version_info.full_version)

    # Start session
    connection.start_session()

    start_time = 637450560000000000
    end_time = 637450776000000000
    # Preapare the request
    timskey = 2125
    interval = mesh_pb2.UtcInterval(
        start_time=start_time,
        end_time=end_time)

    # Send request, and wait for reply
    timeseries = connection.get_timeseries_points(
        timskey=timskey,
        interval=interval
    )

    # Lets have a look at what we got
    print("Original timeseries:")
    print_timeseries_points(timeseries, timskey, True)

    # Lets edit some points:
    t = start_time
    segment = mesh_pb2.TimeseriesSegment()

    while (t < end_time):
        point = segment.points.add()
        point.value = random.randint(-10000, 10000)
        point.timestamp = t
        t += 36000000000

    print("\nEdited timeseries points:")
    connection.edit_timeseries_points(
        timskey=timskey,
        interval=interval,
        points=segment)

    # Let's have a look at the points again
    timeseries = connection.get_timeseries_points(
        timskey=timskey,
        interval=interval)
    print("\nTimeseries after editing:")
    print_timeseries_points(timeseries, timskey, True)

    # Rollback
    connection.rollback()
    print("\nTimeseries after Rollback:")
    timeseries = connection.get_timeseries_points(
        timskey=timskey,
        interval=interval)
    print_timeseries_points(timeseries, timskey, True)

    # Edit again, and commit. Now the changes will be stored in database:
    print(
        "\nEdit timeseries again, and commit. Run the example "
        "again, to verify that the changes have been stored in DB.")
    connection.edit_timeseries_points(
        timskey=timskey,
        interval=interval,
        points=segment)
    connection.commit()

    connection.end_session()
