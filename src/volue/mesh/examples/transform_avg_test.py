import asyncio
import random
import string
import uuid

from datetime import datetime

import helpers
import pandas as pd
import pyarrow as pa

from dateutil import tz

from volue import mesh
from volue.mesh.calc import transform as Transform

# # Define the time series identifier, it can be:
# # - time series key of a physical time series
# # - path of a time series attribute that is connected to a physical time series
# # - ID of a time series attribute that is connected to a physical time series
timeseries_key = 9


def get_pa_table_with_time_series_points() -> pa.Table:
    # Defining the data we want to write.
    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]

    # time_zone = tz.gettz("Europe/Warsaw")
    time_zone = tz.UTC

    arrays = [
        # if no time zone is provided then the timestamp is treated as UTC
        pa.array(
            [
                datetime(2024, 1, 1, 10),
                datetime(2024, 1, 1, 15),
                datetime(2024, 1, 3, 5),
            ]
        ),
        pa.array([mesh.Timeseries.PointFlags.OK.value] * 3),
        pa.array([100.0, 10.0, 20.0]),
    ]
    return pa.Table.from_arrays(arrays, schema=mesh.Timeseries.schema)


def write_timeseries_points(address, tls_root_pem_cert):
    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = mesh.Connection.with_tls(address, tls_root_pem_cert)
    connection = mesh.Connection.insecure(address)

    with connection.create_session() as session:
        table = get_pa_table_with_time_series_points()

        # Each time series point occupies 20 bytes. Mesh server has a limitation of 4MB inbound message size.
        # In case of larger data volumes please send input data in chunks.
        # E.g.: call multiple times `write_timeseries_points` with shorter interval.

        # Send request to write time series based on time series key.
        timeseries = mesh.Timeseries(table=table, timskey=timeseries_key)
        session.write_timeseries_points(timeseries=timeseries)
        print("Time series points written using time series key.")

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 4)

        # Each time series point occupies 20 bytes. By default gRPC has a limitation of 4MB inbound message size.
        # In case of larger data volumes please send request data in chunks.
        # E.g.: call multiple times `read_timeseries_points` with shorter interval.

        # Send request to read time series based on time series key.
        timeseries = session.read_timeseries_points(
            target=timeseries_key, start_time=start, end_time=end
        )

        print(f"Read {timeseries.number_of_points} points using time series key.")
        print(timeseries.arrow_table.to_pandas())

        transformed_timeseries = session.transform_functions(
            timeseries_key, start, end
        ).transform(mesh.Timeseries.Resolution.DAY, Transform.Method.AVG)

        print(transformed_timeseries.arrow_table.to_pandas())

        session.commit()


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    write_timeseries_points(
        address,
        tls_root_pem_cert,
    )
