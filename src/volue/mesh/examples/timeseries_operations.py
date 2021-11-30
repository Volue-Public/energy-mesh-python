from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh import Connection, Timeseries
from volue.mesh.examples import _get_connection_info

from datetime import datetime, timezone
import grpc
import pyarrow as pa

def main(address, port, secure_connection):
    """Showing how find timeseries, write, read points from it and convert them to pandas format."""

    model_name = "TimeSeriesConsistencyTestsModel"
    query = "{*}.TsRawAtt"
    start_object_path = "ThermalComponent"

    connection = Connection(address, port, secure_connection)
    with connection.create_session() as session:
        # first lets find a timeseries in our model
        try:
            timeseries_attributes = session.search_for_timeseries_attribute(model_name, query, start_object_path)
        except grpc.RpcError as e:
            print(f"Could not find timeseries attribute: {e}")
            return

        if timeseries_attributes is None:
            print("No such timeseries attribute in the given model/database")
            return

        # pick the first timeseries and do some operations with it
        timeseries_attribute = timeseries_attributes[0]

        # check for example the unit of measurement or curve type
        print('Unit of measurement: ' + timeseries_attribute.entry.unit_of_measurement)
        print('Curve ' + str(timeseries_attribute.entry.curveType))

        # now lets write some data to it
        try:
            # Mesh data is organized as an Arrow table with the following schema:
            # utc_time - [pa.date64] as a UTC Unix timestamp expressed in milliseconds
            # flags - [pa.uint32]
            # value - [pa.float64]
            interval_1 = int(datetime(2016, 5, 1, tzinfo=timezone.utc).timestamp() * 1000)  # to get milliseconds
            interval_2 = int(datetime(2016, 5, 2, tzinfo=timezone.utc).timestamp() * 1000)  # to get milliseconds
            interval_3 = int(datetime(2016, 5, 3, tzinfo=timezone.utc).timestamp() * 1000)  # to get milliseconds

            arrays = [
                pa.array([interval_1, interval_2, interval_3]),
                pa.array([0, 0, 0]),
                pa.array([1.1, 2.2, 3.3])]
            arrow_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
            start_time = datetime(2016, 5, 1, tzinfo=timezone.utc)
            end_time = datetime(2016, 5, 4, tzinfo=timezone.utc)  # end time must be greater than last point to be read

            timeseries = Timeseries(table=arrow_table, start_time=start_time, end_time=end_time, full_name=timeseries_attribute.path)
            session.write_timeseries_points(timeseries)

        except grpc.RpcError as e:
            print(f"Could not write timeseries points {e}")

        # now lets read from it
        try:
            start_time = datetime(2016, 5, 1, tzinfo=timezone.utc)
            end_time = datetime(2016, 5, 4, tzinfo=timezone.utc)  # end time must be greater than last point to be read

            timeseries_read = session.read_timeseries_points(start_time=start_time, end_time=end_time, full_name=timeseries_attribute.path)
            # there should be exactly one timeseries read
            if len(timeseries_read) != 1:
                print("Invalid timeseries")
                return

            # convert to pandas format
            pandas_series = timeseries_read[0].arrow_table.to_pandas()
            print(pandas_series)

            # do some further processing

        except grpc.RpcError as e:
            print(f"Could not read timeseries points {e}")


if __name__ == "__main__":
    # This will search for a given timeseries, write some data,
    # read it and convert to pandas format.

    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)