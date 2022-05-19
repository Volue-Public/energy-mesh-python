"""
Functionality for working with Mesh objects.
"""

from dataclasses import dataclass, field
from typing import Dict, Type
import uuid

from volue.mesh._attribute import AttributeBase, _from_proto_attribute
from volue.mesh._common import _from_proto_guid
from volue.mesh.proto.core.v1alpha import core_pb2


@dataclass
class Object:
    """Represents a Mesh Object.

    Mesh Object is an instance of Object Definition in the Mesh Model.
    """

    id: uuid = None
    path: str = None
    name: str = None
    type_name: str = None
    owner_id: uuid = None
    owner_path: str = None
    attributes: Dict[str, Type[AttributeBase]] = field(default_factory=dict)

    @classmethod
    def _from_proto_object(cls, proto_object: core_pb2.Object):
        """Create an `Object` from protobuf Mesh Object.

        Args:
            proto_object (core_pb2.Object): protobuf Object returned from the gRPC methods
        """
        object = cls()
        object.id = _from_proto_guid(proto_object.id)
        object.path = proto_object.path
        object.name = proto_object.name
        object.type_name = proto_object.type_name
        object.owner_id = _from_proto_guid(proto_object.owner_id.id)
        object.owner_path = proto_object.owner_id.path

        # no particular order of attributes and objects returned from Mesh is guaranteed
        # sort attributes by name
        for proto_attribute in sorted(
            proto_object.attributes, key=lambda attribute: attribute.name.lower()):
            object.attributes[proto_attribute.name] = _from_proto_attribute(proto_attribute)

        return object
