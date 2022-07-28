"""
Tests for volue.mesh.aio
"""

import sys

import grpc
import pytest

from volue.mesh.tests.test_utilities.utilities import get_physical_timeseries


@pytest.mark.asyncio
@pytest.mark.database
async def test_commit(async_connection):
    """Check that commit keeps changes between sessions"""
    attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.TsCalcAtt"
    new_local_expression = "something"

    async with async_connection.create_session() as session1:
        try:
            # check baseline
            attribute1 = await session1.get_timeseries_attribute(attribute_path)
            old_local_expression = attribute1.expression
            assert old_local_expression != new_local_expression

            # change something
            await session1.update_timeseries_attribute(
                attribute_path, new_local_expression=new_local_expression)

            # commit
            await session1.commit()

            # check that the change is in the session
            attribute2 = await session1.get_timeseries_attribute(attribute_path)
            assert attribute2.expression == new_local_expression

            # rollback
            await session1.rollback()

            # check that changes are still there
            attribute3 = await session1.get_timeseries_attribute(attribute_path)
            assert attribute3.expression == new_local_expression

        except grpc.RpcError as error:
            pytest.fail(f"Could not commit changes: {error}")

    async with async_connection.create_session() as session2:
        try:
            # check that the change is still there
            attribute4 = await session2.get_timeseries_attribute(attribute_path)
            assert attribute4.expression == new_local_expression

            # change it back to what is was originally
            await session2.update_timeseries_attribute(
                attribute_path, new_local_expression=old_local_expression)

            # commit
            await session2.commit()

            # check that status has been restored (important to keep db clean)
            attribute5 = await session2.get_timeseries_attribute(attribute_path)
            assert attribute5.expression == old_local_expression

        except grpc.RpcError as error:
            pytest.fail(f"Could not restore committed changes: {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_rollback(async_session):
    """Check that rollback discards changes made in the current session."""
    timeseries = get_physical_timeseries()
    new_unit_of_measurement = "Unit1"

    # check baseline
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement

    # change something
    await async_session.update_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key,
        new_unit_of_measurement=new_unit_of_measurement)

    # check that the change is in the session
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement == new_unit_of_measurement

    # rollback
    await async_session.rollback()

    # check that changes have been discarded
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement


if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
