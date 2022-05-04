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
    def search_for_objects(
            self,
            query: str,
            start_object_id: Optional[uuid.UUID] = None,
            start_object_path: Optional[str] = None,
            full_attribute_info: Optional[bool] = False,
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
    def get_object(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path:  Optional[str] = None,
            full_attribute_info:  Optional[bool] = False,
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

    def _prepare_search_for_objects_request(
            self,
            query: str,
            start_object_path: str,
            start_object_id: uuid.UUID,
            full_attribute_info: bool,
            attributes_filter: AttributesFilter) -> core_pb2.SearchObjectsRequest:
        """Create a gRPC `SearchObjectsRequest`"""

        try:
            start_object_id = _to_proto_mesh_id(start_object_path, start_object_id)
        except ValueError as e:
            raise ValueError("invalid start object") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.SearchObjectsRequest(
                    session_id=_to_proto_guid(self.session_id),
                    start_object_id=start_object_id,
                    attributes_masks=_to_proto_attribute_masks(attributes_filter),
                    attribute_view=attribute_view,
                    query=query
                )
        return request

    def _prepare_get_object_request(
            self,
            object_path: str,
            object_id: uuid.UUID,
            full_attribute_info: bool,
            attributes_filter: AttributesFilter) -> core_pb2.SearchObjectsRequest:
        """Create a gRPC `GetObjectRequest`"""

        try:
            object_id = _to_proto_mesh_id(object_path, object_id)
        except ValueError as e:
            raise ValueError("invalid object") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.GetObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=object_id,
                    attributes_masks=_to_proto_attribute_masks(attributes_filter),
                    attribute_view=attribute_view,
                )
        return request

