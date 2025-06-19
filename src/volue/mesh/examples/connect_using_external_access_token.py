from datetime import datetime

import helpers

from volue.mesh import Connection


def main(address, tls_root_pem_cert):
    """
    Showing how to authorize to gRPC Mesh server using externally obtained
    access token, e.g: a OAuth JWT. Obtaining the access token is out of scope
    for this example.

    Depending on your environment, e.g.: Microsoft Entra ID, using libraries
    like Microsoft Authentication Library (MSAL) for getting the tokens is
    suggested.
    """

    token = "my_token"

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
        timeseries_key = 1388
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


if __name__ == "__main__":
    # This requires Mesh server to be running with enabled TLS and OAuth options.
    # Obtaining access token is out of the scope for this example.

    address, tls_root_pem_cert = helpers.get_connection_info()
    # main(address, tls_root_pem_cert)
