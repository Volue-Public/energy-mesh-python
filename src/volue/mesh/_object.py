"""
Functionality for working with Mesh objects.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from volue.mesh._attribute import AttributeBase, _from_proto_attribute
from volue.mesh._common import _from_proto_guid
from volue.mesh.proto.model.v1alpha import resources_pb2 as model_resources_pb2


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
    owner_id: Optional[uuid.UUID]
    owner_path: Optional[str]
    attributes: Dict[str, AttributeBase] = field(default_factory=dict)

    @classmethod
    def _from_proto_object(cls, proto_object: model_resources_pb2.Object):
        """Create an `Object` from protobuf Mesh Object.

        Args:
            proto_object: Protobuf Object returned from the gRPC methods.
        """

        owner_id = (
            _from_proto_guid(proto_object.owner_id.id)
            if proto_object.HasField("owner_id")
            else None
        )
        owner_path = (
            proto_object.owner_id.path if proto_object.HasField("owner_id") else None
        )

        object = cls(
            id=_from_proto_guid(proto_object.id),
            path=proto_object.path,
            name=proto_object.name,
            type_name=proto_object.type_name,
            owner_id=owner_id,
            owner_path=owner_path,
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
