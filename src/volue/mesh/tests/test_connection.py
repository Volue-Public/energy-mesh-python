"""
Tests for volue.mesh.Connection and volue.mesh.aio.Connection.
"""

import sys

import pytest


@pytest.mark.server
def test_get_version(connection):
    """Check if the server can respond with its version."""
    version_info = connection.get_version()
    # if all version numbers are single digits then the version length should be 7
    # E.g.: 0.0.0.0
    assert len(version_info.version) >= 7
    assert version_info.name == "Volue Mesh Server"


@pytest.mark.server
@pytest.mark.asyncio
async def test_async_get_version(async_connection):
    """Check if the server can respond with its version."""
    version_info = await async_connection.get_version()
    assert len(version_info.version) >= 7
    assert version_info.name == "Volue Mesh Server"


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
