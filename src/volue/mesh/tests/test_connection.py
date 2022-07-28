"""
Tests for volue.mesh.Connection
"""

import sys

import grpc
import pytest

from volue.mesh.tests.test_utilities.utilities import get_physical_timeseries


@pytest.mark.database
def test_commit(connection):
    """Check that commit keeps changes between sessions"""
    attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.TsCalcAtt"
    new_local_expression = "something"

    with connection.create_session() as session1:
        try:
            # check baseline
            attribute1 = session1.get_timeseries_attribute(attribute_path)
            old_local_expression = attribute1.expression
            assert old_local_expression != new_local_expression

            # change something
            session1.update_timeseries_attribute(
                attribute_path, new_local_expression=new_local_expression)

            # commit
            session1.commit()

            # check that the change is in the session
            attribute2 = session1.get_timeseries_attribute(attribute_path)
            assert attribute2.expression == new_local_expression

            # rollback
            session1.rollback()

            # check that changes are still there
            attribute3 = session1.get_timeseries_attribute(attribute_path)
            assert attribute3.expression == new_local_expression

        except grpc.RpcError as error:
            pytest.fail(f"Could not commit changes: {error}")

    with connection.create_session() as session2:
        try:
            # check that the change is still there
            attribute4 = session2.get_timeseries_attribute(attribute_path)
            assert attribute4.expression == new_local_expression

            # change it back to what is was originally
            session2.update_timeseries_attribute(
                attribute_path, new_local_expression=old_local_expression)

            # commit
            session2.commit()

            # check that status has been restored (important to keep db clean)
            attribute5 = session2.get_timeseries_attribute(attribute_path)
            assert attribute5.expression == old_local_expression

        except grpc.RpcError as error:
            pytest.fail(f"Could not restore committed changes: {error}")


@pytest.mark.database
def test_rollback(session):
    """Check that rollback discards changes made in the current session."""

    timeseries = get_physical_timeseries()
    new_unit_of_measurement = "Unit1"

    # check baseline
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement

    # change something
    session.update_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key,
        new_unit_of_measurement=new_unit_of_measurement)

    # check that the change is in the session
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement == new_unit_of_measurement

    # rollback
    session.rollback()

    # check that changes have been discarded
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement


if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
