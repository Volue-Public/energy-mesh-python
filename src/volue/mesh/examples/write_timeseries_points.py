import asyncio
import uuid
from datetime import datetime

import grpc
import helpers
import pandas as pd
import pyarrow as pa
from dateutil import tz

import volue.mesh.aio
from volue import mesh

# Define the time series identifier, it can be:
# - time series key of a physical time series
# - path of a time series attribute that is connected to a physical time series
# - ID of a time series attribute that is connected to a physical time series
timeseries_key = 3
timeseries_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2.TsRawAtt"
timeseries_attribute_id = uuid.UUID("e5df77a9-8b60-4b0a-aa1b-3c3957c538a0")


def get_pa_table_from_pa_arrays() -> pa.Table:
    """Create a sample PyArrow Table with time series points from PyArrow arrays."""

    # Defining the data we want to write.
    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]

    # time_zone = tz.gettz("Europe/Warsaw")
    time_zone = tz.UTC
    number_of_points = 3

    arrays = [
        # if no time zone is provided then the timestamp is treated as UTC
        pa.array(
            pd.date_range(
                datetime(2016, 1, 1, 1, tzinfo=time_zone),
                periods=number_of_points,
                freq="1h",
            )
        ),
        pa.array([mesh.Timeseries.PointFlags.OK.value] * number_of_points),
        pa.array([0.0, 10.0, 1000.0]),
    ]
    return pa.Table.from_arrays(arrays, schema=mesh.Timeseries.schema)


def get_pa_table_from_pandas() -> pa.Table:
    """Create a sample PyArrow Table with time series points from pandas DataFrame."""

    # Defining the data we want to write.
    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]

    # time_zone = tz.gettz("Europe/Warsaw")
    time_zone = tz.UTC
    number_of_points = 3

    df = pd.DataFrame(
        {
            mesh.Timeseries.TIMESTAMP_PA_FIELD_NAME: pd.date_range(
                datetime(2016, 1, 1, 1, tzinfo=time_zone),
                periods=number_of_points,
                freq="1h",
            ),
            mesh.Timeseries.FLAGS_PA_FIELD_NAME: [mesh.Timeseries.PointFlags.OK.value]
            * number_of_points,
            mesh.Timeseries.VALUE_PA_FIELD_NAME: [1.1, 22.2, 333.3],
        }
    )

    return pa.Table.from_pandas(df, schema=mesh.Timeseries.schema)


def sync_write_timeseries_points(address, tls_root_pem_cert):
    print("Synchronous write time series points:")

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = mesh.Connection.with_tls(address, tls_root_pem_cert)
    connection = mesh.Connection.insecure(address)

    with connection.create_session() as session:
        table = get_pa_table_from_pandas()

        # Each time series point occupies 20 bytes. Mesh server has a limitation of 4MB inbound message size.
        # In case of larger data volumes please send input data in chunks.
        # E.g.: call multiple times `write_timeseries_points` with shorter interval.

        # Send request to write time series based on time series key.
        timeseries = mesh.Timeseries(table=table, timskey=timeseries_key)
        session.write_timeseries_points(timeseries=timeseries)
        print("Time series points written using time series key.")

        # To only remove time series points we need to provide an empty PyArrow table, but with correct schema.
        empty_table = mesh.Timeseries.schema.empty_table()

        # If `start_time` and `end_time` are not provided explicitly they will be taken from PyArrow `table`.
        # Because we are providing empty table we must specify them explicitly.
        # For this interval all existing points will be removed.
        #
        # End time is exclusive so from the 3 points written by timeseries key,
        # 2 points will be removed by this call.
        #
        # Send request to write time series based on time series attribute path/full_name.
        timeseries = mesh.Timeseries(
            table=empty_table,
            start_time=datetime(2016, 1, 1, 1),
            end_time=datetime(2016, 1, 1, 3),
            full_name=timeseries_attribute_path,
        )
        session.write_timeseries_points(timeseries=timeseries)
        print("Time series points written using time series attribute path.")

        # Let's check it. We should get just one point.
        # Note:
        # - the `timeseries_attribute_path` and `timeseries_key` both point to the same time series attribute.
        # - the `end_time` in `read_timeseries_points` is also exclusive,
        #   but for time series with linear curve type Mesh is also returning one point after the interval.
        timeseries = session.read_timeseries_points(
            target=timeseries_key,
            start_time=datetime(2016, 1, 1, 1),
            end_time=datetime(2016, 1, 1, 3),
        )
        print(f"Read {timeseries.number_of_points} points using time series key.")
        print(timeseries.arrow_table.to_pandas())

        # Send request to write time series based on time series attribute ID.
        # Attribute IDs are auto-generated when an object is created.
        # That is why we can't use any fixed ID in this example and the code will throw.
        try:
            timeseries = mesh.Timeseries(table=table, uuid_id=timeseries_attribute_id)
            session.write_timeseries_points(timeseries=timeseries)
            print("Time series points written using time series attribute ID.")
        except grpc.RpcError as e:
            print(
                f"failed to write time series points based on time series attribute ID: {e}"
            )
        # Commit the changes to the database.
        # session.commit()

        # Or discard changes.
        session.rollback()


