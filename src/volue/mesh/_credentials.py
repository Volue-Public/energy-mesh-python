"""
Handling security details.
"""

import grpc


class Credentials:
    """ Security details for connecting to a mesh server.
    """

    def __init__(self, root_pem_certificate: str):
        # Mesh server does not require clients to be authenticated via TLS mechanism
        self.channel_creds = grpc.ssl_channel_credentials(
            root_certificates=root_pem_certificate
        )
