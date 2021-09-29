from volue.mesh import Connection
from volue.mesh.aio import Connection as AsyncConnection
from volue.tests.test_utilities.server_config import ADDRESS, PORT, SECURE_CONNECTION

import unittest
import pytest


@pytest.mark.server
def test_get_version():
    connection = Connection(ADDRESS, PORT, SECURE_CONNECTION)
    version_info = connection.get_version()
    assert version_info.full_version != ""


@pytest.mark.server
@pytest.mark.asyncio
async def test_async_get_version():
    connection = AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION)
    version_info = await connection.get_version()
    assert version_info.full_version != ""


@pytest.mark.server
@pytest.mark.asyncio
async def test_open_session():
    connection = AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION)
    session = connection.create_session()
    await session.open()
    await session.close()


@pytest.mark.server
@pytest.mark.asyncio
async def test_open_session_using_contextmanager():
    connection = AsyncConnection(ADDRESS, PORT, SECURE_CONNECTION)
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
    unittest.main()
