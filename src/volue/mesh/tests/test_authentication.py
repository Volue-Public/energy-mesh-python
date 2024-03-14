"""
Tests for volue.mesh.Authentication
"""

import sys

import grpc
import pytest
import pytest_asyncio

import volue.mesh.aio
from volue import mesh


@pytest.fixture
def auth_metadata_plugin(mesh_test_config):
    """Yields Authentication object. No clean-up is done (it requires Connection object)
    Note: Depending on the test-case there will be some tokens left (not revoked) in Mesh server.
    """
    assert mesh_test_config.creds_type == "kerberos"
    channel_credentials = grpc.ssl_channel_credentials(
        root_certificates=mesh_test_config.tls_root_certs
    )
    authentication_parameters = mesh.Authentication.Parameters(
        mesh_test_config.krb5_svc, mesh_test_config.krb5_usr
    )
    return mesh.Authentication(
        authentication_parameters, mesh_test_config.address, channel_credentials
    )


@pytest.fixture
def kerberos_connection(mesh_test_config) -> mesh.Connection:
    assert mesh_test_config.creds_type == "kerberos"
    connection = mesh.Connection.with_kerberos(
        mesh_test_config.address,
        mesh_test_config.tls_root_certs,
        mesh_test_config.krb5_svc,
        mesh_test_config.krb5_usr,
    )
    yield connection
    connection.revoke_access_token()


@pytest_asyncio.fixture
async def async_kerberos_connection(mesh_test_config) -> mesh.aio.Connection:
    assert mesh_test_config.creds_type == "kerberos"
    connection = mesh.aio.Connection.with_kerberos(
        mesh_test_config.address,
        mesh_test_config.tls_root_certs,
        mesh_test_config.krb5_svc,
        mesh_test_config.krb5_usr,
    )
    yield connection
    await connection.revoke_access_token()


@pytest.mark.authentication
def test_auth_metadata_plugin_obtains_valid_token_in_init(auth_metadata_plugin):
    """Check if newly created Authentication object has obtained valid Mesh token."""
    assert auth_metadata_plugin.token is not None
    assert auth_metadata_plugin.token_expiration_date is not None
    assert auth_metadata_plugin.is_token_valid()


@pytest.mark.authentication
def test_delete_access_token(auth_metadata_plugin):
    """Check if deleting access token correctly resets token class members."""
    auth_metadata_plugin.delete_access_token()
    assert auth_metadata_plugin.token is None
    assert auth_metadata_plugin.token_expiration_date is None


@pytest.mark.authentication
def test_is_valid_token_returns_false_for_deleted_access_token(auth_metadata_plugin):
    """Check if after deleting access token the validation method will return False."""
    auth_metadata_plugin.delete_access_token()
    assert auth_metadata_plugin.is_token_valid() is False


@pytest.mark.authentication
def test_auth_metadata_plugin_obtains_correctly_new_token_after_delete(
    auth_metadata_plugin,
):
    """Check if after deleting access token a new one is correctly obtained."""
    assert auth_metadata_plugin.is_token_valid()
    previous_token = auth_metadata_plugin.token
    previous_token_expiration_date = auth_metadata_plugin.token_expiration_date

    auth_metadata_plugin.delete_access_token()
    auth_metadata_plugin.get_token()
    new_token = auth_metadata_plugin.token
    new_token_expiration_date = auth_metadata_plugin.token_expiration_date

    assert auth_metadata_plugin.is_token_valid()
    assert new_token is not None
    assert new_token is not previous_token
    assert previous_token_expiration_date < new_token_expiration_date


@pytest.mark.authentication
def test_connection_revoke_access_token(kerberos_connection):
    """Check if revoking access token from Connection class correctly invalidates it."""
    assert kerberos_connection.auth_metadata_plugin.is_token_valid()
    kerberos_connection.revoke_access_token()
    assert kerberos_connection.auth_metadata_plugin.is_token_valid() is False


@pytest.mark.asyncio
@pytest.mark.authentication
async def test_async_connection_revoke_access_token(async_kerberos_connection):
    """Check if revoking access token from AsyncConnection class correctly invalidates it."""
    assert async_kerberos_connection.auth_metadata_plugin.is_token_valid()
    await async_kerberos_connection.revoke_access_token()
    assert async_kerberos_connection.auth_metadata_plugin.is_token_valid() is False


@pytest.mark.authentication
def test_connection_get_user_identity(kerberos_connection):
    """Check if getting user identity from Connection class returns something."""
    user_identity = kerberos_connection.get_user_identity()
    assert user_identity.display_name is not None
    assert user_identity.identifier is not None


@pytest.mark.asyncio
@pytest.mark.authentication
async def test_async_connection_get_user_identity(async_kerberos_connection):
    """Check if getting user identity from AsyncConnection class returns something."""
    user_identity = await async_kerberos_connection.get_user_identity()
    assert user_identity.display_name is not None
    assert user_identity.identifier is not None


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
