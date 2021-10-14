"""
Client library for Volue Energy's Mesh software.
"""

from ._timeserie import Timeseries
from ._common import uuid_to_guid, guid_to_uuid, dot_net_ticks_to_protobuf_timestamp, eagle_wind, TimeseriesTestdata
from ._credentials import Credentials
from ._connection import Connection
from .tests import *
from .examples import *

__title__ = 'volue.mesh'
__author__ = 'Volue AS'
__version__ = "0.1.0"

__all__ = [
    'Connection',
    'uuid_to_guid',
    'guid_to_uuid',
    'dot_net_ticks_to_protobuf_timestamp',
    'TimeseriesTestdata',
    'eagle_wind',
    'Timeseries',
    'Credentials',
    'tests',
    'examples'
]