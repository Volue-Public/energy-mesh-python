import asyncio

import helpers
import volue.mesh.aio
from volue import mesh


def sync_auth(address, tls_root_pem_cert, service_principal, user_principal):
    print("Synchronous authentication example: ")

    # Providing `root_certificates` is optional. If set to `None` root
    # certificates will be retrieved from a default location chosen by the gRPC
    # runtime.
    connection = mesh.Connection.with_kerberos(
        address, tls_root_pem_cert, service_principal, user_principal
    )

    user_identity = connection.get_user_identity()
    print(user_identity)

    # revoke no longer used token
    connection.revoke_access_token()


async def async_auth(address, tls_root_pem_cert, service_principal, user_principal):
    print("Asynchronous authentication example:")

    # Providing `root_certificates` is optional. If set to `None` root
    # certificates will be retrieved from a default location chosen by the gRPC
    # runtime.
    connection = mesh.aio.Connection.with_kerberos(
        address, tls_root_pem_cert, service_principal, user_principal
    )

    user_identity = await connection.get_user_identity()
    print(user_identity)

    # revoke no longer used token
    await connection.revoke_access_token()


def main(address, tls_root_pem_cert):
    """Showing how to authorize to gRPC Mesh server."""

    # If Mesh gRPC server is running as a service user,
    # for example LocalSystem, NetworkService or a user account
    # with a registered service principal name then it is enough
    # to provide hostname as service principal, e.g.:
    #   'HOST/hostname.companyad.company.com'
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
    service_principal = "HOST/hostname.companyad.company.com"
    user_principal = None

    sync_auth(address, tls_root_pem_cert, service_principal, user_principal)
    asyncio.run(
        async_auth(address, tls_root_pem_cert, service_principal, user_principal)
    )


if __name__ == "__main__":
    # This will authenticate Python client (receive authorization token from Mesh),
    # then send gRPC request that requires authorization (e.g.: GetUserIdentity)
    # and print the result. If your user name info is printed, you have successfully
    # communicated with the server.
    #
    # This requires Mesh server to be running with enabled TLS and Kerberos options.

    address, tls_root_pem_cert = helpers.get_connection_info()
#    main(address, tls_root_pem_cert)
