"""
Client library for Volue Energy's Mesh software.
"""

from ._authentication import Authentication
from ._timeseries import Timeseries
from ._timeseries_resource import TimeseriesResource
from ._attribute import (
    AttributeBase,
    LinkRelationAttribute,
    OwnershipRelationAttribute,
    TimeseriesAttribute,
    VersionedLinkRelationAttribute,
)
from ._object import Object
from ._common import (
    AttributesFilter,
    LinkRelationVersion,
    LogMessage,
    RatingCurveSegment,
    RatingCurveVersion,
    UserIdentity,
    VersionInfo,
    XyCurve,
    XySet,
)
from ._connection import Connection

__title__ = "volue.mesh"
__author__ = "Volue AS"

__all__ = [
    "Authentication",
    "Connection",
    "AttributeBase",
    "LinkRelationAttribute",
    "LogMessage",
    "OwnershipRelationAttribute",
    "TimeseriesAttribute",
    "VersionedLinkRelationAttribute",
    "Object",
    "Timeseries",
    "TimeseriesResource",
    "AttributesFilter",
    "UserIdentity",
    "VersionInfo",
    "XyCurve",
    "XySet",
    "RatingCurveSegment",
    "RatingCurveVersion",
    "LinkRelationVersion",
]
