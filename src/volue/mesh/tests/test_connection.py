"""
Tests for volue.mesh.Connection and volue.mesh.aio.Connection.
"""

import sys

import pytest

from volue.mesh._connection import Connection


@pytest.mark.server
def test_get_version(connection):
    """Check if the server can respond with its version."""
    version_info = connection.get_version()
    # if all version numbers are single digits then the version length should be 7
    # E.g.: 0.0.0.0
    assert len(version_info.version) >= 7
    assert version_info.name == "Volue Mesh Server"


def test_connection_throws_if_mesh_server_version_is_incompatible(mocker):
    # Mock working with an old Mesh version,
    # this simulates a `VersionInfo` type.
    mock_response = mocker.Mock()
    mock_response.version = "2.1.0"

    # Mock configuration service to return mock version on `GetVersion` call
    mock_config_service = mocker.Mock()
    mock_config_service.GetVersion.return_value = mock_response

    # Mock the whole configuration service stub
    mocker.patch(
        "volue.mesh._base_connection.config_pb2_grpc.ConfigurationServiceStub",
        return_value=mock_config_service,
    )

    # When the channel is not None
    # the configuration service is populated
    mock_channel = mocker.Mock()
    with pytest.raises(RuntimeError) as e:
        Connection(channel=mock_channel)
    assert "connecting to incompatible server version" in str(e.value)


@pytest.mark.server
@pytest.mark.asyncio
async def test_async_get_version(async_connection):
    """Check if the server can respond with its version."""
    version_info = await async_connection.get_version()
    assert len(version_info.version) >= 7
    assert version_info.name == "Volue Mesh Server"


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
