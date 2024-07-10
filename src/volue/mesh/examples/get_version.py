import asyncio

import helpers

import volue.mesh.aio
from volue import mesh


def sync_get_version(address, tls_root_pem_cert):
    print("Synchronous get version:")

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = mesh.Connection.with_tls(address, tls_root_pem_cert)
    connection = mesh.Connection.insecure(address)

    version_info = connection.get_version()
    print(version_info.version)


async def async_get_version(address, tls_root_pem_cert):
    print("Asynchronous get version:")

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = mesh.aio.Connection.with_tls(address, tls_root_pem_cert)
    connection = mesh.aio.Connection.insecure(address)

    version_info = await connection.get_version()
    print(version_info.version)


if __name__ == "__main__":
    # This will request and print version info from the mesh server.
    # If some sensible version info is printed, you have successfully
    # communicated with the server.
    address, tls_root_pem_cert = helpers.get_connection_info()
    sync_get_version(address, tls_root_pem_cert)
    asyncio.run(async_get_version(address, tls_root_pem_cert))
