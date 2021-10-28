from volue.mesh import Authentication, Connection
from volue.mesh.examples import _get_connection_info


def main(address, port, secure_connection):
    """Showing how to authorize to gRPC Mesh server."""

    authentication_parameters = Authentication.Parameters('HOST/tdtrhsmgTrunkA3.voluead.volue.com')
    connection = Connection(address, port, secure_connection, authentication_parameters)

    user_identity = connection.get_user_identity()
    print(user_identity)


if __name__ == "__main__":
    # This will authenticate Python client (receive authorization token from Mesh),
    # then send gRPC request that requires authorization (e.g.: GetUserIdentity)
    # and print the result. If your user name info is printed, you have successfully
    # communicated with the server.
    #
    # This requires Mesh server to be running with enabled TLS and Kerberos options:
    # GRPC.EnableTLS(true)
    # GRPC.EnableKerberos(true)

    address, port, secure_connection = _get_connection_info()
    main(address, port, secure_connection)
