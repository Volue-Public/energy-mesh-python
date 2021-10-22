from time import sleep
import grpc
import pytest
from volue.mesh import Connection
from volue.mesh.aio import Connection as AsyncConnection
import volue.mesh.tests.test_utilities.server_config as sc

@pytest.mark.server
def test_get_version():
    """Check if the server can respond with its version. |test|"""
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
    version_info = connection.get_version()
    assert version_info.full_version != ""


@pytest.mark.server
@pytest.mark.asyncio
async def test_async_get_version():
    """Check if the server can respond with its version. |testaio|"""
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
    version_info = await connection.get_version()
    assert version_info.full_version != ""


@pytest.mark.server
def test_open_and_close_session():
    """Check if a session can be opened and closed. |test|"""
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
    session = connection.create_session()
    session.open()
    assert session.session_id is not None
    session.close()
    assert session.session_id is None


@pytest.mark.server
@pytest.mark.asyncio
async def test_open_and_close_session():
    """Check if a session can be opened and closed. |testaio|"""
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
    session = connection.create_session()
    await session.open()
    assert session.session_id is not None
    await session.close()
    assert session.session_id is None


@pytest.mark.server
def test_can_connect_to_existing_session():
    """Check if it is possible to connect to an existing session. |test|
    1. Create a session.
    2. Connect to the session using a new object.
    3. Close using the new session object.
    4. Try to close the old session object, which should no longer be alive on the server."""
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
    session = connection.create_session()
    session.open()
    assert session.session_id is not None
    same_session = connection.connect_to_session(session.session_id)
    assert session.session_id == same_session.session_id
    assert session.mesh_service == same_session.mesh_service
    same_session.close()
    sleep(1)  # Closing a session on the server is not a blocking call, so there is not telling how long closing a session will take.
    with pytest.raises(grpc.RpcError) as info:
        session.close()
    assert info.type == grpc._channel._InactiveRpcError
    assert info.value.details() == ('Session with id {} not found.'.format({str(session.session_id).upper()})).replace("'", "")

@pytest.mark.server
def test_sessions_using_contextmanager():
    """Check if a session can be opened and closed using a contextmanager. |test|"""
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
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
async def test_sessions_using_async_contextmanager():
    """Check if a session can be opened and closed using a contextmanager. |testaio|"""
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT, sc.DefaultServerConfig.SECURE_CONNECTION)
    session_id1 = None
    session_id2 = None
    async with connection.create_session() as open_session:
        session_id1 = open_session.session_id
        assert session_id1 is not None

    async with connection.create_session() as open_session:
        session_id2 = open_session.session_id
        assert session_id1 is not None

    # Make sure the two sessions we opened were not the same
    assert session_id1 != session_id2


if __name__ == '__main__':
    pytest.main()
