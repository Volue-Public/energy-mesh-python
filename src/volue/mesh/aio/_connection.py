"""
Functionality for asynchronously connecting to a Mesh server and working with its sessions.
"""

import asyncio
import typing
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Union

import grpc
from google import protobuf

from volue.mesh import (
    AttributeBase,
    AttributesFilter,
    Authentication,
    HydSimDataset,
    LinkRelationVersion,
    LogMessage,
    Object,
    Timeseries,
    TimeseriesAttribute,
    TimeseriesResource,
    UserIdentity,
    VersionInfo,
    _attribute,
    _base_connection,
    _base_session,
)
from volue.mesh._attribute import _from_proto_attribute
from volue.mesh._authentication import ExternalAccessTokenPlugin
from volue.mesh._common import (
    RatingCurveVersion,
    XySet,
    _from_proto_guid,
    _to_proto_curve_type,
    _to_proto_guid,
    _to_proto_resolution,
)
from volue.mesh._version_compatibility import (
    get_client_version,
    get_client_version_metadata_key,
    get_min_server_version,
    to_parsed_version,
)
from volue.mesh.availability._availability_aio import Availability
from volue.mesh.calc.forecast import ForecastFunctionsAsync
from volue.mesh.calc.history import HistoryFunctionsAsync
from volue.mesh.calc.statistical import StatisticalFunctionsAsync
from volue.mesh.calc.transform import TransformFunctionsAsync
from volue.mesh.proto.config.v1alpha import config_pb2, config_pb2_grpc
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc
from volue.mesh.proto.calc.v1alpha import calc_pb2_grpc
from volue.mesh.proto.hydsim.v1alpha import hydsim_pb2_grpc
from volue.mesh.proto.model.v1alpha import model_pb2_grpc
from volue.mesh.proto.model_definition.v1alpha import (
    model_definition_pb2,
    model_definition_pb2_grpc,
)
from volue.mesh.proto.session.v1alpha import session_pb2_grpc
from volue.mesh.proto.time_series.v1alpha import time_series_pb2, time_series_pb2_grpc
from volue.mesh.proto.type import resources_pb2


