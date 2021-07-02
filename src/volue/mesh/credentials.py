import os
import grpc

class Credentials:
    def __init__(self):
        self.server_cert_path = os.path.join(
            os.path.dirname(__file__),
            'cert/server_self_signed_crt.pem')

        with open(self.server_cert_path, 'rb') as file:
            self.server_cert = file.read()

        self.channel_creds = grpc.ssl_channel_credentials(
            root_certificates=self.server_cert)

