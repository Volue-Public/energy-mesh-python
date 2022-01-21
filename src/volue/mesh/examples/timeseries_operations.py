from volue.mesh import Connection, Timeseries
from volue.mesh.examples import _get_connection_info
from volue.mesh._common import CalendarType, TransformationMethod, TransformationResolution

from datetime import datetime
import grpc
import pyarrow as pa

def main(address, port, secure_connection):
    """Showing how to find timeseries, write, read points from it and convert them to pandas format."""

    model_name = "SimpleThermalTestModel"
    query = "*[.Name=SomePowerPlantChimney2].TsRawAtt"  # make sure only 1 timeseries is returned
    start_object_path = "ThermalComponent"

    connection = Connection(address, port, secure_connection)
    with connection.create_session() as session:
        # first lets find a timeseries in our model
        try:
            timeseries_attributes = session.search_for_timeseries_attribute(model_name, query, start_object_path)
        except grpc.RpcError as e:
            print(f"Could not find timeseries attribute: {e}")
            return

        if len(timeseries_attributes) == 0:
            print("No such timeseries attribute in the given model/database")
            return

        print(f'Number of timeseries: {len(timeseries_attributes)}')

        # pick the first timeseries and do some operations with it
        timeseries_attribute = timeseries_attributes[0]
        print('Working on timeseries with path: ' + timeseries_attribute.path)

        # check for example the unit of measurement or curve type
        print('Unit of measurement: ' + timeseries_attribute.entry.unit_of_measurement)
        print('Curve ' + str(timeseries_attribute.entry.curveType))

        # now lets write some data to it
        try:
            # Mesh data is organized as an Arrow table with the following schema:
            # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
            # flags - [pa.uint32]
            # value - [pa.float64]

            number_of_points = 72
            timestamps = []
            values = []
            for i in range(0, number_of_points):
                hours = i % 24
                days = int(i / 24) + 1
                timestamps.append(datetime(2016, 5, days, hours))
                values.append(days * 10)

            flags = [Timeseries.PointFlags.NOT_OK.value] * number_of_points

            arrays = [
                pa.array(timestamps),
                pa.array(flags),
                pa.array(values)]
            arrow_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
            start_time = datetime(2016, 5, 1)  # timezone provided in start and end datetimes will be discarded, it will be treated as UTC
            end_time = datetime(2016, 5, 4)  # end time must be greater than last point to be written

            timeseries = Timeseries(table=arrow_table, start_time=start_time, end_time=end_time, full_name=timeseries_attribute.path)
            session.write_timeseries_points(timeseries)

        except grpc.RpcError as e:
            print(f"Could not write timeseries points: {e}")

        # now lets read from it
        try:
            start_time = datetime(2016, 5, 1)  # timezone provided in start and end datetimes will be discarded, it will be treated as UTC
            end_time = datetime(2016, 5, 4)

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
            print(f"Could not read timeseries points: {e}")

        # now lets read transformations from it (transform to days)
        try:
            start_time = datetime(2016, 5, 1)  # timezone provided in start and end datetimes will be discarded, it will be treated as UTC
            end_time = datetime(2016, 5, 3)

            timeseries_read = session.read_transformed_timeseries_points(
                start_time=start_time,
                end_time=end_time,
                resolution=TransformationResolution.DAY,
                method=TransformationMethod.SUM,
                calendar_type=CalendarType.UTC,
                uuid_id=timeseries_attribute.id)

            # convert to pandas format
            pandas_series = timeseries_read.arrow_table.to_pandas()
            print(pandas_series)

            # do some further processing

        except Exception as e:
            print(f"Could not read transformed timeseries points: {e}")

        # optionally discard changes
        session.rollback()


if __name__ == "__main__":
    # This will search for a given timeseries, write some data,
    # read it and convert to pandas format.

    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)