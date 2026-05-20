import sys

from volue.mesh import Connection


def get_connection_info():
    """Helper function to set hand over connection info to examples."""
    address = "localhost:50051"
    tls_root_pem_cert = ""

    if len(sys.argv) > 1:
        address = sys.argv[1]
    if len(sys.argv) > 2:
        root_certificate_path = sys.argv[2]
        if root_certificate_path:
            with open(root_certificate_path, "rb") as file:
                # In case multiple root certificates are needed, e.g.:
                # the same client accesses different Mesh servers (with different root certs)
                # Just combine into single file the root certificates, like:
                # -----BEGIN CERTIFICATE-----
                # ...(first certificate)...
                # -----END CERTIFICATE-----
                # -----BEGIN CERTIFICATE-----
                # ..(second certificate)..
                # -----END CERTIFICATE-----
                tls_root_pem_cert = file.read()

    return address, tls_root_pem_cert


def main(address, tls_root_pem_cert):
    """Showing the quickest way to get started."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    # Which version is the server running
    version_info = connection.get_version()
    print(f"Connected to {version_info.name} {version_info.version}")

    # Create a remote session on the Volue Mesh server
    with connection.create_session() as session:
        print("You have now an open session and can request time series")
        # Do some work with the session, e.g. read time series points, write time series points, etc.
        # The session will be automatically closed when the block is exited.


if __name__ == "__main__":
    address, tls_root_pem_cert = get_connection_info()
    main(address, tls_root_pem_cert)
