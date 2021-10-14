import asyncio
import uuid
from volue.mesh.aio import Connection
from volue.mesh import dot_net_ticks_to_protobuf_timestamp, eagle_wind
from volue.mesh.proto.mesh_pb2 import UtcInterval
from volue.mesh.examples import _get_connection_info


async def read_timeseries_points_async(session: Connection.Session):
    """Showing how to read timeseries points."""

    # Defining a time interval to read timeseries from
    interval = UtcInterval(
        start_time=dot_net_ticks_to_protobuf_timestamp(eagle_wind.start_time_ticks),
        end_time=dot_net_ticks_to_protobuf_timestamp(eagle_wind.end_time_ticks)
    )

    # Indicate that these two functions can be run concurrently
    timskey_timeseries, guid_timeseries = await asyncio.gather(
        session.read_timeseries_points(
            timskey=eagle_wind.timskey,  # Send request to read timeseries based on timskey
            interval=interval
        ),
        session.read_timeseries_points(
            guid=uuid.UUID(eagle_wind.guid), # Send request to read timeseries based on guid
            interval=interval
        )
    )
    print(f"Timskey timeseries contains {timskey_timeseries.number_of_points}.")
    print(f"Guid timeseries contains {guid_timeseries.number_of_points}.")


async def main(address, port, secure_connection):
    """Showing how to get timeseries points asynchronously."""
    connection = Connection(address, port, secure_connection)

    async with connection.create_session() as session:
        await read_timeseries_points_async(session)


if __name__ == "__main__":
    address, port, secure_connection = _get_connection_info()
    asyncio.run(main(address, port, secure_connection))
