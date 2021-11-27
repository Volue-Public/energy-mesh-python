
from volue.mesh import Timeseries
from volue.mesh.aio import Connection as AsyncConnection
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.tests.test_utilities.utilities import get_timeseries_data_2
import grpc
import pytest

@pytest.mark.asyncio
@pytest.mark.database
async def test_write_timeseries_points_using_timskey_async():
    """Check that timeseries can be written to the server using timskey."""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)
    ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_data_2()
    timeseries = Timeseries(table=modified_table, start_time=start_time, end_time=end_time, timskey=ts_entry.timeseries_key)

    async with connection.create_session() as session:
        try:
            await session.write_timeseries_points(
                timeserie=timeseries
            )
        except grpc.RpcError:
            pytest.fail("Could not write timeseries points")


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_timeseries_points_using_timskey_async():
    """Check that timeseries can be retrieved using timskey."""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)
    async with connection.create_session() as session:
        ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_data_2()
        try:
            timeseries = await session.read_timeseries_points(
                start_time=start_time,
                end_time=end_time,
                timskey=ts_entry.timeseries_key)
            assert len(timeseries) == 1
            assert timeseries[0].number_of_points == 312
        except grpc.RpcError:
            pytest.fail("Could not read timeseries points")

if __name__ == '__main__':
    pytest.main()
