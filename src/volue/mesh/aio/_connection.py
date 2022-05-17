"""
Functionality for asynchronously connecting to a Mesh server and working with its sessions.
"""

import datetime
from typing import Optional, List, Type
import uuid

from google import protobuf
import grpc

from volue.mesh import Timeseries, MeshObjectId, AttributeBase, Object
from volue.mesh._attribute import _from_proto_attribute
from volue.mesh._common import AttributesFilter, _from_proto_guid, _to_proto_guid, _to_protobuf_utcinterval, \
    _read_proto_reply, _to_proto_object_id, _to_proto_timeseries, _to_proto_curve_type
from volue.mesh.calc.forecast import ForecastFunctionsAsync
from volue.mesh.calc.history import HistoryFunctionsAsync
from volue.mesh.calc.statistical import StatisticalFunctionsAsync
from volue.mesh.calc.transform import TransformFunctionsAsync
from volue.mesh.proto.core.v1alpha import core_pb2, core_pb2_grpc

from volue.mesh import _base_connection
from volue.mesh import _base_session


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
            """
            Request to open a session on the Mesh server
            |coro|

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            reply = await self.mesh_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = _from_proto_guid(reply)
            return reply

        async def close(self) -> None:
            """
            Request to close a session on the Mesh server. |coro|

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed

            Note:
                This method does not wait for the Mesh server to finish closing
                the session on the Mesh server
            """
            await self.mesh_service.EndSession(_to_proto_guid(self.session_id))
            self.session_id = None

        async def read_timeseries_points(self,
                                         start_time: datetime,
                                         end_time: datetime,
                                         mesh_object_id: MeshObjectId) -> Timeseries:
            """
            Reads time series points for
            the specified timeseries in the given interval. |coro|

            Args:
                start_time (datetime): the start date and time of the time series interval
                end_time (datetime): the end date and time of the time series interval
                mesh_object_id (MeshObjectId): unique way of identifying a Mesh object that contains a time series. Using either a  Universal Unique Identifier for Mesh objects, a path in the :ref:`Mesh object model <mesh object model>` or a  integer that only applies to a specific raw time series

            For information about `datetime` arguments and time zones refer to :ref:`mesh_client:Date times and time zones`.

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
                RuntimeError:  Error message raised if the input is not valid
                TypeError:  Error message raised if the returned result from the request is not as expected
            """
            object_id = core_pb2.ObjectId()
            if mesh_object_id.timskey is not None:
                object_id.timskey = mesh_object_id.timskey
            elif mesh_object_id.uuid_id is not None:
                object_id.guid.CopyFrom(_to_proto_guid(mesh_object_id.uuid_id))
            elif mesh_object_id.full_name is not None:
                object_id.full_name = mesh_object_id.full_name
            else:
                raise TypeError("need to specify either timskey, uuid_id or full_name")

            response = await self.mesh_service.ReadTimeseries(
                core_pb2.ReadTimeseriesRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=object_id,
                    interval=_to_protobuf_utcinterval(start_time, end_time)
                ))

            timeseries = _read_proto_reply(response)
            if len(timeseries) != 1:
                raise RuntimeError(
                    f"invalid result from 'read_timeseries_points', expected 1 timeseries, but got {len(timeseries)}")

            return timeseries[0]

        async def write_timeseries_points(self, timeserie: Timeseries):
            """
            Writes time series points for the specified timeseries in the given interval.
            |coro|

            Args:
                timeserie (:class:`volue.mesh.Timeseries`): The modified time series

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            await self.mesh_service.WriteTimeseries(
                core_pb2.WriteTimeseriesRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=_to_proto_object_id(timeserie),
                    timeseries=_to_proto_timeseries(timeserie)
                ))

        async def get_timeseries_resource_info(self,
                                               uuid_id: uuid.UUID = None,
                                               path: str = None,
                                               timskey: int = None,
                                               ) -> core_pb2.TimeseriesEntry:
            """
            Request information associated with a raw  time series entry. *Time series entry* is the raw timestamps, values and flags of a times series. It is stored in the resource catalog and will often be connected to a :doc:`time series attribute <mesh_object_attributes>`.. |coro|

            Args:
                uuid_id (uuid.UUID): Universal Unique Identifier for Mesh objects
                path (str): path in the resource model.
                timskey (int): integer that only applies to a specific raw time series

            Note:
                This `path` is NOT the same as full name or the path in the Mesh object model,
                this `path` refers to its location in the resource catalog.

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed

            Returns:
                core_pb2.TimeseriesEntry
            """
            entry_id = core_pb2.TimeseriesEntryId()
            if timskey is not None:
                entry_id.timeseries_key = timskey
            elif uuid_id is not None:
                entry_id.guid.CopyFrom(_to_proto_guid(uuid_id))
            elif path is not None:
                entry_id.path = path
            else:
                raise Exception("Need to specify either uuid_id, timeseries_key or path.")

            reply = await self.mesh_service.GetTimeseriesEntry(
                core_pb2.GetTimeseriesEntryRequest(
                    session_id=_to_proto_guid(self.session_id),
                    entry_id=entry_id
                ))
            return reply

        async def update_timeseries_resource_info(self,
                                                  uuid_id: uuid.UUID = None,
                                                  path: str = None,
                                                  timskey: int = None,
                                                  new_path: str = None,
                                                  new_curve_type: Timeseries.Curve = None,
                                                  new_unit_of_measurement: str = None
                                                  ) -> None:
            """
            Request information associated with a Mesh object
            which has a link to a time series, either calculated or raw. |coro|

            Args:
                uuid_id (uuid.UUID): Universal Unique Identifier for Mesh objects
                path (str): path in the resource model.
                timskey (int): integer that only applies to a specific raw time series
                new_path (str): set new  path in the resource model.
                new_curve_type (Timeseries.Curve): set new  curve type for the time series.
                new_unit_of_measurement (str): set new  unit of measurement for the time series.

            Note:
                Specify either uuid_id, path or timskey to a timeseries entry.
                Only one is needed.

            Note:
                Specify which ever of the new_* fields you want to update.

            Note:
                This `path` is NOT the same as full name or the path in the Mesh object model,
                this `path` refers to its location in the resource catalog.

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            entry_id = core_pb2.TimeseriesEntryId()
            if timskey is not None:
                entry_id.timeseries_key = timskey
            elif uuid_id is not None:
                entry_id.guid.CopyFrom(_to_proto_guid(uuid_id))
            elif path is not None:
                entry_id.path = path
            else:
                raise Exception("Need to specify either uuid_id, timeseries_key or path.")

            request = core_pb2.UpdateTimeseriesEntryRequest(
                session_id=_to_proto_guid(self.session_id),
                entry_id=entry_id
            )

            paths = []
            if new_path is not None:
                request.new_path = new_path
                paths.append("new_path")
            if new_curve_type is not None:
                request.new_curve_type.CopyFrom(_to_proto_curve_type(new_curve_type))
                paths.append("new_curve_type")
            if new_unit_of_measurement is not None:
                request.new_unit_of_measurement = new_unit_of_measurement
                paths.append("new_unit_of_measurement")

            request.field_mask.CopyFrom(protobuf.field_mask_pb2.FieldMask(paths=paths))

            await self.mesh_service.UpdateTimeseriesEntry(request)

        async def get_timeseries_attribute(self,
                                           model: str = None,
                                           uuid_id: uuid.UUID = None,
                                           path: str = None
                                           ) -> core_pb2.TimeseriesAttribute:
            """
            Request information associated with a Mesh object :doc:`attribute <mesh_object_attributes>`. |coro|

            Args:
                model (str): the name of the :ref:`Mesh object model <mesh object model>` you want to work within
                uuid_id (uuid.UUID): Universal Unique Identifier for Mesh objects
                path (str): path in the :ref:`Mesh object model <mesh object model>`

            Note:
                Specify model and either `uuid_id` or `path` to a timeseries attribute.
                Only one or uuid_id and path is needed.

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            attribute_id = core_pb2.AttributeId()
            if uuid_id is not None:
                attribute_id.id.CopyFrom(_to_proto_guid(uuid_id))
            elif path is not None:
                attribute_id.path = path
            else:
                raise Exception("Need to specify either uuid_id or path.")

            reply = await self.mesh_service.GetTimeseriesAttribute(
                core_pb2.GetTimeseriesAttributeRequest(
                    session_id=_to_proto_guid(self.session_id),
                    model=model,
                    attribute_id=attribute_id
                )
            )
            return reply

        async def update_timeseries_attribute(self,
                                              uuid_id: uuid.UUID = None,
                                              path: str = None,
                                              new_local_expression: str = None,
                                              new_timeseries_entry_id: core_pb2.TimeseriesEntryId = None,
                                              ) -> None:
            """
            Update information associated with a Mesh object doc:`attribute <mesh_object_attributes>`. |coro|

            Args:
                uuid_id (uuid.UUID): Universal Unique Identifier for Mesh objects
                path (str): path in the :ref:`Mesh object model <mesh object model>`
                new_local_expression (str): set new local  expression which consists of one or more functions to call. See :ref:`expressions <mesh expression>`
                new_timeseries_entry_id (core_pb2.TimeseriesEntryId): set new  Universal Unique Identifier for Mesh objects for the  time series entry. *Time series entry* is the raw timestamps, values and flags of a times series. It is stored in the resource catalog and will often be connected to a :doc:`time series attribute <mesh_object_attributes>`..

            Note:
                Specify either `uuid_id` or `path` to a timeseries attribute you want to update. Only one argument: `uuid_id ` or `path` is needed.

            Note:
             Specify a new entry and/or a new local expression for the attribute.

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            attribute_id = core_pb2.AttributeId()
            if uuid_id is not None:
                attribute_id.id.CopyFrom(_to_proto_guid(uuid_id))
            elif path is not None:
                attribute_id.path = path
            else:
                raise Exception("Need to specify either uuid_id or path.")

            paths = []
            if new_timeseries_entry_id is not None:
                paths.append("new_timeseries_entry_id")
            if new_local_expression is not None:
                paths.append("new_local_expression")
            field_mask = protobuf.field_mask_pb2.FieldMask(paths=paths)

            await self.mesh_service.UpdateTimeseriesAttribute(
                core_pb2.UpdateTimeseriesAttributeRequest(
                    session_id=_to_proto_guid(self.session_id),
                    attribute_id=attribute_id,
                    field_mask=field_mask,
                    new_timeseries_entry_id=new_timeseries_entry_id,
                    new_local_expression=new_local_expression
                )
            )

        async def search_for_timeseries_attribute(self,
                                                  model: str,
                                                  query: str,
                                                  start_object_path: str = None,
                                                  start_object_guid: uuid.UUID = None
                                                  ) -> List[core_pb2.TimeseriesAttribute]:
            """
            Use the :doc:`Mesh search language <mesh_search>` to find :doc:`Mesh object attributes <mesh_object_attributes>` in the Mesh object model. |coro|

            Args:
                model (str): the name of the :ref:`Mesh object model <mesh object model>` you want to work within
                query (str): a search formulated using the :doc:`Mesh search language <mesh_search>`
                start_object_path (str): Start searching at the path in the :ref:`Mesh object model <mesh object model>`
                start_object_guid (uuid.UUID): Start searching at the object with the  Universal Unique Identifier for Mesh objects

            Note:
                Specify a model, a query using mesh query language and start object to start the search from,
                using either a path or a guid.

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            request = core_pb2.SearchTimeseriesAttributesRequest(
                session_id=_to_proto_guid(self.session_id),
                model_name=model,
                query=query
            )
            if start_object_path is not None:
                request.start_object_path = start_object_path
            elif start_object_guid is not None:
                request.start_object_guid.CopyFrom(_to_proto_guid(start_object_guid))
            else:
                raise Exception("Need to specify either start_object_path or start_object_guid")

            replies = []
            async for reply in self.mesh_service.SearchTimeseriesAttributes(request):
                replies.append(reply)
            return replies

        async def get_attribute(
                self,
                attribute_id: Optional[uuid.UUID] = None,
                attribute_path: Optional[str] = None,
                full_attribute_info: bool = False) -> Type[AttributeBase]:
            request = super()._prepare_get_attribute_request(
                attribute_id, attribute_path, full_attribute_info)
            proto_attribute = await self.mesh_service.GetAttribute(request)
            return _from_proto_attribute(proto_attribute)

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
            return await self.mesh_service.UpdateObject(request)

        async def delete_object(
                self,
                object_id: Optional[uuid.UUID] = None,
                object_path: Optional[str] = None,
                recursive_delete: bool = False) -> None:
            request = super()._prepare_delete_object_request(
                object_id, object_path, recursive_delete)
            return await self.mesh_service.DeleteObject(request)

        async def rollback(self) -> None:
            """
            Discard changes in the :doc:`Mesh session <mesh_session>`. |coro|

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            await self.mesh_service.Rollback(_to_proto_guid(self.session_id))

        async def commit(self) -> None:
            """
            Commit changes made in the :doc:`Mesh session <mesh_session>` to the shared storage. |coro|

            Raises:
                grpc.RpcError:  Error message raised if the gRPC request could not be completed
            """
            await self.mesh_service.Commit(_to_proto_guid(self.session_id))

        def forecast_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> ForecastFunctionsAsync:
            """Access to :ref:`mesh_functions:Forecast` functions.

            Args:
                relative_to (MeshObjectId): a Mesh object to perform actions relative to
                start_time (datetime): the start date and time of the time series interval
                end_time (datetime): the end date and time of the time series interval

            Returns:
                ForecastFunctions: object containing all forecast functions
            """
            return ForecastFunctionsAsync(self, relative_to, start_time, end_time)

        def history_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> HistoryFunctionsAsync:
            """Access to :ref:`mesh_functions:History` functions.

            Args:
                relative_to (MeshObjectId): a Mesh object to perform actions relative to
                start_time (datetime): the start date and time of the time series interval
                end_time (datetime): the end date and time of the time series interval

            Returns:
                HistoryFunctions: object containing all history functions
            """
            return HistoryFunctionsAsync(self, relative_to, start_time, end_time)

        def statistical_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> StatisticalFunctionsAsync:
            """Access to :ref:`mesh_functions:Statistical` functions.

            Args:
                relative_to (MeshObjectId): a Mesh object to perform actions relative to
                start_time (datetime): the start date and time of the time series interval
                end_time (datetime): the end date and time of the time series interval

            Returns:
                StatisticalFunctions: object containing all statistical functions
            """
            return StatisticalFunctionsAsync(self, relative_to, start_time, end_time)

        def transform_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> TransformFunctionsAsync:
            """Access to :ref:`mesh_functions:Transform` functions.

            Args:
                relative_to (MeshObjectId): a Mesh object to perform actions relative to
                start_time (datetime): the start date and time of the time series interval
                end_time (datetime): the end date and time of the time series interval

            Returns:
                TransformFunctions: object containing all transformation functions
            """
            return TransformFunctionsAsync(self, relative_to, start_time, end_time)

    @staticmethod
    def _secure_grpc_channel(*args, **kwargs):
        return grpc.aio.secure_channel(*args, **kwargs)

    @staticmethod
    def _insecure_grpc_channel(*args, **kwargs):
        return grpc.aio.insecure_channel(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_version(self):
        return await self.mesh_service.GetVersion(protobuf.empty_pb2.Empty())

    async def get_user_identity(self):
        response = await self.mesh_service.GetUserIdentity(protobuf.empty_pb2.Empty())
        return response

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
