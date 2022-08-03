from datetime import datetime
from dateutil import tz

import grpc
import pandas as pd
import pyarrow as pa

from volue.mesh import Connection, Timeseries
from volue.mesh.calc import transform as Transform
from volue.mesh.calc.common import Timezone
from volue.mesh.examples import _get_connection_info


def main(address, port, root_pem_certificate):
    """Showing how to find time series, write, read points from it and convert them to pandas format."""

    query = "*[.Name=SomePowerPlantChimney2].TsRawAtt"  # make sure only 1 time series is returned
    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"

    connection = Connection(address, port, root_pem_certificate)
    with connection.create_session() as session:
        # first lets find a time series in our model
        try:
            timeseries_attributes = session.search_for_timeseries_attributes(
                start_object_path, query
            )
        except grpc.RpcError as e:
            print(f"Could not find time series attribute: {e}")
            return

        if len(timeseries_attributes) == 0:
            print("No such time series attribute in the given model/database")
            return

        print(f"Number of found time series: {len(timeseries_attributes)}")

        # pick the first time series and do some operations with it
        timeseries_attribute = timeseries_attributes[0]
        print("Working on timeseries with path: " + timeseries_attribute.path)

        # check for example the curve type of the connected physical time series
        print(f"Curve: {timeseries_attribute.time_series_resource.curve_type}")

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
                timestamps.append(
                    datetime(2016, 5, days, hours)
                )  # if no time zone is provided then the timestamp is treated as UTC
                values.append(days * 10)

            flags = [Timeseries.PointFlags.OK.value] * number_of_points

            arrays = [pa.array(timestamps), pa.array(flags), pa.array(values)]
            arrow_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

            timeseries = Timeseries(
                table=arrow_table, full_name=timeseries_attribute.path
            )
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
                target=timeseries_attribute, start_time=start_time, end_time=end_time
            )

            # convert to pandas format
            # the timestamps in PyArrow table are always returned in UTC format
            pandas_series = timeseries_read.arrow_table.to_pandas()

            # lets convert it back to local time zone
            # first convert to UTC time zone aware datetime object and then to local time zone (set in operating system)
            pandas_series["utc_time"] = pd.to_datetime(
                pandas_series["utc_time"], utc=True
            ).dt.tz_convert(local_time_zone)
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
            end_time = datetime(2016, 5, 4, tzinfo=local_time_zone)

            # Transform function may take optionally a time zone argument.
            # Refer to `transform` documentation for more details.
            # If you are using `LOCAL` or `STANDARD` time zone then make sure
            # the Mesh server is operating in the same time zone or adjust properly.
            transformed_timeseries = session.transform_functions(
                timeseries_attribute, start_time, end_time
            ).transform(Timeseries.Resolution.DAY, Transform.Method.SUM, Timezone.LOCAL)

            # convert to pandas format
            # the timestamps in PyArrow table are always returned in UTC format
            pandas_series = transformed_timeseries.arrow_table.to_pandas()
            print(pandas_series)

            # lets convert it back to local time zone
            # first convert to UTC time zone aware datetime object and then to local time zone (set in operating system)
            pandas_series["utc_time"] = pd.to_datetime(
                pandas_series["utc_time"], utc=True
            ).dt.tz_convert(local_time_zone)
            print(pandas_series)

            # do some further processing

        except Exception as e:
            print(f"Could not read transformed timeseries points: {e}")

        # optionally discard changes
        session.rollback()


if __name__ == "__main__":
    # This will search for a given time series, write some data,
    # read it and convert to pandas format.

    address, port, root_pem_certificate = _get_connection_info()
    main(address, port, root_pem_certificate)
