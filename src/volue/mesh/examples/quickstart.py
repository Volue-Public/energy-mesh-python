import helpers

from volue.mesh import Connection


def main(address, tls_root_pem_cert):
    """Showing the quickest way to get started."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    # Which version is the server running
    version_info = connection.get_version()
    print(f"Connected to {version_info.name} {version_info.version}")

    # Create a remote session on the Volue Mesh server
    session = connection.create_session()
    session.open()
    print("You have now an open session and can request time series")

    # Close the remote session
    session.close()


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
