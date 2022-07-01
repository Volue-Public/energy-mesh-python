"""
Functionality for asynchronously connecting to a Mesh server and working with its sessions.
"""

import typing
import uuid
from typing import Optional, List, Type, Union
from datetime import datetime

from google import protobuf
import grpc

from volue.mesh import Timeseries, AttributesFilter, UserIdentity, VersionInfo, MeshObjectId, \
    AttributeBase, TimeseriesAttribute, TimeseriesResource, Object
from volue.mesh._attribute import _from_proto_attribute
from volue.mesh._common import (XySet, RatingCurveVersion, _to_proto_guid,
     _from_proto_guid, _to_protobuf_utcinterval, _read_proto_reply,
     _to_proto_timeseries)
from volue.mesh.calc.forecast import ForecastFunctionsAsync
from volue.mesh.calc.history import HistoryFunctionsAsync
from volue.mesh.calc.statistical import StatisticalFunctionsAsync
from volue.mesh.calc.transform import TransformFunctionsAsync
from volue.mesh.proto.core.v1alpha import core_pb2, core_pb2_grpc

from volue.mesh import _base_connection
from volue.mesh import _base_session
from volue.mesh import _attribute


class Connection(_base_connection.Connection):
    class Session(_base_session.Session):
        """
        This class supports the async with statement, because it's an async contextmanager.
        https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers
        https://docs.python.org/3/reference/compound_stmts.html#async-with
        """

        def __init__(
                self,
                mesh_service: core_pb2_grpc.MeshServiceStub,
                session_id: uuid.UUID = None):
            super().__init__(session_id=session_id, mesh_service=mesh_service)

        async def __aenter__(self):
            """
            Used by the 'with' statement to open a session when entering 'with'. |coro|

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            await self.open()
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            """
            Used by the 'with' statement to close a session when exiting 'with'. |coro|

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            await self.close()

        async def open(self):
            reply = await self.mesh_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = _from_proto_guid(reply)
            return reply

        async def close(self) -> None:
            await self.mesh_service.EndSession(_to_proto_guid(self.session_id))
            self.session_id = None

        async def rollback(self) -> None:
            await self.mesh_service.Rollback(_to_proto_guid(self.session_id))

        async def commit(self) -> None:
            await self.mesh_service.Commit(_to_proto_guid(self.session_id))

        async def read_timeseries_points(self,
                                         start_time: datetime,
                                         end_time: datetime,
                                         mesh_object_id: MeshObjectId) -> Timeseries:
            mesh_id = core_pb2.MeshId()
            if mesh_object_id.timskey is not None:
                mesh_id.timeseries_key = mesh_object_id.timskey
            elif mesh_object_id.uuid_id is not None:
                mesh_id.id.CopyFrom(_to_proto_guid(mesh_object_id.uuid_id))
            elif mesh_object_id.full_name is not None:
                mesh_id.path = mesh_object_id.full_name
            else:
                raise TypeError("need to specify either timskey, uuid_id or full_name")

            response = await self.mesh_service.ReadTimeseries(
                core_pb2.ReadTimeseriesRequest(
                    session_id=_to_proto_guid(self.session_id),
                    timeseries_id=mesh_id,
                    interval=_to_protobuf_utcinterval(start_time, end_time)
                ))

            timeseries = _read_proto_reply(response)
            if len(timeseries) != 1:
                raise RuntimeError(
                    f"invalid result from 'read_timeseries_points', expected 1 time series, but got {len(timeseries)}")

            return timeseries[0]

        async def write_timeseries_points(self, timeseries: Timeseries):
            await self.mesh_service.WriteTimeseries(
                core_pb2.WriteTimeseriesRequest(
                    session_id=_to_proto_guid(self.session_id),
                    timeseries=_to_proto_timeseries(timeseries)
                ))

        async def get_timeseries_resource_info(
                self,
                timeseries_key: int) -> TimeseriesResource:
            proto_timeseries_resource = await self.mesh_service.GetTimeseriesResource(
                core_pb2.GetTimeseriesResourceRequest(
                    session_id=_to_proto_guid(self.session_id),
                    timeseries_resource_key=timeseries_key
                ))
            return TimeseriesResource._from_proto_timeseries_resource(proto_timeseries_resource)

        async def update_timeseries_resource_info(
                self,
                timeseries_key: int,
                new_curve_type: Timeseries.Curve = None,
                new_unit_of_measurement: str = None) -> None:
            request = super()._prepare_update_timeseries_resource_request(
                timeseries_key, new_curve_type, new_unit_of_measurement)
            await self.mesh_service.UpdateTimeseriesResource(request)

        async def get_attribute(
                self,
                attribute_id: Optional[uuid.UUID] = None,
                attribute_path: Optional[str] = None,
                full_attribute_info: bool = False) -> Type[AttributeBase]:
            request = super()._prepare_get_attribute_request(
                attribute_id, attribute_path, full_attribute_info)
            proto_attribute = await self.mesh_service.GetAttribute(request)
            return _from_proto_attribute(proto_attribute)

        async def get_timeseries_attribute(
                self,
                attribute_id: uuid.UUID = None,
                attribute_path: str = None,
                full_attribute_info: bool = False) -> TimeseriesAttribute:
            attribute = await self.get_attribute(attribute_id, attribute_path, full_attribute_info)
            if not isinstance(attribute, TimeseriesAttribute):
                raise ValueError(f'attribute is not a TimeseriesAttribute, but a {type(attribute).__name__}')
            return attribute

        async def search_for_attributes(
                self,
                query: str,
                start_object_id: Optional[uuid.UUID] = None,
                start_object_path: Optional[str] = None,
                full_attribute_info: bool = False) -> List[Type[AttributeBase]]:

            request = super()._prepare_search_attributes_request(
                start_object_id=start_object_id,
                start_object_path=start_object_path,
                query=query, full_attribute_info=full_attribute_info)

            attributes = []
            async for proto_attribute in self.mesh_service.SearchAttributes(request):
                attributes.append(_from_proto_attribute(proto_attribute))
            return attributes

        async def search_for_timeseries_attributes(
                self,
                query: str,
                start_object_id: Optional[uuid.UUID] = None,
                start_object_path: Optional[str] = None,
                full_attribute_info: bool = False) -> List[TimeseriesAttribute]:
            attributes = await self.search_for_attributes(
                query, start_object_id, start_object_path, full_attribute_info)
            return list(filter(lambda attr: (isinstance(attr, TimeseriesAttribute)), attributes))

        async def update_simple_attribute(
                self,
                value: _attribute.SIMPLE_TYPE_OR_COLLECTION,
                attribute_id: Optional[uuid.UUID] = None,
                attribute_path: Optional[str] = None) -> None:

            request = super()._prepare_update_simple_attribute_request(
                attribute_id=attribute_id,
                attribute_path=attribute_path,
                value=value)
            await self.mesh_service.UpdateSimpleAttribute(request)

        async def update_timeseries_attribute(
                self,
                new_local_expression: str = None,
                new_timeseries_resource_key: int = None,
                attribute_id: Optional[uuid.UUID] = None,
                attribute_path: Optional[str] = None) -> None:

            request = super()._prepare_update_timeseries_attribute_request(
                attribute_id=attribute_id,
                attribute_path=attribute_path,
                new_local_expression=new_local_expression,
                new_timeseries_resource_key=new_timeseries_resource_key)
            await self.mesh_service.UpdateTimeseriesAttribute(request)

        async def get_object(
                self,
                object_id: Optional[uuid.UUID] = None,
                object_path:  Optional[str] = None,
                full_attribute_info:  bool = False,
                attributes_filter: Optional[AttributesFilter] = None) -> Object:
            request = super()._prepare_get_object_request(
                object_id, object_path, full_attribute_info, attributes_filter)
            proto_object = await self.mesh_service.GetObject(request)
            return Object._from_proto_object(proto_object)

        async def search_for_objects(
                self,
                query: str,
                start_object_id: Optional[uuid.UUID] = None,
                start_object_path: Optional[str] = None,
                full_attribute_info: bool = False,
                attributes_filter: Optional[AttributesFilter] = None) -> List[Object]:
            request = super()._prepare_search_for_objects_request(
                query, start_object_id, start_object_path, full_attribute_info, attributes_filter)

            objects = []
            async for proto_object in self.mesh_service.SearchObjects(request):
                objects.append(proto_object)
            return objects

        async def create_object(
                self,
                name: str,
                owner_attribute_id: Optional[uuid.UUID] = None,
                owner_attribute_path: Optional[str] = None) -> Object:
            request = super()._prepare_create_object_request(
                name, owner_attribute_id, owner_attribute_path)
            proto_object = await self.mesh_service.CreateObject(request)
            return Object._from_proto_object(proto_object)

        async def update_object(
                self,
                object_id: Optional[uuid.UUID] = None,
                object_path: Optional[str] = None,
                new_name: Optional[str] = None,
                new_owner_attribute_id: Optional[uuid.UUID] = None,
                new_owner_attribute_path: Optional[str] = None) -> None:
            request = super()._prepare_update_object_request(
                object_id, object_path, new_name, new_owner_attribute_id, new_owner_attribute_path)
            await self.mesh_service.UpdateObject(request)

        async def delete_object(
                self,
                object_id: Optional[uuid.UUID] = None,
                object_path: Optional[str] = None,
                recursive_delete: bool = False) -> None:
            request = super()._prepare_delete_object_request(
                object_id, object_path, recursive_delete)
            await self.mesh_service.DeleteObject(request)

        def forecast_functions(
                self,
                relative_to: MeshObjectId,
                start_time: datetime,
                end_time: datetime) -> ForecastFunctionsAsync:
            return ForecastFunctionsAsync(self, relative_to, start_time, end_time)

        def history_functions(
                self,
                relative_to: MeshObjectId,
                start_time: datetime,
                end_time: datetime) -> HistoryFunctionsAsync:
            return HistoryFunctionsAsync(self, relative_to, start_time, end_time)

        def statistical_functions(
                self,
                relative_to: MeshObjectId,
                start_time: datetime,
                end_time: datetime) -> StatisticalFunctionsAsync:
            return StatisticalFunctionsAsync(self, relative_to, start_time, end_time)

        def transform_functions(
                self,
                relative_to: MeshObjectId,
                start_time: datetime,
                end_time: datetime) -> TransformFunctionsAsync:
            return TransformFunctionsAsync(self, relative_to, start_time, end_time)

        async def get_xy_sets(
                self, target: typing.Union[uuid.UUID, str],
                start_time: datetime = None,
                end_time: datetime = None,
                versions_only: bool = False
        ) -> typing.List[XySet]:
            gen = super()._get_xy_sets_impl(target, start_time, end_time, versions_only)
            request = next(gen)
            response = await self.mesh_service.GetXySets(request)
            return gen.send(response)

        async def update_xy_sets(
                self, target: typing.Union[uuid.UUID, str],
                start_time: datetime = None,
                end_time: datetime = None,
                new_xy_sets: typing.List[XySet] = []
        ) -> None:
            request = super()._prepare_update_xy_sets_request(target, start_time, end_time, new_xy_sets)
            await self.mesh_service.UpdateXySets(request)

        async def get_rating_curve_versions(
            self,
            target: Union[uuid.UUID, str],
            start_time: datetime,
            end_time: datetime,
            versions_only: bool = False
        ) -> List[RatingCurveVersion]:
            gen = super()._get_rating_curve_versions_impl(target, start_time, end_time, versions_only)
            request = next(gen)
            response = await self.mesh_service.GetRatingCurveVersions(request)
            return gen.send(response)

        async def update_rating_curve_versions(
            self,
            target: Union[uuid.UUID, str],
            start_time: datetime,
            end_time: datetime,
            new_versions: List[RatingCurveVersion]
        ) -> None:
            request = super()._prepare_update_rating_curve_versions_request(
                target, start_time, end_time, new_versions)
            await self.mesh_service.UpdateRatingCurveVersions(request)

    @staticmethod
    def _secure_grpc_channel(*args, **kwargs):
        return grpc.aio.secure_channel(*args, **kwargs)

    @staticmethod
    def _insecure_grpc_channel(*args, **kwargs):
        return grpc.aio.insecure_channel(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_version(self) -> VersionInfo:
        return VersionInfo._from_proto(
            await self.mesh_service.GetVersion(protobuf.empty_pb2.Empty()))

    async def get_user_identity(self) -> UserIdentity:
        return UserIdentity._from_proto(
            await self.mesh_service.GetUserIdentity(protobuf.empty_pb2.Empty()))

    async def revoke_access_token(self):
        if self.auth_metadata_plugin is None:
            raise RuntimeError('Authentication not configured for this connection')

        await self.mesh_service.RevokeAccessToken(
            protobuf.wrappers_pb2.StringValue(value = self.auth_metadata_plugin.token))
        self.auth_metadata_plugin.delete_access_token()

    def create_session(self) -> Optional[Session]:
        return self.connect_to_session(session_id=None)

    def connect_to_session(self, session_id: uuid.UUID):
        return self.Session(self.mesh_service, session_id)
