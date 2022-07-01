"""
Client library for Volue Energy's Mesh software.
"""

from ._authentication import Authentication
from ._timeseries import Timeseries
from ._timeseries_resource import TimeseriesResource
from ._attribute import AttributeBase, TimeseriesAttribute
from ._object import Object
from ._common import AttributesFilter, UserIdentity, VersionInfo, MeshObjectId, XyCurve, XySet
from ._credentials import Credentials
from ._connection import Connection
from .tests import *
from .examples import *

__title__ = 'volue.mesh'
__author__ = 'Volue AS'

__all__ = [
    'Authentication',
    'Credentials',
    'Connection',
    'AttributeBase',
    'TimeseriesAttribute',
    'Object',
    'Timeseries',
    'TimeseriesResource',
    'AttributesFilter',
    'UserIdentity',
    'VersionInfo',
    'MeshObjectId',
    'XyCurve',
    'XySet'
]
