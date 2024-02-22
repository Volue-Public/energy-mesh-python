import asyncio
import uuid
from datetime import datetime

import pyarrow as pa

from volue.mesh import Timeseries
from volue.mesh.aio import Connection
import helpers


async def write_timeseries_points(session: Connection.Session):
    """Showing how to write timeseries points."""

    # Define the time series identifier, it can be:
    # - time series key of a physical time series
    # - path of a time series attribute that is connected to a physical time series
    # - ID of a time series attribute that is connected to a physical time series
    timeseries_key = 3
    timeseries_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2.TsRawAtt"
    timeseries_attribute_id = uuid.UUID("e5df77a9-8b60-4b0a-aa1b-3c3957c538a0")

    # Defining the data we want to write.
    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]
    arrays = [
        # if no time zone is provided then the timestamp is treated as UTC
        pa.array(
            [datetime(2016, 1, 1, 1), datetime(2016, 1, 1, 2), datetime(2016, 1, 1, 3)]
        ),
        pa.array([Timeseries.PointFlags.OK.value] * 3),
        pa.array([0.0, 10.0, 1000.0]),
    ]
    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    # Send requests to write time series based on timskey.
    timeseries = Timeseries(table=table, timskey=timeseries_key)
    await session.write_timeseries_points(timeseries=timeseries)
    print("Time series points written using time series key.")

    # Send requests to write time series based on time series attribute path/full_name.
    timeseries = Timeseries(table=table, full_name=timeseries_attribute_path)
    await session.write_timeseries_points(timeseries=timeseries)
    print("Time series points written using time series attribute path.")

    # Send requests to write time series based on time series attribute ID.
    # Attribute IDs are auto-generated when an object is created.
    # That is why we can't use any fixed ID in this example and the code is commented out.
    # timeseries = Timeseries(table=table, uuid_id=timeseries_attribute_id)
    # await session.write_timeseries_points(timeseries=timeseries)
    # print("Time series points written using time series attribute ID.")

    # Commit the changes to the database.
    # await session.commit()

    # Or discard changes.
    await session.rollback()


async def main(address, port, root_pem_certificate):
    """Showing how to write timeseries points."""
    connection = Connection(address, port, root_pem_certificate)

    async with connection.create_session() as session:
        await write_timeseries_points(session)


if __name__ == "__main__":
    address, port, root_pem_certificate = helpers.get_connection_info()
    asyncio.run(main(address, port, root_pem_certificate))
