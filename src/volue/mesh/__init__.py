"""
Client library for Volue Energy's Mesh software.
"""

from ._authentication import Authentication
from ._timeseries import Timeseries
from ._common import *
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
    'Timeseries',
    'copydoc'
]