async def async_write_timeseries_points(
    address,
    tls_root_pem_cert,
):
    print("Asynchronous write time series points:")

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = mesh.aio.Connection.with_tls(address, tls_root_pem_cert)
    connection = mesh.aio.Connection.insecure(address)

    async with connection.create_session() as session:
        table = get_pa_table_from_pa_arrays()

        # Each time series point occupies 20 bytes. Mesh server has a limitation of 4MB inbound message size.
        # In case of larger data volumes please send input data in chunks.
        # E.g.: call multiple times `write_timeseries_points` with shorter interval.

        # Send request to write time series based on time series key.
        timeseries = mesh.Timeseries(table=table, timskey=timeseries_key)
        await session.write_timeseries_points(timeseries=timeseries)
        print("Time series points written using time series key.")

        # To only remove time series points we need to provide an empty PyArrow table, but with correct schema.
        empty_table = mesh.Timeseries.schema.empty_table()

        # If `start_time` and `end_time` are not provided explicitly they will be taken from PyArrow `table`.
        # Because we are providing empty table we must specify them explicitly.
        # For this interval all existing points will be removed.
        #
        # End time is exclusive so from the 3 points written by timeseries key,
        # 2 points will be removed by this call.
        #
        # Send request to write time series based on time series attribute path/full_name.
        timeseries = mesh.Timeseries(
            table=empty_table,
            start_time=datetime(2016, 1, 1, 1),
            end_time=datetime(2016, 1, 1, 3),
            full_name=timeseries_attribute_path,
        )
        await session.write_timeseries_points(timeseries=timeseries)
        print("Time series points written using time series attribute path.")

        # Let's check it. We should get just one point.
        # Note:
        # - the `timeseries_attribute_path` and `timeseries_key` both point to the same time series attribute.
        # - the `end_time` in `read_timeseries_points` is also exclusive,
        #   but for time series with linear curve type Mesh is also returning one point after the interval.
        timeseries = await session.read_timeseries_points(
            target=timeseries_key,
            start_time=datetime(2016, 1, 1, 1),
            end_time=datetime(2016, 1, 1, 3),
        )
        print(f"Read {timeseries.number_of_points} points using time series key.")
        print(timeseries.arrow_table.to_pandas())

        # Send request to write time series based on time series attribute ID.
        # Attribute IDs are auto-generated when an object is created.
        # That is why we can't use any fixed ID in this example and the code will throw.
        try:
            timeseries = mesh.Timeseries(table=table, uuid_id=timeseries_attribute_id)
            await session.write_timeseries_points(timeseries=timeseries)
            print("Time series points written using time series attribute ID.")
        except grpc.RpcError as e:
            print(
                f"failed to write time series points based on time series attribute ID: {e}"
            )

        # Commit the changes to the database.
        # await session.commit()

        # Or discard changes.
        await session.rollback()


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    sync_write_timeseries_points(
        address,
        tls_root_pem_cert,
    )
    asyncio.run(async_write_timeseries_points(address, tls_root_pem_cert))
