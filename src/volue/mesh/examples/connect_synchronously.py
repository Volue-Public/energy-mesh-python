import helpers

from volue.mesh import Connection


def get_version(connection):
    """Showing how to send get the server version."""
    print("1. Requesting server version")
    version = connection.get_version()
    print(f"2. Server version is {version.version}")


def start_and_end_session(session):
    """Showing how to start and end a session."""
    print("A. Starting session")
    session.open()
    print("B. Ending session")
    session.close()


def main(address, tls_root_pem_cert):
    """Showing how to connect to a server and run two tasks sequentially."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    get_version(connection)
    start_and_end_session(connection.create_session())


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
    print("Done")

# Outputs:
# 1. Requesting server version
# 2. Server version is 1.12.5.0-dev
# A. Starting session
# B. Ending session
# Done
