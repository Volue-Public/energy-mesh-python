import grpc


class Credentials:
    """ Security details for connecting to a mesh server.
    """

    def __init__(self, root_certificate_path: str):
        with open(root_certificate_path, 'rb') as file:
            # In case multiple root certificates are needed, e.g.:
            # the same client accesses different Mesh servers (with different root certs)
            # Just combine into single file the root certificates, like:
            #-----BEGIN CERTIFICATE-----
            # ...(first certificate)...
            #-----END CERTIFICATE-----
            #-----BEGIN CERTIFICATE-----
            # ..(second certificate)..
            #-----END CERTIFICATE-----
            self.root_certificate_path = file.read()

        # Mesh server does not require clients to be authenticated via TLS mechanism
        self.channel_creds = grpc.ssl_channel_credentials(
            root_certificates=self.root_certificate_path
        )
