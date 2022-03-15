from datetime import datetime
from dateutil import tz

import grpc
import pandas as pd
import pyarrow as pa

from volue.mesh import Connection, MeshObjectId, Timeseries
from volue.mesh.calc import transform as Transform
from volue.mesh.calc.common import Timezone
from volue.mesh.examples import _get_connection_info


def main(address, port, root_pem_certificate):
    """Showing how to find timeseries, write, read points from it and convert them to pandas format."""

    model_name = "SimpleThermalTestModel"
    query = "*[.Name=SomePowerPlantChimney2].TsRawAtt"  # make sure only 1 timeseries is returned
    start_object_path = "ThermalComponent"

    connection = Connection(address, port, root_pem_certificate)
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
        #print('Curve ' + str(timeseries_attribute.entry.curve_type))

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
                timestamps.append(datetime(2016, 5, days, hours))  # if no time zone is provided then the timestamp is treated as UTC
                values.append(days * 10)

            flags = [Timeseries.PointFlags.OK.value] * number_of_points

            arrays = [
                pa.array(timestamps),
                pa.array(flags),
                pa.array(values)]
            arrow_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
            start_time = datetime(2016, 5, 1)  # if no time zone is provided then it will be treated as UTC
            end_time = datetime(2016, 5, 4)  # end time must be greater than last point to be written

            timeseries = Timeseries(table=arrow_table, start_time=start_time, end_time=end_time, full_name=timeseries_attribute.path)
            session.write_timeseries_points(timeseries)

        except grpc.RpcError as e:
            print(f"Could not write timeseries points: {e}")

        local_time_zone = tz.tzlocal()

        # now lets read from it
        try:
            # lets use local time zone (read from operating system settings)
            start_time = datetime(2016, 5, 1, tzinfo=local_time_zone)
            end_time = datetime(2016, 5, 4, tzinfo=local_time_zone)

            timeseries_read = session.read_timeseries_points(
                start_time=start_time, end_time=end_time, full_name=timeseries_attribute.path)

            # convert to pandas format
            # the timestamps in PyArrow table are always returned in UTC format
            pandas_series = timeseries_read.arrow_table.to_pandas()

            # lets convert it back to local time zone
            # first convert to UTC time zone aware datetime object and then to local time zone (set in operating system)
            pandas_series['utc_time'] = pd.to_datetime(pandas_series['utc_time'], utc=True).dt.tz_convert(local_time_zone)
            print(pandas_series)

            # notice that depending on the local time zone there is a shift in the data
            # e.g. for UTC+2 time zone, first 2 values will be NaN, because writing time series points in the previous step
            # is using time zone naive datetime object, so they are treated as UTC.

            # do some further processing

        except grpc.RpcError as e:
            print(f"Could not read timeseries points: {e}")

        # now lets read transformations from it (transform to days)
        print("Transform resolution to days:")
        try:
            start_time = datetime(2016, 5, 1, tzinfo=local_time_zone)
            end_time = datetime(2016, 5, 3, tzinfo=local_time_zone)

            # Transform function may take optionally a time zone argument.
            # Refer to `transform` documentation for more details.
            # If you are using `LOCAL` or `STANDARD` time zone then make sure
            # the Mesh server is operating in the same time zone or adjust properly.
            transformed_timeseries = session.transform_functions(
                MeshObjectId(uuid_id=timeseries_attribute.id), start_time, end_time).transform(
                    Timeseries.Resolution.DAY, Transform.Method.SUM, Timezone.LOCAL)

            # convert to pandas format
            # the timestamps in PyArrow table are always returned in UTC format
            pandas_series = transformed_timeseries.arrow_table.to_pandas()
            print(pandas_series)

            # lets convert it back to local time zone
            # first convert to UTC time zone aware datetime object and then to local time zone (set in operating system)
            pandas_series['utc_time'] = pd.to_datetime(pandas_series['utc_time'], utc=True).dt.tz_convert(local_time_zone)
            print(pandas_series)

            # do some further processing

        except Exception as e:
            print(f"Could not read transformed timeseries points: {e}")

        # optionally discard changes
        session.rollback()


if __name__ == "__main__":
    # This will search for a given timeseries, write some data,
    # read it and convert to pandas format.

    address, port, root_pem_certificate = _get_connection_info()
    main(address, port, root_pem_certificate)
