"""
Tests for volue.mesh.Connection.Session and volue.mesh.aio.Connection.Session.
"""

import asyncio
import random
import sys
import threading
from time import sleep

import grpc
import pytest

from .test_utilities.utilities import UNIT_1

# After this timeout an inactive session must be closed by the server.
# gRPC session timeout + ping interval + minimal margin:
# 5 mins + 1 min + 1 sec
SESSION_LIFETIME_EXTENSION_TESTS_SLEEP_VALUE_IN_SECS = 361


@pytest.mark.server
def test_open_and_close_session(connection):
    """Check if a session can be opened and closed. |test|"""
    session = connection.create_session()
    session.open()
    assert session.session_id is not None
    session.close()
    assert session.session_id is None


@pytest.mark.server
@pytest.mark.asyncio
async def test_async_open_and_close_session(async_connection):
    """Check if a session can be opened and closed. |testaio|"""
    session = async_connection.create_session()
    await session.open()
    assert session.session_id is not None
    await session.close()
    assert session.session_id is None


@pytest.mark.server
def test_can_connect_to_existing_session(connection):
    """Check if it is possible to connect to an existing session. |test|
    1. Create a session.
    2. Connect to the session using a new object.
    3. Close using the new session object.
    4. Try to close the old session object, which should no longer be alive on the server.
    """
    session = connection.create_session()
    session.open()
    assert session.session_id is not None
    same_session = connection.connect_to_session(session.session_id)
    assert session.session_id == same_session.session_id
    assert session.session_service == same_session.session_service
    # This is not how user should work with sessions.
    # A session opened by one `Session` object MUST be
    # closed using the same `Session` object.
    same_session.close()
    # Closing a session on the server is not a blocking call,
    # so there is not telling how long closing a session will take.
    sleep(1)
    with pytest.raises(grpc.RpcError) as info:
        session.close()
    assert info.type == grpc._channel._InactiveRpcError
    assert info.value.details() == (
        "Session with id {} not found.".format({str(session.session_id).upper()})
    ).replace("'", "")


@pytest.mark.server
def test_sessions_using_contextmanager(connection):
    """Check if a session can be opened and closed using a contextmanager. |test|"""
    session_id1 = None
    session_id2 = None
    with connection.create_session() as open_session:
        session_id1 = open_session.session_id
        assert session_id1 is not None

    with connection.create_session() as open_session:
        session_id2 = open_session.session_id
        assert session_id1 is not None

    # Make sure the two sessions we opened were not the same
    assert session_id1 != session_id2


@pytest.mark.server
@pytest.mark.asyncio
async def test_sessions_using_async_contextmanager(async_connection):
    """Check if a session can be opened and closed using a contextmanager. |testaio|"""
    session_id1 = None
    session_id2 = None

    async with async_connection.create_session() as open_session:
        session_id1 = open_session.session_id
        assert session_id1 is not None

    async with async_connection.create_session() as open_session:
        session_id2 = open_session.session_id
        assert session_id1 is not None

    # Make sure the two sessions we opened were not the same
    assert session_id1 != session_id2


@pytest.mark.asyncio
async def test_async_session_throws_if_mesh_server_version_is_incompatible(
    async_connection, mocker
):
    # Mock working with an old Mesh version,
    # this simulates a `VersionInfo` type.
    mock_response = mocker.Mock()
    mock_response.version = "2.1.0"

    # Mock GetVersion RPC returning the mocked response
    async_mock = mocker.AsyncMock(return_value=mock_response)
    async_connection.config_service.GetVersion = async_mock

    # Expect the exception
    with pytest.raises(RuntimeError) as e:
        async with async_connection.create_session() as _:
            pass
    assert "connecting to incompatible server version" in str(e.value)

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
                attribute_path, new_local_expression=new_local_expression
            )

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
                attribute_path, new_local_expression=old_local_expression
            )

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

    timeseries_key = 3
    new_unit_of_measurement = UNIT_1

    # check baseline
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement

    # change something
    session.update_timeseries_resource_info(
        timeseries_key=timeseries_key, new_unit_of_measurement=new_unit_of_measurement
    )

    # check that the change is in the session
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement == new_unit_of_measurement

    # rollback
    session.rollback()

    # check that changes have been discarded
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement


