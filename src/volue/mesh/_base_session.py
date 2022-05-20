import abc
from typing import List, Optional, Type, Tuple
import uuid
from datetime import datetime

from google import protobuf

from ._attribute import AttributeBase, SIMPLE_TYPE_OR_COLLECTION, SIMPLE_TYPE
from ._common import AttributesFilter, _to_proto_attribute_masks, _to_proto_guid, \
    _to_proto_mesh_id, _datetime_to_timestamp_pb2
from ._object import Object
from .proto.core.v1alpha import core_pb2, core_pb2_grpc


class Session(abc.ABC):
    """Represents a session to a Mesh server."""

    def __init__(
            self,
            mesh_service: core_pb2_grpc.MeshServiceStub,
            session_id: Optional[uuid.UUID] = None):
        """
        Initialize a session object for working with the Mesh server.

        Args:
            mesh_service: gRPC generated Mesh service to communicate with
                the :doc:`Mesh server <mesh_server>`.
            session_id: ID of the session you are (or want to be) connected to.
        """
        self.session_id: uuid = session_id
        self.mesh_service: core_pb2_grpc.MeshServiceStub = mesh_service

    @abc.abstractmethod
    def get_object(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path:  Optional[str] = None,
            full_attribute_info:  bool = False,
            attributes_filter: Optional[AttributesFilter] = None) -> Object:
        """
        Request information associated with a Mesh object from the Mesh object model.
        Specify either `object_id` or `object_path` to a Mesh object.

        Args:
            object_id: Universal Unique Identifier of the Mesh object.
            object_path: Path in the :ref:`Mesh object model <mesh object model>`
                of the Mesh object.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object will be returned, otherwise only name,
                path, ID and value(s).
            attributes_filter: Filtering criteria for what attributes owned by
                object(s) should be returned. By default all attributes are returned.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def search_for_objects(
            self,
            query: str,
            start_object_id: Optional[uuid.UUID] = None,
            start_object_path: Optional[str] = None,
            full_attribute_info: bool = False,
            attributes_filter: Optional[AttributesFilter] = None) -> List[Object]:
        """
        Use the :doc:`Mesh search language <mesh_search>` to find Mesh objects
        in the Mesh object model. Specify either `start_object_id` or
        `start_object_path` to an object where the search query should start from.

        Args:
            query: A search formulated using the :doc:`Mesh search language <mesh_search>`.
            start_object_id: Start searching at the object with the 
                Universal Unique Identifier for Mesh objects.
            start_object_path: Start searching at the path in the
                :ref:`Mesh object model <mesh object model>`.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object(s) will be returned, otherwise only name,
                path, ID and value(s).
            attributes_filter: Filtering criteria for what attributes owned by
                object(s) should be returned. By default all attributes are returned.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def create_object(
            self,
            name: str,
            owner_attribute_id: Optional[uuid.UUID] = None,
            owner_attribute_path: Optional[str] = None) -> Object:
        """
        Create new Mesh object in the Mesh object model.
        Owner of the new object must be a relationship attribute of Object Collection type.
        E.g.: for `SomePowerPlant1` object with path:
        - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1

        Owner will be the `ThermalPowerToPlantRef` attribute.

        Args:
            name: Name for the new object to create.
            owner_attribute_id: Universal Unique Identifier of the owner which
                is a relationship attribute of Object Collection type.
            owner_attribute_path: Path in the :ref:`Mesh object model <mesh object model>`
                of the owner which is a relationship attribute of Object Collection type.

        Returns:
            Created object with all attributes (no mask applied) and basic
            information: name, path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def update_object(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path: Optional[str] = None,
            new_name: Optional[str] = None,
            new_owner_attribute_id: Optional[uuid.UUID] = None,
            new_owner_attribute_path: Optional[str] = None) -> None:
        """
        Update an existing Mesh object in the Mesh object model.
        New owner of the object must be a relationship attribute of Object Collection type.
        E.g.: for `SomePowerPlant1` object with path:
        - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1

        Args:
            object_id: Universal Unique Identifier of the Mesh object to be updated.
            object_path: Path in the :ref:`Mesh object model <mesh object model>`
                of the Mesh object to be updated.
            new_name: New name for the object.
            new_owner_attribute_id: Universal Unique Identifier of the new owner which
                is a relationship attribute of Object Collection type.
            new_owner_attribute_path: Path in the :ref:`Mesh object model <mesh object model>`
                of the new owner which is a relationship attribute of Object Collection type.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def delete_object(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path: Optional[str] = None,
            recursive_delete: bool = False) -> None:
        """
        Delete an existing Mesh object in the Mesh object model.

        Args:
            object_id: Universal Unique Identifier of the object to be deleted.
            object_path: Path in the :ref:`Mesh object model <mesh object model>`
                of the object to be deleted.
            recursive_delete: If set then all child objects
                (owned by the object to be deleted) in the model will also be deleted.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def get_attribute(
            self,
            attribute_id: Optional[uuid.UUID] = None,
            attribute_path: Optional[str] = None,
            full_attribute_info: bool = False) -> Type[AttributeBase]:
        """
        Retrieve an existing attribute from the Mesh object model.

        Args:
            attribute_id: Universal Unique Identifier of the attribute to be retrieved.
            attribute_path: Path in the :ref:`Mesh object model <mesh object model>`
                of the attribute to be retrieved.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attribute will be returned, otherwise only name, path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def search_for_attributes(
            self,
            query: str,
            start_object_id: Optional[uuid.UUID] = None,
            start_object_path: Optional[str] = None,
            full_attribute_info: bool = False) -> List[Type[AttributeBase]]:
        """
        Use the :doc:`Mesh search language <mesh_search>` to find Mesh attributes
        in the Mesh object model. Specify either `start_object_id` or
        `start_object_path` to an object where the search query should start from.

        Args:
            query: A search formulated using the :doc:`Mesh search language <mesh_search>`.
            start_object_id: Start searching at the object with the 
                Universal Unique Identifier for Mesh objects.
            start_object_path: Start searching at the path in the
                :ref:`Mesh object model <mesh object model>`.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object(s) will be returned, otherwise only name,
                path, ID and value(s).
        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def update_simple_attribute(
            self,
            value: SIMPLE_TYPE_OR_COLLECTION,
            attribute_id: Optional[uuid.UUID] = None,
            attribute_path: Optional[str] = None) -> None:
        """
        Update an existing Mesh attribute's value in the Mesh object model.

        Args:
            value: New simple attribute value. It can be one of following simple types:
                bool, float, int, str, datetime or a list of simple types.
            attribute_id: Universal Unique Identifier of the Mesh attribute to be updated.
            attribute_path: Path in the :ref:`Mesh object model <mesh object model>`
                of the Mesh attribute which value is to be updated.
        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """


    def _prepare_get_object_request(
            self,
            object_id: uuid.UUID,
            object_path: str,
            full_attribute_info: bool,
            attributes_filter: AttributesFilter) -> core_pb2.GetObjectRequest:
        """Create a gRPC `GetObjectRequest`"""

        try:
            object_mesh_id = _to_proto_mesh_id(id=object_id, path=object_path)
        except ValueError as e:
            raise ValueError("invalid object") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.GetObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=object_mesh_id,
                    attributes_masks=_to_proto_attribute_masks(attributes_filter),
                    attribute_view=attribute_view,
                )
        return request

    def _prepare_search_for_objects_request(
            self,
            query: str,
            start_object_id: uuid.UUID,
            start_object_path: str,
            full_attribute_info: bool,
            attributes_filter: AttributesFilter) -> core_pb2.SearchObjectsRequest:
        """Create a gRPC `SearchObjectsRequest`"""

        try:
            start_object_mesh_id = _to_proto_mesh_id(id=start_object_id, path=start_object_path)
        except ValueError as e:
            raise ValueError("invalid start object") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.SearchObjectsRequest(
                    session_id=_to_proto_guid(self.session_id),
                    start_object_id=start_object_mesh_id,
                    attributes_masks=_to_proto_attribute_masks(attributes_filter),
                    attribute_view=attribute_view,
                    query=query
                )
        return request

    def _prepare_create_object_request(
            self,
            name: str,
            owner_attribute_id: uuid.UUID,
            owner_attribute_path: str) -> core_pb2.CreateObjectRequest:
        """Create a gRPC `CreateObjectRequest`"""

        try:
            owner_mesh_id = _to_proto_mesh_id(id=owner_attribute_id, path=owner_attribute_path)
        except ValueError as e:
            raise ValueError("invalid owner") from e

        request = core_pb2.CreateObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    owner_id=owner_mesh_id,
                    name=name
                )
        return request

    def _prepare_update_object_request(
            self,
            object_id: uuid.UUID,
            object_path: str,
            new_name: str,
            new_owner_attribute_id: uuid.UUID,
            new_owner_attribute_path:str) -> core_pb2.UpdateObjectRequest:
        """Create a gRPC `UpdateObjectRequest`"""

        try:
            object_mesh_id = _to_proto_mesh_id(id=object_id, path=object_path)
        except ValueError as e:
            raise ValueError("invalid object to update") from e

        request = core_pb2.UpdateObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=object_mesh_id
                )

        fields_to_update = []

        # providing new owner is optional
        if new_owner_attribute_id is not None or new_owner_attribute_path is not None:
            try:
                new_owner_mesh_id = _to_proto_mesh_id(
                    id=new_owner_attribute_id, path=new_owner_attribute_path)
            except ValueError as e:
                raise ValueError("invalid new owner") from e
            
            request.new_owner_id.CopyFrom(new_owner_mesh_id)
            fields_to_update.append("new_owner_id")

        # providing new name is optional
        if new_name is not None:
            request.new_name = new_name
            fields_to_update.append("new_name")

        request.field_mask.CopyFrom(protobuf.field_mask_pb2.FieldMask(paths=fields_to_update))
        return request

    def _prepare_delete_object_request(
            self,
            object_id: uuid.UUID,
            object_path: str,
            recursive_delete: bool) -> core_pb2.DeleteObjectRequest:
        """Create a gRPC `DeleteObjectRequest`"""

        try:
            object_mesh_id = _to_proto_mesh_id(id=object_id, path=object_path)
        except ValueError as e:
            raise ValueError("invalid object") from e

        request = core_pb2.DeleteObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=object_mesh_id,
                    recursive_delete=recursive_delete
                )
        return request

    def _prepare_get_attribute_request(
        self,
        attribute_id: uuid.UUID,
        attribute_path: str,
        full_attribute_info: bool) -> core_pb2.GetAttributeRequest:

        try:
            attribute_mesh_id = _to_proto_mesh_id(id=attribute_id, path=attribute_path)
        except ValueError as e:
            raise ValueError("invalid attribute") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.GetAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_id=attribute_mesh_id,
            attribute_view=attribute_view
        )

        return request

    def _prepare_search_attributes_request(
        self,
        start_object_id: uuid.UUID,
        start_object_path: str,
        query: str,
        full_attribute_info: bool) -> core_pb2.SearchAttributesRequest:

        try:
            start_object_mesh_id = _to_proto_mesh_id(id=start_object_id, path=start_object_path)
        except ValueError as e:
            raise ValueError("invalid start object") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.SearchAttributesRequest(
            session_id=_to_proto_guid(self.session_id),
            start_object_id=start_object_mesh_id,
            query=query,
            attribute_view=attribute_view
        )

        return request

    def _prepare_update_attribute_request(
        self,
        attribute_id: uuid.UUID,
        attriubte_path: str,
        new_singular_value: core_pb2.AttributeValue,
        new_collection_values: List[core_pb2.AttributeValue]
    ) -> core_pb2.UpdateAttributeResponse:

        try:
            attribute_mesh_id = _to_proto_mesh_id(id=attribute_id, path=attriubte_path)
        except ValueError as e:
            raise ValueError("invalid attribute to update") from e

        request = core_pb2.UpdateAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_id=attribute_mesh_id
        )

        fields_to_update = []
        if new_singular_value is not None:
            fields_to_update.append("value")
            request.new_singular_value.CopyFrom(new_singular_value)

        if new_collection_values is not None:
            for value in new_collection_values:
                request.new_collection_values.append(value)
            fields_to_update.append("value")

        request.field_mask.CopyFrom(protobuf.field_mask_pb2.FieldMask(paths=fields_to_update))
        return request

    def _to_proto_singular_attribute_value(
        self,
        v: SIMPLE_TYPE
    ) -> core_pb2.AttributeValue:
    
        att_value = core_pb2.AttributeValue()
        if type(v) is int:
            att_value.int_value = v
        elif type(v) is float:
            att_value.double_value = v
        elif type(v) is bool:
            att_value.boolean_value = v
        elif type(v) is str:
            att_value.string_value = v
        elif type(v) is datetime:
            att_value.utc_time_value.CopyFrom(_datetime_to_timestamp_pb2(v))
        else:
            raise RuntimeError("Not supported value type. Supported simple types are: boolean, float, int, str, datetime.")

        return att_value


    def _to_update_attribute_request_values(
        self,
        value: SIMPLE_TYPE_OR_COLLECTION
    ) -> Tuple[core_pb2.AttributeValue, List[core_pb2.AttributeValue]]:
            """
                Convert value supplied by the user to singular value/collection values
                expected by the protobuf request
            """
            new_singular_value = None
            new_collection_values = None
            if type(value) is list:
                new_collection_values = []
                for v in value:
                    att_value = self._to_proto_singular_attribute_value(v)
                    new_collection_values.append(att_value)
            else:
                new_singular_value = self._to_proto_singular_attribute_value(value)       

            return (new_singular_value, new_collection_values)
