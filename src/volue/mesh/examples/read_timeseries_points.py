import uuid
from datetime import datetime
from volue.mesh import Connection
from volue.mesh.examples import _get_connection_info


def read_timeseries_points(session: Connection.Session):
    """Showing how to read timeseries points."""

    # Define the timeseries identifiers
    timeseries_full_name = "Resource/SimpleThermalTestResourceCatalog/chimney2TimeSeriesRaw"
    timeseries_id = uuid.UUID("00000003-0003-0000-0000-000000000000")

    # Defining a time interval to read timeseries from
    start = datetime(2016, 1, 1, 6, 0, 0)
    end = datetime(2016, 1, 1, 8, 0, 0)

    # Send request to read timeseries based on path
    timeseries = session.read_timeseries_points(start_time=start, end_time=end, full_name=timeseries_full_name)
    print(f"Read {timeseries.number_of_points} points")

    # OR

    # Send request to read timeseries based on guid
    timeseries = session.read_timeseries_points(start_time=start, end_time=end, uuid_id=timeseries_id)
    print(f"Read {timeseries.number_of_points} points")


def main(address, port, root_certificate_path):
    """Showing how to get timeseries points."""
    connection = Connection(address, port, root_certificate_path)

    with connection.create_session() as session:
        read_timeseries_points(session)


if __name__ == "__main__":
    address, port, root_certificate_path = _get_connection_info()
    main(address, port, root_certificate_path)
