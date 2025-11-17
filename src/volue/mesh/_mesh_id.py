"""
Mesh ID helper functions.
"""

import uuid
from typing import Union

from volue.mesh import AttributeBase, Object
from volue.mesh._common import _to_proto_guid
from volue.mesh.proto import type


def _to_proto_attribute_mesh_id(
    target: Union[uuid.UUID, str, AttributeBase],
) -> type.resources_pb2.MeshId:
    """
    Accepts attribute identifiers (path and ID) and attribute instance as
    input.
    """
    if not isinstance(target, (uuid.UUID, str, AttributeBase)):
        raise TypeError(
            "need to provide either path (as str), ID (as uuid.UUID) or attribute instance"
        )

    return _to_proto_mesh_id(target)


def _to_proto_attribute_definition_mesh_id(
    target: Union[uuid.UUID, str, AttributeBase.AttributeBaseDefinition],
) -> type.resources_pb2.MeshId:
    """
    Accepts attribute definition identifiers (path and ID) and attribute definition instance as
    input.
    """
    if not isinstance(target, (uuid.UUID, str, AttributeBase.AttributeBaseDefinition)):
        raise TypeError(
            "need to provide either path (as str), ID (as uuid.UUID) or attribute definition instance"
        )

    return _to_proto_mesh_id(target)


def _to_proto_object_mesh_id(
    target: Union[uuid.UUID, str, Object],
) -> type.resources_pb2.MeshId:
    """
    Accepts object identifiers (path and ID) and object instance as input.
    """
    if not isinstance(target, (uuid.UUID, str, Object)):
        raise TypeError(
            "need to provide either path (as str), ID (as uuid.UUID) or Mesh object instance"
        )

    return _to_proto_mesh_id(target)


def _to_proto_read_timeseries_mesh_id(
    target: Union[uuid.UUID, str, int, AttributeBase],
) -> type.resources_pb2.MeshId:
    """
    Accepts identifiers for reading time series:
    path, ID, time series key and time series attribute instance as input.
    """
    if not isinstance(target, (uuid.UUID, str, int, AttributeBase)):
        raise TypeError(
            "need to provide either path (as str), ID (as uuid.UUID), time series key or time series attribute instance"
        )

    return _to_proto_mesh_id(target)


def _to_proto_calculation_target_mesh_id(
    target: Union[uuid.UUID, str, int, AttributeBase, Object],
) -> type.resources_pb2.MeshId:
    """
    Accepts identifiers for calculation target (`relative_to` in gRPC):
    path, ID, time series key and attribute or object instance as input.
    """
    if not isinstance(target, (uuid.UUID, str, int, AttributeBase, Object)):
        raise TypeError(
            "need to provide either path (as str), ID (as uuid.UUID), time series key (as int), Mesh object or attribute instance"
        )

    return _to_proto_mesh_id(target)


def _to_proto_mesh_id(
    target: Union[uuid.UUID, str, int, AttributeBase, Object],
) -> type.resources_pb2.MeshId:
    """Accepts path, ID and time series key as input."""
    proto_mesh_id = type.resources_pb2.MeshId()

    if isinstance(
        target, (AttributeBase, Object, AttributeBase.AttributeBaseDefinition)
    ):
        proto_mesh_id.id.CopyFrom(_to_proto_guid(target.id))
        proto_mesh_id.path = target.path
    elif isinstance(target, uuid.UUID):
        proto_mesh_id.id.CopyFrom(_to_proto_guid(target))
    elif isinstance(target, str):
        proto_mesh_id.path = target
    elif isinstance(target, int):
        proto_mesh_id.timeseries_key = target
    else:
        raise TypeError("invalid target type")

    return proto_mesh_id