@pytest.mark.asyncio
@pytest.mark.database
async def test_rollback_and_commit_async(async_session):
    """For async run the simplest test, implementation is the same."""

    timeseries_key = 3
    new_unit_of_measurement = UNIT_1

    # check baseline
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement
    original_unit_of_measurement = timeseries_info.unit_of_measurement

    # change something
    await async_session.update_timeseries_resource_info(
        timeseries_key=timeseries_key, new_unit_of_measurement=new_unit_of_measurement
    )

    # check that the change is in the session
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement == new_unit_of_measurement

    # rollback
    await async_session.rollback()

    # check that changes have been discarded
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement

    # change something once again
    await async_session.update_timeseries_resource_info(
        timeseries_key=timeseries_key, new_unit_of_measurement=new_unit_of_measurement
    )

    # commit
    await async_session.commit()

    # check that the change persisted
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement == new_unit_of_measurement

    # rollback - nothing should change
    await async_session.rollback()

    # check that the committed change is still there
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement == new_unit_of_measurement

    # change it back to what is was originally
    await async_session.update_timeseries_resource_info(
        timeseries_key=timeseries_key,
        new_unit_of_measurement=original_unit_of_measurement,
    )

    # commit
    await async_session.commit()

    # check that status has been restored (important to keep db clean)
    timeseries_info = await async_session.get_timeseries_resource_info(
        timeseries_key=timeseries_key
    )
    assert timeseries_info.unit_of_measurement == original_unit_of_measurement


@pytest.mark.server
@pytest.mark.long
def test_session_lifetime_auto_extension_ctx_manager(connection):
    """
    Check if an inactive session lifetime is automatically extended.
    Session is created using `with` statement.
    """

    # open session using 'with' statement
    with connection.create_session() as session:
        sleep(SESSION_LIFETIME_EXTENSION_TESTS_SLEEP_VALUE_IN_SECS)

        # make some call, if the session is inactive then we will get an error
        session.list_models()


@pytest.mark.server
@pytest.mark.long
def test_sessions_lifetime_auto_extension(connection):
    """
    Check if inactive sessions lifetime is automatically extended.
    """

    session_1 = connection.create_session()
    session_2 = connection.create_session()

    # just to spice things up
    session_1.open()
    session_1.close()

    session_1.open()
    session_2.open()

    sleep(SESSION_LIFETIME_EXTENSION_TESTS_SLEEP_VALUE_IN_SECS)

    # make some calls, if the sessions are inactive then we will get an error
    session_1.list_models()
    session_2.list_models()

    session_1.close()
    session_2.close()


@pytest.mark.server
@pytest.mark.asyncio
@pytest.mark.long
async def test_async_session_lifetime_auto_extension_ctx_manager(async_connection):
    """
    Check if an inactive session lifetime is automatically extended.
    Session is created using `with` statement.
    """

    # open session using 'with' statement
    async with async_connection.create_session() as session:
        await asyncio.sleep(SESSION_LIFETIME_EXTENSION_TESTS_SLEEP_VALUE_IN_SECS)

        # make some call, if the session is inactive then we will get an error
        await session.list_models()


@pytest.mark.server
@pytest.mark.asyncio
@pytest.mark.long
async def test_async_sessions_lifetime_auto_extension(async_connection):
    """
    Check if inactive sessions lifetime is automatically extended.
    """

    session_1 = async_connection.create_session()
    session_2 = async_connection.create_session()

    # just to spice things up
    await session_1.open()
    await session_1.close()

    await session_1.open()
    await session_2.open()

    await asyncio.sleep(SESSION_LIFETIME_EXTENSION_TESTS_SLEEP_VALUE_IN_SECS)

    # make some calls, if the sessions are inactive then we will get an error
    await session_1.list_models()
    await session_2.list_models()

    await session_1.close()
    await session_2.close()


@pytest.mark.server
@pytest.mark.long
def test_model_changes_in_multiple_concurrent_sessions(connection):
    """
    Check if having multiple sessions open at the same time, with some of them
    doing changes and committing them, does not crash Mesh.
    """

    def update_simple_attribute(connection, path):
        with connection.create_session() as session:
            value = random.uniform(0, 10)
            session.update_simple_attribute(path, value)
            session.commit()

    def run_in_threads(connection, paths):
        threads = []
        for path in paths:
            for _ in range(10):
                thread = threading.Thread(
                    target=update_simple_attribute, args=(connection, path)
                )
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    session_with_no_changes = connection.create_session()
    session_with_no_changes.open()

    session_with_changes = connection.create_session()
    session_with_changes.open()
    session_with_changes.update_simple_attribute(
        "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1.Int64Att", 80
    )

    for _ in range(100):
        run_in_threads(
            connection,
            [
                "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney1.DblAtt",
                "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2.DblAtt",
                "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1.DblAtt",
            ],
        )

    session_with_no_changes.close()
    session_with_changes.close()


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
