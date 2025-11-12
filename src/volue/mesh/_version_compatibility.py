import re
from dataclasses import dataclass
from importlib import metadata
from typing import Optional

# Minimum supported Mesh server version
MINIMUM_SERVER_VERSION_STR = "2.18.0"

# Name of the metadata key used to transmit client version information
CLIENT_VERSION_METADATA_KEY = "x-volue-mesh-client-version"


def get_client_version() -> str:
    try:
        # Get the package version from the environment
        return metadata.version("volue.mesh")
    except:
        # Fallback to a version number which shouldn't
        # interrupt using the SDK in case of problems.
        # Most of the time the package is installed via
        # `pip install` or `poetry install`. For these
        #  cases, using the importlib metadata should be fine.
        return "99.99.99"


CLIENT_VERSION = get_client_version()


def get_client_version_metadata_key() -> str:
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
        return ParsedVersion(
            major=int(r.group(1)), minor=int(r.group(2)), patch=int(r.group(3))
        )
    else:
        return None


MINIMUM_SERVER_VERSION = to_parsed_version(MINIMUM_SERVER_VERSION_STR)


def get_min_server_version() -> Optional[ParsedVersion]:
    return MINIMUM_SERVER_VERSION


def get_compatibility_check_metadata() -> list[tuple[str, str]]:
    return [(get_client_version_metadata_key(), get_client_version())]
