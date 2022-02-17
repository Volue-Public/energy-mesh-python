import asyncio

from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh import Authentication, Connection
from volue.mesh.examples import _get_connection_info


def main(address, port, root_certificate_path):
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

    print("Synchronous authentication example: ")
    connection = Connection(address, port, root_certificate_path, authentication_parameters)
    user_identity = connection.get_user_identity()
    print(user_identity)

    # revoke no longer used token
    connection.revoke_access_token()

    print("Asynchronous authentication example: ")
    aconnection = AsyncConnection(address, port, root_certificate_path, authentication_parameters)
    user_identity = asyncio.get_event_loop().run_until_complete(aconnection.get_user_identity())
    print(user_identity)

    # revoke no longer used token
    asyncio.get_event_loop().run_until_complete(aconnection.revoke_access_token())


if __name__ == "__main__":
    # This will authenticate Python client (receive authorization token from Mesh),
    # then send gRPC request that requires authorization (e.g.: GetUserIdentity)
    # and print the result. If your user name info is printed, you have successfully
    # communicated with the server.
    #
    # This requires Mesh server to be running with enabled TLS and Kerberos options.

    address, port, root_certificate_path = _get_connection_info()
#    main(address, port, root_certificate_path)
