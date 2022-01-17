import pytest

from volue.mesh import Authentication, Connection, Credentials
from volue.mesh.aio import Connection as AsyncConnection
import volue.mesh.tests.test_utilities.server_config as sc


@pytest.fixture
def auth_metadata_plugin():
    """Yields Authentication object. No clean-up is done (it requires Connection object)
    Note: Depending on the test-case there will be some tokens left (not revoked) in Mesh server."""
    target = f'{sc.DefaultServerConfig.ADDRESS}:{sc.DefaultServerConfig.PORT}'
    credentials = Credentials()
    authentication_parameters = Authentication.Parameters(
        sc.DefaultServerConfig.KERBEROS_SERVICE_PRINCIPAL_NAME)
    return Authentication(authentication_parameters, target, credentials.channel_creds)


@pytest.fixture
def connection():
    """Yields Connection object and revokes access token in clean-up."""
    authentication_parameters = Authentication.Parameters(
        sc.DefaultServerConfig.KERBEROS_SERVICE_PRINCIPAL_NAME)
    conn = Connection(sc.DefaultServerConfig.ADDRESS,
                      sc.DefaultServerConfig.PORT,
                      True,  # authentication requires TLS (to make sure tokens are encrypted)
                      authentication_parameters)
    yield conn

    # clean-up
    conn.revoke_access_token()


@pytest.fixture
async def aconnection():
    """Yields AsyncConnection object and revokes access token in clean-up."""
    authentication_parameters = Authentication.Parameters(
        sc.DefaultServerConfig.KERBEROS_SERVICE_PRINCIPAL_NAME)
    aconn = AsyncConnection(sc.DefaultServerConfig.ADDRESS,
                            sc.DefaultServerConfig.PORT,
                            True,  # authentication requires TLS (to make sure tokens are encrypted)
                            authentication_parameters)
    yield aconn

    # clean-up
    await aconn.revoke_access_token()


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
def test_auth_metadata_plugin_obtains_correctly_new_token_after_delete(auth_metadata_plugin):
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
def test_connection_revoke_access_token(connection):
    """Check if revoking access token from Connection class correctly invalidates it."""
    assert connection.auth_metadata_plugin.is_token_valid()
    connection.revoke_access_token()
    assert connection.auth_metadata_plugin.is_token_valid() is False


@pytest.mark.asyncio
@pytest.mark.authentication
async def test_async_connection_revoke_access_token(aconnection):
    """Check if revoking access token from AsyncConnection class correctly invalidates it."""
    assert aconnection.auth_metadata_plugin.is_token_valid()
    await aconnection.revoke_access_token()
    assert aconnection.auth_metadata_plugin.is_token_valid() is False


@pytest.mark.authentication
def test_connection_get_user_identity(connection):
    """Check if getting user identity from Connection class returns something."""
    user_identity = connection.get_user_identity()
    assert user_identity.display_name is not None
    assert user_identity.identifier is not None


@pytest.mark.asyncio
@pytest.mark.authentication
async def test_async_connection_get_user_identity(aconnection):
    """Check if getting user identity from AsyncConnection class returns something."""
    user_identity = await aconnection.get_user_identity()
    assert user_identity.display_name is not None
    assert user_identity.identifier is not None


if __name__ == '__main__':
    pytest.main()
