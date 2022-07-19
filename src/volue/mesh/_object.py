"""
Functionality for working with Mesh objects.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict

from volue.mesh._attribute import AttributeBase, _from_proto_attribute
from volue.mesh._common import _from_proto_guid
from volue.mesh.proto.core.v1alpha import core_pb2


@dataclass
class Object:
    """Represents a Mesh Object.

    Mesh Object is an instance of Object Definition in the Mesh Model.
    Refer to documentation for more details:
    :ref:`Mesh object <mesh_object>`.
    """

    id: uuid.UUID
    path: str
    name: str
    type_name: str
    owner_id: uuid.UUID
    owner_path: str
    attributes: Dict[str, AttributeBase] = field(default_factory=dict)

    @classmethod
    def _from_proto_object(cls, proto_object: core_pb2.Object):
        """Create an `Object` from protobuf Mesh Object.

        Args:
            proto_object: Protobuf Object returned from the gRPC methods.
        """
        object = cls(
            id=_from_proto_guid(proto_object.id),
            path=proto_object.path,
            name=proto_object.name,
            type_name=proto_object.type_name,
            owner_id=_from_proto_guid(proto_object.owner_id.id),
            owner_path=proto_object.owner_id.path,
        )

        # no particular order of attributes and objects returned from Mesh is guaranteed
        # sort attributes by name
        for proto_attribute in sorted(
            proto_object.attributes, key=lambda attribute: attribute.name.lower()
        ):
            object.attributes[proto_attribute.name] = _from_proto_attribute(
                proto_attribute
            )

        return object
