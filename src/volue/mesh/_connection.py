"""
Functionality for synchronously connecting to a Mesh server and working with its sessions.
"""

from datetime import datetime
import typing
from typing import List, Optional, Union
import uuid

from google import protobuf
import grpc

from volue.mesh import (
    Authentication,
    Timeseries,
    AttributesFilter,
    UserIdentity,
    VersionInfo,
    AttributeBase,
    TimeseriesAttribute,
    TimeseriesResource,
    Object,
)
from volue.mesh._attribute import _from_proto_attribute
from volue.mesh._authentication import ExternalAccessTokenPlugin
from volue.mesh._common import (
    LinkRelationVersion,
    XySet,
    RatingCurveVersion,
    _to_proto_guid,
    _from_proto_guid,
    _to_proto_timeseries,
    _to_proto_utcinterval,
)
from volue.mesh._mesh_id import _to_proto_object_mesh_id
from volue.mesh.calc.forecast import ForecastFunctions
from volue.mesh.calc.history import HistoryFunctions
from volue.mesh.calc.statistical import StatisticalFunctions
from volue.mesh.calc.transform import TransformFunctions
from volue.mesh.proto.core.v1alpha import core_pb2, core_pb2_grpc

from . import _base_connection
from . import _base_session
from . import _attribute


