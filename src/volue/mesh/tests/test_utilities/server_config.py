"""
Reflects the setup of the Volue Mesh server integration tests and examples should be run against.
"""

from dataclasses import dataclass


@dataclass
class ServerConfig:
    ADDRESS: str = 'localhost'
    PORT: int = 50051
    # PEM-encoded root certificate(s) as a byte string.
    ROOT_PEM_CERTIFICATE: str = ''
    KERBEROS_SERVICE_PRINCIPAL_NAME: str = 'HOST/example.companyad.company.com'


DefaultServerConfig: ServerConfig = ServerConfig()
