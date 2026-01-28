"""
Tests for version compatibility checks.
"""

import pytest
from volue.mesh import Connection
from volue.mesh._version_compatibility import ParsedVersion, to_parsed_version


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


def test_to_parsed_version():
    parsed = to_parsed_version("99.0.0+0")
    assert parsed is not None
    assert parsed.major == 99 and parsed.minor == 0 and parsed.patch == 0

    parsed = to_parsed_version("2.20.0")
    assert parsed is not None
    assert parsed.major == 2 and parsed.minor == 20 and parsed.patch == 0

    parsed = to_parsed_version("01.01.01")
    assert parsed is not None
    assert parsed.major == 1 and parsed.minor == 1 and parsed.patch == 1

    parsed = to_parsed_version("2.20")
    assert parsed is None

    parsed = to_parsed_version("-1.0.0")
    assert parsed is None

    parsed = to_parsed_version("a.0.0")
    assert parsed is None

    parsed = to_parsed_version("0,0.0")
    assert parsed is None

    parsed = to_parsed_version("")
    assert parsed is None


def test_parsed_version_comparisons():
    assert ParsedVersion(1, 1, 1) < ParsedVersion(2, 1, 1)
    assert ParsedVersion(1, 1, 1) < ParsedVersion(1, 2, 1)
    assert ParsedVersion(1, 1, 1) < ParsedVersion(1, 1, 2)
    assert ParsedVersion(0, 0, 0) < ParsedVersion(1, 1, 1)
