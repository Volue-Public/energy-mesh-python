import os
from datetime import datetime

import helpers

from volue.mesh import Connection

# Settings for the optional Microsoft Entra ID examples below. They are read
# from environment variables, so that no secrets are stored in the source code.
#
# - MESH_ENTRA_TENANT_ID: Directory (tenant) ID.
# - MESH_ENTRA_CLIENT_ID: Application (client) ID of the app registration that
#   represents your script or service.
# - MESH_ENTRA_CLIENT_SECRET: Client secret of that app registration. Needed
#   only when signing in as an application.
# - MESH_ENTRA_SCOPE: Scope exposed by the app registration that represents the
#   Mesh server, e.g.:
#   - "api://<mesh-server-client-id>/.default" when signing in as an application
#   - "api://<mesh-server-client-id>/<scope-name>" when signing in as a user
ENTRA_TENANT_ID = os.environ.get("MESH_ENTRA_TENANT_ID")
ENTRA_CLIENT_ID = os.environ.get("MESH_ENTRA_CLIENT_ID")
ENTRA_CLIENT_SECRET = os.environ.get("MESH_ENTRA_CLIENT_SECRET")
ENTRA_SCOPE = os.environ.get("MESH_ENTRA_SCOPE")

# MSAL application objects keep an in-memory token cache. Create them once and
# reuse them, so that subsequent token requests are served from the cache until
# the token is about to expire.
_msal_applications = {}


def _get_access_token_from_msal_result(result) -> str:
    if "access_token" not in result:
        raise RuntimeError(
            "Failed to obtain access token: "
            f"{result.get('error')}: {result.get('error_description')}"
        )
    return result["access_token"]


def get_entra_id_token_as_application() -> str:
    """
    Optional: obtain an access token from Microsoft Entra ID using the
    Microsoft Authentication Library (MSAL) for Python and the OAuth 2.0 client
    credentials flow. The script signs in as itself (an application), without
    any user interaction. Suitable for services and scheduled jobs.

    Requires: `pip install msal`

    Note: MSAL is a third-party library developed and maintained by Microsoft.
    It is not a part of the Mesh Python SDK. This is just an example. Volue
    does not maintain MSAL, takes no responsibility for it, and does not
    commit to keeping this example compatible with future MSAL versions.
    Please refer to the official MSAL and Microsoft Entra ID documentation for
    up to date and authoritative guidance:
    https://learn.microsoft.com/entra/msal/python/
    """
    import msal  # Third-party library, not a dependency of Mesh Python SDK.

    app = _msal_applications.get("application")
    if app is None:
        app = msal.ConfidentialClientApplication(
            ENTRA_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}",
            client_credential=ENTRA_CLIENT_SECRET,
        )
        _msal_applications["application"] = app

    # MSAL looks up its token cache first and requests a new token from
    # Microsoft Entra ID only when needed.
    result = app.acquire_token_for_client(scopes=[ENTRA_SCOPE])
    return _get_access_token_from_msal_result(result)


def get_entra_id_token_as_user() -> str:
    """
    Optional: obtain an access token from Microsoft Entra ID using the
    Microsoft Authentication Library (MSAL) for Python and the OAuth 2.0
    authorization code flow (with PKCE). A web browser is opened where the user
    signs in. Suitable for scripts run interactively by a user.

    The app registration that represents your script (MESH_ENTRA_CLIENT_ID)
    must be set up in Microsoft Entra ID as a public client (desktop)
    application with `http://localhost` (`http`, not `https`) as a redirect
    URI, and it must be granted the delegated permission for the scope exposed
    by the Mesh server app registration (MESH_ENTRA_SCOPE). Refer to the
    Microsoft Entra ID documentation for details.

    Requires: `pip install msal`

    Note: MSAL is a third-party library developed and maintained by Microsoft.
    It is not a part of the Mesh Python SDK. This is just an example. Volue
    does not maintain MSAL, takes no responsibility for it, and does not
    commit to keeping this example compatible with future MSAL versions.
    Please refer to the official MSAL and Microsoft Entra ID documentation for
    up to date and authoritative guidance:
    https://learn.microsoft.com/entra/msal/python/
    """
    import msal  # Third-party library, not a dependency of Mesh Python SDK.

    app = _msal_applications.get("user")
    if app is None:
        app = msal.PublicClientApplication(
            ENTRA_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}",
        )
        _msal_applications["user"] = app

    # First try to get the token from the cache (it is refreshed if needed),
    # so that the user needs to sign in only once.
    result = None
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent([ENTRA_SCOPE], account=accounts[0])

    if not result:
        result = app.acquire_token_interactive(scopes=[ENTRA_SCOPE])

    return _get_access_token_from_msal_result(result)


def main(address, tls_root_pem_cert):
    """
    Showing how to authorize to gRPC Mesh server using externally obtained
    access token, e.g: a OAuth JWT.

    How to obtain the access token depends on your authorization server and is
    in general out of scope for Mesh Python SDK. For Microsoft Entra ID, using
    Microsoft Authentication Library (MSAL) is suggested. See the optional
    `get_entra_id_token_*` functions above. Treat the access token as a secret,
    do not print or log it.
    """

    token = "my_token"
    # Optionally, if you are using Microsoft Entra ID, use one of:
    # token = get_entra_id_token_as_application()
    # token = get_entra_id_token_as_user()

    # Providing `root_certificates` is optional. If set to `None` root
    # certificates will be retrieved from a default location chosen by the gRPC
    # runtime.
    connection = Connection.with_external_access_token(
        address, tls_root_pem_cert, access_token=token
    )

    with connection.create_session() as session:
        # Print user information contained in the access token.
        user_identity = connection.get_user_identity()
        print(user_identity)

        # Read some time series data.
        # This requires the user has time series read permissions.
        timeseries_key = 3
        timeseries = session.read_timeseries_points(
            timeseries_key, datetime(2014, 1, 1), datetime(2015, 1, 1)
        )
        print(timeseries.arrow_table.to_pandas())

        # For long running sessions it may be necessary to refresh the access
        # token.
        # Other possibility would be to catch grpc.RpcError with status code
        # UNAUTHENTICATED and then get new access token and update it in the
        # Mesh connection using `update_external_access_token`.
        connection.update_external_access_token("my_new_access_token")
        # If you are using one of the optional Microsoft Entra ID functions,
        # just call it again. A new token is requested only when the cached one
        # is about to expire:
        # connection.update_external_access_token(get_entra_id_token_as_application())


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()

    # The call below is commented out on purpose: this example needs a Mesh
    # server running with TLS and OAuth enabled and a valid access token (see
    # `token` in `main`). Once you have both, uncomment it to run the example.
    # main(address, tls_root_pem_cert)