class Connection(_base_connection.Connection):
    class Session(_base_session.Session):
        """
        This class supports the async with statement, because it's an async contextmanager.
        https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers
        https://docs.python.org/3/reference/compound_stmts.html#async-with
        """

        def __init__(
            self,
            calc_service: calc_pb2_grpc.CalculationServiceStub,
            config_service: config_pb2_grpc.ConfigurationServiceStub,
            hydsim_service: hydsim_pb2_grpc.HydsimServiceStub,
            model_service: model_pb2_grpc.ModelServiceStub,
            model_definition_service: model_definition_pb2_grpc.ModelDefinitionServiceStub,
            session_service: session_pb2_grpc.SessionServiceStub,
            time_series_service: time_series_pb2_grpc.TimeseriesServiceStub,
            availability_service: availability_pb2_grpc.AvailabilityServiceStub,
            session_id: Optional[uuid.UUID] = None,
        ):
            super().__init__(
                session_id=session_id,
                calc_service=calc_service,
                hydsim_service=hydsim_service,
                model_service=model_service,
                model_definition_service=model_definition_service,
                session_service=session_service,
                time_series_service=time_series_service,
            )
            self.availability = Availability(
                availability_service=availability_service, session_id=session_id
            )
            self.config_service = config_service

        async def __aenter__(self):
            """
            Used by the 'with' statement to open a session when entering 'with'. |coro|

            Raises:
                grpc.RpcError: Error message raised if the gRPC request could not be completed
            """
            await self.open()
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            """
            Used by the 'with' statement to close a session when exiting 'with'. |coro|

            Raises:
                grpc.RpcError: Error message raised if the gRPC request could not be completed
            """
            await self.close()

        async def _extend_lifetime(self) -> None:
            await self.session_service.ExtendSession(_to_proto_guid(self.session_id))

        async def _get_unit_of_measurement_id_by_name(
            self, unit_of_measurement: str
        ) -> resources_pb2.Guid:
            list_response = await self.model_definition_service.ListUnitsOfMeasurement(
                model_definition_pb2.ListUnitsOfMeasurementRequest(
                    session_id=_to_proto_guid(self.session_id)
                )
            )

            return super()._get_unit_of_measurement_id_by_name(
                unit_of_measurement, list_response
            )

        async def open(self) -> None:
            metadata = [(get_client_version_metadata_key(), get_client_version())]
            version_info =  await self.config_service.GetVersion(
                protobuf.empty_pb2.Empty(), metadata=metadata
            )

            parsed_version = to_parsed_version(version_info.version)
            min_server_version = get_min_server_version()
            if parsed_version is not None:
                if parsed_version < min_server_version:
                    raise RuntimeError(
                        f"connecting to incompatible server version: {version_info.version}, minimum version is {min_server_version}"
                    )

            reply = await self.session_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = _from_proto_guid(reply.session_id)

            self.availability.session_id = self.session_id
            self.stop_worker_thread.clear()
            self.worker_thread = super().WorkerThread(self, asyncio.get_running_loop())
            self.worker_thread.start()

        async def close(self) -> None:
            if self.worker_thread is not None:
                self.stop_worker_thread.set()
                self.worker_thread.join()

            await self.session_service.EndSession(_to_proto_guid(self.session_id))
            self.session_id = None

        async def rollback(self) -> None:
            await self.session_service.Rollback(_to_proto_guid(self.session_id))

        async def commit(self) -> None:
            await self.session_service.Commit(_to_proto_guid(self.session_id))

        async def read_timeseries_points(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase],
            start_time: datetime,
            end_time: datetime,
        ) -> Timeseries:
            gen = super()._read_timeseries_impl(target, start_time, end_time)
            request = next(gen)
            return gen.send(await self.time_series_service.ReadTimeseries(request))

        async def write_timeseries_points(self, timeseries: Timeseries) -> None:
            request = super()._prepare_write_timeseries_points_request(timeseries)
            await self.time_series_service.WriteTimeseries(request)

        async def get_timeseries_resource_info(
            self, timeseries_key: int
        ) -> TimeseriesResource:
            proto_timeseries_resource = (
                await self.time_series_service.GetTimeseriesResource(
                    time_series_pb2.GetTimeseriesResourceRequest(
                        session_id=_to_proto_guid(self.session_id),
                        timeseries_resource_key=timeseries_key,
                    )
                )
            )
            return TimeseriesResource._from_proto_timeseries_resource(
                proto_timeseries_resource
            )

        async def update_timeseries_resource_info(
            self,
            timeseries_key: int,
            new_curve_type: Optional[Timeseries.Curve] = None,
            new_unit_of_measurement: Optional[str] = None,
        ) -> None:
            new_unit_of_measurement_id = None

            if new_unit_of_measurement is not None:
                new_unit_of_measurement_id = (
                    await self._get_unit_of_measurement_id_by_name(
                        new_unit_of_measurement
                    )
                )

            request = super()._prepare_update_timeseries_resource_request(
                timeseries_key, new_curve_type, new_unit_of_measurement_id
            )
            await self.time_series_service.UpdateTimeseriesResource(request)

        async def create_physical_timeseries(
            self,
            path: str,
            name: str,
            curve_type: Timeseries.Curve,
            resolution: Timeseries.Resolution,
            unit_of_measurement: str,
        ) -> TimeseriesResource:
            unit_of_measurement_id = await self._get_unit_of_measurement_id_by_name(
                unit_of_measurement
            )

            request = time_series_pb2.CreatePhysicalTimeseriesRequest(
                session_id=_to_proto_guid(self.session_id),
                path=path,
                name=name,
                curve_type=_to_proto_curve_type(curve_type),
                resolution=_to_proto_resolution(resolution),
                unit_of_measurement_id=unit_of_measurement_id,
            )

            response = await self.time_series_service.CreatePhysicalTimeseries(request)

            return TimeseriesResource._from_proto_timeseries_resource(response)

        async def get_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            full_attribute_info: bool = False,
        ) -> AttributeBase:
            request = super()._prepare_get_attribute_request(
                target, full_attribute_info
            )
            proto_attribute = await self.model_service.GetAttribute(request)
            return _from_proto_attribute(proto_attribute)

        async def get_timeseries_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            full_attribute_info: bool = False,
        ) -> TimeseriesAttribute:
            attribute = await self.get_attribute(target, full_attribute_info)
            if not isinstance(attribute, TimeseriesAttribute):
                raise ValueError(
                    f"attribute is not a TimeseriesAttribute, but a {type(attribute).__name__}"
                )
            return attribute

        async def search_for_attributes(
            self,
            target: Union[uuid.UUID, str, Object],
            query: str,
            full_attribute_info: bool = False,
        ) -> List[AttributeBase]:
            request = super()._prepare_search_attributes_request(
                target, query, full_attribute_info
            )

            attributes = []
            async for proto_attribute in self.model_service.SearchAttributes(request):
                attributes.append(_from_proto_attribute(proto_attribute))
            return attributes

        async def search_for_timeseries_attributes(
            self,
            target: Union[uuid.UUID, str, Object],
            query: str,
            full_attribute_info: bool = False,
        ) -> List[TimeseriesAttribute]:
            attributes = await self.search_for_attributes(
                target, query, full_attribute_info
            )
            return list(
                filter(lambda attr: (isinstance(attr, TimeseriesAttribute)), attributes)
            )

        async def update_simple_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            value: _attribute.SIMPLE_TYPE_OR_COLLECTION,
        ) -> None:
            request = super()._prepare_update_simple_attribute_request(target, value)
            await self.model_service.UpdateSimpleAttribute(request)

        async def update_timeseries_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            new_local_expression: Optional[str] = None,
            new_timeseries_resource_key: Optional[int] = None,
        ) -> None:
            request = super()._prepare_update_timeseries_attribute_request(
                target, new_local_expression, new_timeseries_resource_key
            )
            await self.model_service.UpdateTimeseriesAttribute(request)

        async def update_link_relation_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            new_target_object_ids: List[uuid.UUID],
            append: bool = False,
        ) -> None:
            request = super()._prepare_update_link_relation_attribute_request(
                target, new_target_object_ids, append
            )
            await self.model_service.UpdateLinkRelationAttribute(request)

        async def update_versioned_one_to_one_link_relation_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            start_time: datetime,
            end_time: datetime,
            new_versions: List[LinkRelationVersion],
        ) -> None:
            # If there are any versions provided then wrap it in additional List to reflect the proto entry.
            new_versions = [new_versions] if new_versions else new_versions
            request = super()._prepare_versioned_link_relation_attribute_request(
                target, new_versions, start_time, end_time
            )
            await self.model_service.UpdateVersionedLinkRelationAttribute(request)

        async def update_versioned_one_to_many_link_relation_attribute(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            new_entries: List[List[LinkRelationVersion]],
        ) -> None:
            request = super()._prepare_versioned_link_relation_attribute_request(
                target, new_entries
            )
            await self.model_service.UpdateVersionedLinkRelationAttribute(request)

        async def list_models(
            self,
        ) -> List[Object]:
            gen = super()._list_models_impl()
            request = next(gen)
            response = await self.model_service.ListModels(request)
            return gen.send(response)

        async def get_object(
            self,
            target: Union[uuid.UUID, str, Object],
            full_attribute_info: bool = False,
            attributes_filter: Optional[AttributesFilter] = None,
        ) -> Object:
            request = super()._prepare_get_object_request(
                target, full_attribute_info, attributes_filter
            )
            proto_object = await self.model_service.GetObject(request)
            return Object._from_proto_object(proto_object)

        async def search_for_objects(
            self,
            target: Union[uuid.UUID, str, Object],
            query: str,
            full_attribute_info: bool = False,
            attributes_filter: Optional[AttributesFilter] = None,
        ) -> List[Object]:
            request = super()._prepare_search_for_objects_request(
                target, query, full_attribute_info, attributes_filter
            )

            objects = []
            async for proto_object in self.model_service.SearchObjects(request):
                objects.append(Object._from_proto_object(proto_object))
            return objects

        async def create_object(
            self, target: Union[uuid.UUID, str, AttributeBase], name: str
        ) -> Object:
            request = super()._prepare_create_object_request(target=target, name=name)
            proto_object = await self.model_service.CreateObject(request)
            return Object._from_proto_object(proto_object)

        async def update_object(
            self,
            target: Union[uuid.UUID, str, Object],
            new_name: Optional[str] = None,
            new_owner_attribute: Optional[Union[uuid.UUID, str, AttributeBase]] = None,
        ) -> None:
            request = super()._prepare_update_object_request(
                target, new_name, new_owner_attribute
            )
            await self.model_service.UpdateObject(request)

        async def delete_object(
            self, target: Union[uuid.UUID, str, Object], recursive_delete: bool = False
        ) -> None:
            request = super()._prepare_delete_object_request(target, recursive_delete)
            await self.model_service.DeleteObject(request)

        def forecast_functions(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase, Object],
            start_time: datetime,
            end_time: datetime,
        ) -> ForecastFunctionsAsync:
            return ForecastFunctionsAsync(self, target, start_time, end_time)

        def history_functions(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase, Object],
            start_time: datetime,
            end_time: datetime,
        ) -> HistoryFunctionsAsync:
            return HistoryFunctionsAsync(self, target, start_time, end_time)

        def statistical_functions(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase, Object],
            start_time: datetime,
            end_time: datetime,
        ) -> StatisticalFunctionsAsync:
            return StatisticalFunctionsAsync(self, target, start_time, end_time)

        def transform_functions(
            self,
            target: Union[uuid.UUID, str, int, AttributeBase, Object],
            start_time: datetime,
            end_time: datetime,
        ) -> TransformFunctionsAsync:
            return TransformFunctionsAsync(self, target, start_time, end_time)

        async def get_xy_sets(
            self,
            target: typing.Union[uuid.UUID, str, AttributeBase],
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            versions_only: bool = False,
        ) -> typing.List[XySet]:
            gen = super()._get_xy_sets_impl(target, start_time, end_time, versions_only)
            request = next(gen)
            response = await self.model_service.GetXySets(request)
            return gen.send(response)

        async def update_xy_sets(
            self,
            target: typing.Union[uuid.UUID, str, AttributeBase],
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            new_xy_sets: typing.List[XySet] = [],
        ) -> None:
            request = super()._prepare_update_xy_sets_request(
                target, start_time, end_time, new_xy_sets
            )
            await self.model_service.UpdateXySets(request)

        async def get_rating_curve_versions(
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
            response = await self.model_service.GetRatingCurveVersions(request)
            return gen.send(response)

        async def update_rating_curve_versions(
            self,
            target: Union[uuid.UUID, str, AttributeBase],
            start_time: datetime,
            end_time: datetime,
            new_versions: List[RatingCurveVersion],
        ) -> None:
            request = super()._prepare_update_rating_curve_versions_request(
                target, start_time, end_time, new_versions
            )
            await self.model_service.UpdateRatingCurveVersions(request)

        async def run_simulation(
            self,
            model: str,
            case: str,
            start_time: datetime,
            end_time: datetime,
            *,
            resolution: timedelta = None,
            scenario: int = None,
            return_datasets: bool = False,
        ) -> typing.AsyncIterator[None]:
            request = self._prepare_run_simulation_request(
                model, case, start_time, end_time, resolution, scenario, return_datasets
            )
            async for response in self.hydsim_service.RunHydroSimulation(request):
                if response.HasField("log_message"):
                    yield LogMessage._from_proto(response.log_message)
                if response.HasField("dataset"):
                    yield HydSimDataset._from_proto(response.dataset)
                else:
                    yield None

        async def run_inflow_calculation(
            self,
            model: str,
            area: str,
            water_course: str,
            start_time: datetime,
            end_time: datetime,
            *,
            resolution: timedelta = None,
            return_datasets: bool = False,
        ) -> typing.AsyncIterator[None]:
            targets = await self.search_for_objects(
                f"Model/{model}/Mesh.To_Areas/{area}",
                f"To_HydroProduction/To_WaterCourses/@[.Name={water_course}]",
            )
            request = self._prepare_run_inflow_calculation_request(
                targets, start_time, end_time, resolution, return_datasets
            )
            async for response in self.hydsim_service.RunInflowCalculation(request):
                if response.HasField("log_message"):
                    yield LogMessage._from_proto(response.log_message)
                if response.HasField("dataset"):
                    yield HydSimDataset._from_proto(response.dataset)
                else:
                    yield None

        async def get_mc_file(
            self,
            model: str,
            case: str,
            start_time: datetime,
            end_time: datetime,
        ) -> Union[typing.Iterator[None], typing.AsyncIterator[None]]:
            request = self._prepare_get_mc_file_request(
                model, case, start_time, end_time
            )
            async for response in self.hydsim_service.GetMcFile(request):
                if response.HasField("log_message"):
                    yield LogMessage._from_proto(response.log_message)
                elif response.HasField("mc_file"):
                    yield response.mc_file
                else:
                    yield None

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
            await self.config_service.GetVersion(
                protobuf.empty_pb2.Empty()
            )
        )

    async def get_user_identity(self) -> UserIdentity:
        return UserIdentity._from_proto(
            await self.auth_service.GetUserIdentity(protobuf.empty_pb2.Empty())
        )

    async def update_external_access_token(self, access_token: str) -> None:
        if (
            self.auth_metadata_plugin is None
            or type(self.auth_metadata_plugin) is not ExternalAccessTokenPlugin
        ):
            raise RuntimeError("connection is not using external access token mode")

        self.auth_metadata_plugin.update_access_token(access_token)

    async def revoke_access_token(self) -> None:
        if (
            self.auth_metadata_plugin is None
            or type(self.auth_metadata_plugin) is ExternalAccessTokenPlugin
        ):
            raise RuntimeError("Authentication not configured for this connection")

        await self.auth_service.RevokeAccessToken(
            protobuf.wrappers_pb2.StringValue(value=self.auth_metadata_plugin.token)
        )
        self.auth_metadata_plugin.delete_access_token()

    def create_session(self) -> Session:
        return self.connect_to_session(session_id=None)

    def connect_to_session(self, session_id: Optional[uuid.UUID]) -> Session:
        session = self.Session(
            calc_service=self.calc_service,
            config_service=self.config_service,
            hydsim_service=self.hydsim_service,
            model_service=self.model_service,
            model_definition_service=self.model_definition_service,
            session_service=self.session_service,
            time_series_service=self.time_series_service,
            availability_service=self.availability_service,
            session_id=session_id,
        )
        return session
