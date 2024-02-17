import sys


def get_connection_info():
    """Helper function to set hand over connection info to examples."""
    address = "localhost:50051"
    root_pem_certificate = ""

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
                root_pem_certificate = file.read()

    hostname, port = address.split(":")
    return hostname, port, root_pem_certificate
