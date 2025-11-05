"""
Client version information for Mesh.
"""

from dataclasses import dataclass
import re
from typing import Optional

# Current client version (from pyproject.toml)
CLIENT_VERSION = "1.14.0-dev"

# Minimum supported Mesh server version
MINIMUM_SERVER_VERSION_STR = "2.18.0"

# Name of the metadata key used to transmit client version information
CLIENT_VERSION_METADATA_KEY = "x-volue-mesh-client-version"

def get_client_version() -> str:
    return CLIENT_VERSION

def get_min_server_version() -> str:
    return MINIMUM_SERVER_VERSION

def get_client_version_header_name() -> str:
    return CLIENT_VERSION_METADATA_KEY

# `order=True` generates the comparison operators
@dataclass(order=True)
class ParsedVersion:
    major: int = 0
    minor: int = 0
    patch: int = 0

def to_parsed_version(version: str) -> Optional[ParsedVersion]:
    r = re.match(r"^(\d+)\.(\d+)\.(\d+)(\+\d+)?$", version)
    if r is not None:
        # group with index 0 contains the whole matched string
        return ParsedVersion(major=r.group(1), minor=r.group(2), patch=r.group(3))
    else:
        return None
    

MINIMUM_SERVER_VERSION = to_parsed_version(MINIMUM_SERVER_VERSION_STR)
