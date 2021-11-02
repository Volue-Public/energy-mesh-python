import uuid
from datetime import datetime
from volue.mesh import Connection
from volue.mesh.examples import _get_connection_info
from volue.mesh.tests.test_utilities.utilities import eagle_wind


def read_timeseries_points(session: Connection.Session):
    """Showing how to read timeseries points."""

    # Defining a time interval to read timeseries from
    start = datetime(2016, 5, 1)
    end = datetime(2016, 5, 14)

    # Send request to read timeseries based on timskey
    timskey = eagle_wind.timskey
    timeseries = session.read_timeseries_points(start_time=start, end_time=end, timskey=timskey)
    for timeserie in timeseries:
        print(f"Read {timeserie.number_of_points} points")

    # Send request to read timeseries based on guid
    uuid_id = uuid.UUID(eagle_wind.guid)
    timeseries = session.read_timeseries_points(start_time=start, end_time=end, uuid_id=uuid_id)
    for timeserie in timeseries:
        print(f"Read {timeserie.number_of_points} points")


def main(address, port, secure_connection):
    """Showing how to get timeseries points."""
    connection = Connection(address, port, secure_connection)

    with connection.create_session() as session:
        read_timeseries_points(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)
