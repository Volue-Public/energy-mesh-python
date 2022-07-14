"""
Handling security details.
"""

import grpc


class Credentials:
    """
    Security details for connecting to a Mesh server.
    """

    def __init__(self, root_pem_certificate: str):
        """
        Args:
            root_pem_certificate: PEM-encoded root certificate(s) as a byte string. If this argument is set then a secured connection will be created, otherwise it will be an insecure connection.
        """
        # Mesh server does not require clients to be authenticated via TLS mechanism
        self.channel_creds = grpc.ssl_channel_credentials(
            root_certificates=root_pem_certificate
        )
