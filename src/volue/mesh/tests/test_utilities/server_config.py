"""
Reflects the setup of the Volue Mesh server integration tests and examples should be run against.
"""

from dataclasses import dataclass


@dataclass
class ServerConfig:
    ADDRESS: str = 'localhost'
    PORT: int = 50051
    SECURE_CONNECTION: bool = False


global DefaultServerConfig
DefaultServerConfig: ServerConfig = ServerConfig()