class Connection(_base_connection.Connection):
    class Session(_base_session.Session):
        """
        This class supports the with statement, because it's a contextmanager.
        """

        def __init__(
            self,
            mesh_service: core_pb2_grpc.MeshServiceStub,
            session_id: Optional[uuid.UUID] = None,
        ):
            super().__init__(session_id=session_id, mesh_service=mesh_service)

        def __enter__(self):
            """
            Used by the 'with' statement to open a session when entering 'with'
            Raises:
                grpc.RpcError: Error message raised if the gRPC request could not be completed
            """
            self.open()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            Used by the 'with' statement to close a session when exiting 'with'.

            Raises:
                grpc.RpcError: Error message raised if the gRPC request could not be completed
            """
            self.close()

        def _extend_lifetime(self) -> None:
            self.mesh_service.ExtendSession(_to_proto_guid(self.session_id))

        def open(self) -> None:
            reply = self.mesh_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = _from_proto_guid(reply)

            self.stop_worker_thread.clear()
            self.worker_thread = super().WorkerThread(self)
            self.worker_thread.start()

        def close(self) -> None:
            if self.worker_thread is not None:
                self.stop_worker_thread.set()
                self.worker_thread.join()

            self.mesh_service.EndSession(_to_proto_guid(self.session_id))
            self.session_id = None

        def rollback(self) -> None:
            self.mesh_service.Rollback(_to_proto_guid(self.session_id))

        def commit(self) -> None:
            self.mesh_service.Commit(_to_proto_guid(self.session_id))

        def read_timeseries_points(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase],
            start_time: datetime,
            end_time: datetime,
        ) -> Timeseries:
            gen = super()._read_timeseries_impl(target, start_time, end_time)
            request = next(gen)
            return gen.send(self.mesh_service.ReadTimeseries(request))

        def write_timeseries_points(self, timeseries: Timeseries) -> None:
            self.mesh_service.WriteTimeseries(
                core_pb2.WriteTimeseriesRequest(
                    session_id=_to_proto_guid(self.session_id),
                    timeseries=_to_proto_timeseries(timeseries),
                )
            )

        def get_timeseries_resource_info(
            self, timeseries_key: int
        ) -> TimeseriesResource:
            proto_timeseries_resource = self.mesh_service.GetTimeseriesResource(
                core_pb2.GetTimeseriesResourceRequest(
                    session_id=_to_proto_guid(self.session_id),
                    timeseries_resource_key=timeseries_key,
                )
            )
            return TimeseriesResource._from_proto_timeseries_resource(
                proto_timeseries_resource
            )

        def update_timeseries_resource_info(
            self,
            timeseries_key: int,
            new_curve_type: Optional[Timeseries.Curve] = None,
            new_unit_of_measurement: Optional[str] = None,
        ) -> None:
            request = super()._prepare_update_timeseries_resource_request(
                timeseries_key, new_curve_type, new_unit_of_measurement
            )
            self.mesh_service.UpdateTimeseriesResource(request)

        def get_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            full_attribute_info: bool = False,
        ) -> AttributeBase:
            request = super()._prepare_get_attribute_request(
                target, full_attribute_info
            )
            proto_attribute = self.mesh_service.GetAttribute(request)
            return _from_proto_attribute(proto_attribute)

        def get_timeseries_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            full_attribute_info: bool = False,
        ) -> TimeseriesAttribute:
            attribute = self.get_attribute(target, full_attribute_info)
            if not isinstance(attribute, TimeseriesAttribute):
                raise ValueError(
                    f"attribute is not a TimeseriesAttribute, but a {type(attribute).__name__}"
                )
            return attribute

        def search_for_attributes(
            self,
            target: Union[uuid.UUID, str, Object],
            query: str,
            full_attribute_info: bool = False,
        ) -> List[AttributeBase]:
            request = super()._prepare_search_attributes_request(
                target, query, full_attribute_info
            )

            proto_attributes = self.mesh_service.SearchAttributes(request)

            attributes = []
            for proto_attribute in proto_attributes:
                attributes.append(_from_proto_attribute(proto_attribute))
            return attributes

        def search_for_timeseries_attributes(
            self,
            target: Union[uuid.UUID, str, Object],
            query: str,
            full_attribute_info: bool = False,
        ) -> List[TimeseriesAttribute]:
            attributes = self.search_for_attributes(target, query, full_attribute_info)
            return list(
                filter(lambda attr: (isinstance(attr, TimeseriesAttribute)), attributes)
            )

        def update_simple_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            value: _attribute.SIMPLE_TYPE_OR_COLLECTION,
        ) -> None:
            request = super()._prepare_update_simple_attribute_request(target, value)
            self.mesh_service.UpdateSimpleAttribute(request)

        def update_timeseries_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            new_local_expression: Optional[str] = None,
            new_timeseries_resource_key: Optional[int] = None,
        ) -> None:
            request = super()._prepare_update_timeseries_attribute_request(
                target, new_local_expression, new_timeseries_resource_key
            )
            self.mesh_service.UpdateTimeseriesAttribute(request)

        def update_link_relation_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            new_target_object_ids: List[uuid.UUID],
            append: bool = False,
        ) -> None:
            request = super()._prepare_update_link_relation_attribute_request(
                target, new_target_object_ids, append
            )
            self.mesh_service.UpdateLinkRelationAttribute(request)

        def update_versioned_link_relation_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            start_time: datetime,
            end_time: datetime,
            new_versions: List[LinkRelationVersion],
        ) -> None:
            request = super()._prepare_versioned_link_relation_attribute_request(
                target, start_time, end_time, new_versions
            )
            self.mesh_service.UpdateVersionedLinkRelationAttribute(request)

        def list_models(
            self,
        ) -> List[Object]:
            gen = super()._list_models_impl()
            request = next(gen)
            return gen.send(self.mesh_service.ListModels(request))

        def get_object(
            self,
            target: Union[uuid.UUID, str, Object],
            full_attribute_info: bool = False,
            attributes_filter: Optional[AttributesFilter] = None,
        ) -> Object:
            request = super()._prepare_get_object_request(
                target, full_attribute_info, attributes_filter
            )
            proto_object = self.mesh_service.GetObject(request)
            return Object._from_proto_object(proto_object)

        def search_for_objects(
            self,
            target: Union[uuid.UUID, str, Object],
            query: str,
            full_attribute_info: bool = False,
            attributes_filter: Optional[AttributesFilter] = None,
        ) -> List[Object]:
            request = super()._prepare_search_for_objects_request(
                target, query, full_attribute_info, attributes_filter
            )

            proto_objects = self.mesh_service.SearchObjects(request)

            objects = []
            for proto_object in proto_objects:
                objects.append(Object._from_proto_object(proto_object))
            return objects

        def create_object(
            self, target: Union[uuid.UUID, str, AttributeBase], name: str
        ) -> Object:
            request = super()._prepare_create_object_request(target=target, name=name)
            proto_object = self.mesh_service.CreateObject(request)
            return Object._from_proto_object(proto_object)

        def update_object(
            self,
            target: Union[uuid.UUID, str, Object],
            new_name: Optional[str] = None,
            new_owner_attribute: Optional[Union[uuid.UUID, str, AttributeBase]] = None,
        ) -> None:
            request = super()._prepare_update_object_request(
                target, new_name, new_owner_attribute
            )
            self.mesh_service.UpdateObject(request)

        def delete_object(
            self, target: Union[uuid.UUID, str, Object], recursive_delete: bool = False
        ) -> None:
            request = super()._prepare_delete_object_request(target, recursive_delete)
            self.mesh_service.DeleteObject(request)

        def forecast_functions(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase, Object],
            start_time: datetime,
            end_time: datetime,
        ) -> ForecastFunctions:
            return ForecastFunctions(self, target, start_time, end_time)

        def history_functions(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase, Object],
            start_time: datetime,
            end_time: datetime,
        ) -> HistoryFunctions:
            return HistoryFunctions(self, target, start_time, end_time)

        def statistical_functions(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase, Object],
            start_time: datetime,
            end_time: datetime,
        ) -> StatisticalFunctions:
            return StatisticalFunctions(self, target, start_time, end_time)

        def transform_functions(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase, Object],
            start_time: datetime,
            end_time: datetime,
        ) -> TransformFunctions:
            return TransformFunctions(self, target, start_time, end_time)

        def get_xy_sets(
            self,
            target: typing.Union[uuid.UUID, str, AttributeBase],
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            versions_only: bool = False,
        ) -> typing.List[XySet]:
            gen = super()._get_xy_sets_impl(target, start_time, end_time, versions_only)
            request = next(gen)
            return gen.send(self.mesh_service.GetXySets(request))

        def update_xy_sets(
            self,
            target: typing.Union[uuid.UUID, str, AttributeBase],
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            new_xy_sets: typing.List[XySet] = [],
        ) -> None:
            request = super()._prepare_update_xy_sets_request(
                target, start_time, end_time, new_xy_sets
            )
            self.mesh_service.UpdateXySets(request)

        def get_rating_curve_versions(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            start_time: datetime,
            end_time: datetime,
            versions_only: bool = False,
        ) -> List[RatingCurveVersion]:
            gen = super()._get_rating_curve_versions_impl(
                target, start_time, end_time, versions_only
            )
            request = next(gen)
            return gen.send(self.mesh_service.GetRatingCurveVersions(request))

        def update_rating_curve_versions(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            start_time: datetime,
            end_time: datetime,
            new_versions: List[RatingCurveVersion],
        ) -> None:
            request = super()._prepare_update_rating_curve_versions_request(
                target, start_time, end_time, new_versions
            )
            self.mesh_service.UpdateRatingCurveVersions(request)

        def run_simulation(
            self,
            model: str,
            case_group: str,
            case: str,
            start_time: datetime,
            end_time: datetime,
            resolution: Timeseries.Resolution,
            scenario: int,
            return_datasets: bool,
        ) -> typing.Iterator[None]:
            if start_time is None or end_time is None:
                raise TypeError("start_time and end_time must both have a value")

            simulation = f"Model/{model}/{case_group}.has_OptimisationCases/{case}.has_OptimisationParameters/Optimal.has_HydroSimulation/HydroSimulation"

            request = core_pb2.SimulationRequest(
                session_id=_to_proto_guid(self.session_id),
                simulation=_to_proto_object_mesh_id(simulation),
                interval=_to_proto_utcinterval(start_time, end_time),
                scenario=scenario,
                return_datasets=return_datasets,
            )

            for response in self.mesh_service.RunHydroSimulation(request):
                yield None

        def run_inflow_calculation(
            self,
            model: str,
            area: str,
            water_course: str,
            start_time: datetime,
            end_time: datetime,
        ) -> typing.Iterator[None]:
            if start_time is None or end_time is None:
                raise TypeError("start_time and end_time must both have a value")

            targets = self.search_for_objects(
                f"Model/{model}/Mesh.To_Areas/{area}",
                f"To_HydroProduction/To_WaterCourses/@[.Name={water_course}]",
            )

            if len(targets) != 1:
                raise ValueError(f"expected one water course, found {len(targets)}")

            request = core_pb2.SimulationRequest(
                session_id=_to_proto_guid(self.session_id),
                simulation=_to_proto_object_mesh_id(targets[0].id),
                interval=_to_proto_utcinterval(start_time, end_time),
                scenario=0,
                return_datasets=False,
            )

            for response in self.mesh_service.RunInflowCalculation(request):
                yield None

    @staticmethod
    def _secure_grpc_channel(*args, **kwargs):
        return grpc.secure_channel(*args, **kwargs)

    @staticmethod
    def _insecure_grpc_channel(*args, **kwargs):
        return grpc.insecure_channel(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_version(self) -> VersionInfo:
        return VersionInfo._from_proto(
            self.mesh_service.GetVersion(protobuf.empty_pb2.Empty())
        )

    def get_user_identity(self) -> UserIdentity:
        return UserIdentity._from_proto(
            self.mesh_service.GetUserIdentity(protobuf.empty_pb2.Empty())
        )

    def update_external_access_token(self, access_token: str) -> None:
        if (
            self.auth_metadata_plugin is None
            or type(self.auth_metadata_plugin) is not ExternalAccessTokenPlugin
        ):
            raise RuntimeError("connection is not using external access token mode")

        self.auth_metadata_plugin.update_access_token(access_token)

    def revoke_access_token(self) -> None:
        if (
            self.auth_metadata_plugin is None
            or type(self.auth_metadata_plugin) is not Authentication
        ):
            raise RuntimeError("Authentication not configured for this connection")

        self.mesh_service.RevokeAccessToken(
            protobuf.wrappers_pb2.StringValue(value=self.auth_metadata_plugin.token)
        )
        self.auth_metadata_plugin.delete_access_token()

    def create_session(self) -> Session:
        return self.connect_to_session(session_id=None)

    def connect_to_session(self, session_id: Optional[uuid.UUID]) -> Session:
        return self.Session(self.mesh_service, session_id)
