import abc
from typing import List, Optional
import uuid

from ._common import AttributesFilter, _to_proto_attribute_masks, _to_proto_guid, _to_proto_mesh_id
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
            mesh_service (core_pb2_grpc.MeshServiceStub): the gRPC generated Mesh service to communicate with the :doc:`Mesh server <mesh_server>`
            session_id (uuid.UUID): the id of the session you are (or want to be) connected to
        """
        self.session_id: uuid = session_id
        self.mesh_service: core_pb2_grpc.MeshServiceStub = mesh_service


    @abc.abstractmethod
    def get_object(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path:  Optional[str] = None,
            full_attribute_info:  bool = False,
            attributes_filter: Optional[AttributesFilter] = None) -> core_pb2.Object:
        """
        Request information associated with a Mesh object from the Mesh object model.

        Args:
            object_id (uuid.UUID): Universal Unique Identifier of the Mesh object
            object_path (str): Path in the :ref:`Mesh object model <mesh object model>` of the Mesh object

        Note:
            Specify either `uuid_id` or `path` to a Mesh object.

        Raises:
            grpc.RpcError:  Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def search_for_objects(
            self,
            query: str,
            start_object_id: Optional[uuid.UUID] = None,
            start_object_path: Optional[str] = None,
            full_attribute_info: bool = False,
            attributes_filter: Optional[AttributesFilter] = None) -> List[core_pb2.Object]:
        """
        Use the :doc:`Mesh search language <mesh_search>` to find Mesh objects in the Mesh object model.

        Args:
            query (str): A search formulated using the :doc:`Mesh search language <mesh_search>`
            start_object_id (uuid.UUID): Start searching at the object with the  Universal Unique Identifier for Mesh objects
            start_object_path (str): Start searching at the path in the :ref:`Mesh object model <mesh object model>`
            full_attribute_info (bool): If set then all information (e.g. description, value type, etc.) of attributes owned by object(s) will be returned, otherwise only name, path, id and value(s)
            attributes_filter (AttributesFilter): Filtering criteria for what attributes owned by object(s) should be returned. By default all attributes are returned.

        Note:
            Specify a query using mesh query language and start object to start the search from,
            using either a path or an ID.

        Raises:
            grpc.RpcError:  Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def create_object(
            self,
            name: str,
            owner_attribute_id: Optional[uuid.UUID] = None,
            owner_attribute_path: Optional[str] = None) -> List[core_pb2.Object]:
        """
        Create new Mesh object in the Mesh object model. Owner of the new object must be a relationship attribute of Object Collection type.
        E.g.: for `SomePowerPlant1` object with path:
        - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1

        Owner will be the `ThermalPowerToPlantRef` attribute.

        Args:
            name (str): Name for the new object to create.
            owner_attribute_id (uuid.UUID): Universal Unique Identifier of the owner which is a relationship attribute of Object Collection type
            owner_attribute_path (str): Path in the :ref:`Mesh object model <mesh object model>` of the owner which is a relationship attribute of Object Collection type

        Raises:
            grpc.RpcError:  Error message raised if the gRPC request could not be completed
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
            object_id (uuid.UUID): Universal Unique Identifier of the object to be deleted
            object_path (str): Path in the :ref:`Mesh object model <mesh object model>` of the object to be deleted
            recursive_delete (bool): If set then all child objects (owned by the object to be deleted) in the model will also be deleted

        Raises:
            grpc.RpcError:  Error message raised if the gRPC request could not be completed
        """

    def _prepare_get_object_request(
            self,
            object_id: uuid.UUID,
            object_path: str,
            full_attribute_info: bool,
            attributes_filter: AttributesFilter) -> core_pb2.SearchObjectsRequest:
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
            owner_attribute_id: Optional[uuid.UUID] = None,
            owner_attribute_path: Optional[str] = None) -> core_pb2.CreateObjectRequest:
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

    def _prepare_delete_object_request(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path: Optional[str] = None,
            recursive_delete: bool = False) -> core_pb2.DeleteObjectRequest:
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
