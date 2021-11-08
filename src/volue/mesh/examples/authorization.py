from volue.mesh import Authentication, Connection
from volue.mesh.examples import _get_connection_info


def main(address, port, secure_connection):
    """Showing how to authorize to gRPC Mesh server."""

    # If Mesh gRPC server is running as a service user,
    # for example LocalSystem, NetworkService or a user account
    # with a registered service principal name then it is enough
    # to provide hostname as service principal, e.g.:
    #   'HOST/hostname.ad.examplecompany.com'
    # If Mesh gRPC server is running as a user account without
    # registered service principal name then it is enough to provide
    # user account name running Mesh server as service principal, e.g.:
    #   'ad\\user.name' or r'ad\user.name'
    # Note: winkerberos converts service principal name if provided in
    #       RFC-2078 format. '@' is converted to '/' if there is no '/'
    #       character in the service principal name. E.g.:
    #           service@hostname
    #       Would be converted to:
    #           service/hostname
    authentication_parameters = Authentication.Parameters(
        'HOST/example.companyad.company.com')
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
