"""
Reflects the setup of the Volue Mesh server integration tests and examples should be run against.
"""

from dataclasses import dataclass


@dataclass
class ServerConfig:
    ADDRESS: str = 'localhost'
    PORT: int = 50051
    ROOT_CERTIFICATE_PATH: str = ''
    KERBEROS_SERVICE_PRINCIPAL_NAME: str = 'HOST/example.companyad.company.com'

# change to path with your certificate
VALID_ROOT_CERTIFICATE_PATH: str = 'C:\\certs\\server_self_signed_certificate.crt'

DefaultServerConfig: ServerConfig = ServerConfig()
