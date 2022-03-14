"""
Functionality for asynchronously connecting to a Mesh server and working with its sessions.
"""

import uuid
from typing import Optional, List
from datetime import datetime
from google import protobuf
import grpc
from volue.mesh import Authentication, Credentials, Timeseries, MeshObjectId
from volue.mesh._common import _from_proto_guid, _to_proto_guid, _to_protobuf_utcinterval, \
    _read_proto_reply, _to_proto_object_id, _to_proto_timeseries, _to_proto_curve_type
from volue.mesh.calc.forecast import ForecastFunctionsAsync
from volue.mesh.calc.history import HistoryFunctionsAsync
from volue.mesh.calc.statistical import StatisticalFunctionsAsync
from volue.mesh.calc.transform import TransformFunctionsAsync
from volue.mesh.proto.core.v1alpha import core_pb2, core_pb2_grpc


class Connection:
    """Represents a connection to a Mesh server."""

    class Session:
        """
        This class supports the async with statement, because it's an async contextmanager.
        https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers
        https://docs.python.org/3/reference/compound_stmts.html#async-with
        """

        def __init__(
                self,
                mesh_service: core_pb2_grpc.MeshServiceStub,
                session_id: uuid.UUID = None):
            """
            Initialize a session object
            for working with the Mesh server.

            Args:
                mesh_service: |mesh_service|
                session_id:  |mesh_session_uuid|
            """
            self.session_id: uuid.UUID = session_id
            self.mesh_service: core_pb2_grpc.MeshServiceStub = mesh_service

        async def __aenter__(self):
            """
            Used by the 'with' statement to open a session when entering 'with'
            |coro|

            Raises:
                grpc.RpcError: |grpc_rpc_error|
            """
            await self.open()
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            """
            Used by the 'with' statement to close a session when exiting 'with'
            |coro|

            Raises:
                grpc.RpcError: |grpc_rpc_error|
            """
            await self.close()

        async def open(self):
            """
            Request to open a session on the Mesh server
            |coro|

            Raises:
                grpc.RpcError: |grpc_rpc_error|
            """
            reply = await self.mesh_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = _from_proto_guid(reply)
            return reply

        async def close(self) -> None:
            """
            Request to close a session on the Mesh server
            |coro|

            Raises:
                grpc.RpcError: |grpc_rpc_error|

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
            the specified timeseries in the given interval.
            |coro|

            Args:
                start_time: |start_time|
                end_time: |end_time|
                mesh_object_id: |mesh_object_id|

            Raises:
                grpc.RpcError: |grpc_rpc_error|
                RuntimeError: |runtime_error|
                TypeError: |type_error|
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
                timeserie: The modified time series

            Raises:
                grpc.RpcError: |grpc_rpc_error|
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
            Request information associated with a raw |time_series_entry|
            |coro|

            Args:
                uuid_id : |mesh_object_uuid|
                path: |resource_path|
                timskey: |timskey|

            Note:
                This `path` is NOT the same as full name or the path in the Mesh object model,
                this `path` refers to its location in the resource catalog.

            Raises:
                grpc.RpcError: |grpc_rpc_error|

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
            which has a link to a time series, either calculated or raw

            Args:
                uuid_id: |mesh_object_uuid|
                path: |resource_path|
                timskey: |timskey|
                new_path: set new |resource_path|
                new_curve_type: set new |resource_curve_type|
                new_unit_of_measurement: set new |resource_unit_of_measurement|

            Note:
                Specify either uuid_id, path or timskey to a timeseries entry.
                Only one is needed.

            Note:
                Specify which ever of the new_* fields you want to update.

            Note:
                This `path` is NOT the same as full name or the path in the Mesh object model,
                this `path` refers to its location in the resource catalog.

            |coro|

            Raises:
                grpc.RpcError: |grpc_rpc_error|
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
                model: |mesh_object_model_name|
                uuid_id: |mesh_object_uuid|
                path: |mesh_object_full_name|

            Note:
                Specify model and either `uuid_id` or `path` to a timeseries attribute.
                Only one or uuid_id and path is needed.

            Raises:
                grpc.RpcError: |grpc_rpc_error|
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
                uuid_id: |mesh_object_uuid|
                path: |mesh_object_full_name|
                new_local_expression: set new |mesh_local_expression|
                new_timeseries_entry_id: set new |mesh_object_uuid| for the |time_series_entry|.

            Note:
                Specify either `uuid_id` or `path` to a timeseries attribute you want to update. Only one or uuid_id and path is needed.

            Note:
             Specify a new entry and/or a new local expression for the attribute.

            Raises:
                grpc.RpcError: |grpc_rpc_error|
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
                model: |mesh_object_model_name|
                query: |mesh_query|
                start_object_path: Start searching at the |mesh_object_full_name|
                start_object_guid: Start searching at the object with the |mesh_object_uuid|

            Note:
                Specify a model, a query using mesh query language and start object to start the search from,
                using either a path or a guid.

            Raises:
                grpc.RpcError: |grpc_rpc_error|
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

            ret_val = []
            async for reply in self.mesh_service.SearchTimeseriesAttributes(request):
                ret_val.append(reply)
            return ret_val

        async def rollback(self) -> None:
            """
            Discard changes in the :doc:`Mesh session <mesh_session>`. |coro|

            Raises:
                grpc.RpcError: |grpc_rpc_error|
            """
            await self.mesh_service.Rollback(_to_proto_guid(self.session_id))

        async def commit(self) -> None:
            """
            Commit changes made in the :doc:`Mesh session <mesh_session>` to the shared storage. |coro|

            Raises:
                grpc.RpcError: |grpc_rpc_error|
            """
            await self.mesh_service.Commit(_to_proto_guid(self.session_id))

        def forecast_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> ForecastFunctionsAsync:
            """Access to :ref:`mesh_functions:Forecast` functions.

            Args:
                relative_to: |relative_to|
                start_time: |start_time|
                end_time: |end_time|
            """
            return ForecastFunctionsAsync(self, relative_to, start_time, end_time)

        def history_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> HistoryFunctionsAsync:
            """Access to :ref:`mesh_functions:History` functions.

            Args:
                relative_to: |relative_to|
                start_time: |start_time|
                end_time: |end_time|
            """
            return HistoryFunctionsAsync(self, relative_to, start_time, end_time)

        def statistical_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> StatisticalFunctionsAsync:
            """Access to :ref:`mesh_functions:Statistical` functions.

            Args:
                relative_to: |relative_to|
                start_time: |start_time|
                end_time: |end_time|
            """
            return StatisticalFunctionsAsync(self, relative_to, start_time, end_time)

        def transform_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> TransformFunctionsAsync:
            """Access to :ref:`mesh_functions:Transformation` functions.

            Args:
                relative_to: |relative_to|
                start_time: |start_time|
                end_time: |end_time|
            """
            return TransformFunctionsAsync(self, relative_to, start_time, end_time)

    def __init__(self, host, port, root_pem_certificate: str = None,
                 authentication_parameters: Authentication.Parameters = None):
        """Create an asynchronous connection for communication with Mesh server.

        Args:
            host: |host|
            port: |port|
            root_pem_certificates: |root_pem_certificates|
            authentication_parameters: |authentication_parameters|

        Note:
            There are 3 possible async connection types:
            - insecure (without TLS)
            - with TLS
            - with TLS and Kerberos authentication (authentication requires TLS for encrypting auth tokens)
        """
        target = f'{host}:{port}'
        self.auth_metadata_plugin = None

        if not root_pem_certificate:
            # insecure connection (without TLS)
            channel = grpc.aio.insecure_channel(
                target=target
            )
        else:
            credentials: Credentials = Credentials(root_pem_certificate)

            # authentication requires TLS
            if authentication_parameters:
                self.auth_metadata_plugin = Authentication(
                    authentication_parameters, target, credentials.channel_creds)
                call_credentials = grpc.metadata_call_credentials(self.auth_metadata_plugin)

                composite_credentials = grpc.composite_channel_credentials(
                    credentials.channel_creds,
                    call_credentials,
                )

                # connection using TLS and Kerberos authentication
                channel = grpc.aio.secure_channel(
                    target=target,
                    credentials=composite_credentials
                )
            else:
                # connection using TLS (no Kerberos authentication)
                channel = grpc.aio.secure_channel(
                    target=target,
                    credentials=credentials.channel_creds
                )

        self.mesh_service = core_pb2_grpc.MeshServiceStub(channel)

    async def get_version(self):
        """
        Request version information of the connected Mesh server. |coro|

        Note:
            Does not require an open session.

        Raises:
            grpc.RpcError: |grpc_rpc_error|
        """
        response = await self.mesh_service.GetVersion(protobuf.empty_pb2.Empty())
        return response

    async def get_user_identity(self):
        """
        Request information about the user authorized to work with the Mesh server. |coro|

        Note:
            Does not require an open session.

        Raises:
            grpc.RpcError: |grpc_rpc_error|
        """
        response = await self.mesh_service.GetUserIdentity(protobuf.empty_pb2.Empty())
        return response

    async def revoke_access_token(self):
        """
        Revokes Mesh token if user no longer should be authenticated. |coro|

        Note:
            Does not require an open session.

        Raises:
            RuntimeError: |runtime_error| and the authentication is not configured
            grpc.RpcError: |grpc_rpc_error|
        """
        if self.auth_metadata_plugin is None:
            raise RuntimeError('Authentication not configured for this connection')

        await self.mesh_service.RevokeAccessToken(
            protobuf.wrappers_pb2.StringValue(value = self.auth_metadata_plugin.token))
        self.auth_metadata_plugin.delete_access_token()

    def create_session(self) -> Optional[Session]:
        """
        Create a new session.

        Note:
            This is only happens locally. No communication with the server is involved. You will need to open the session before it will be created on the Mesh server
        """
        return self.connect_to_session(session_id=None)

    def connect_to_session(self, session_id: uuid):
        """
        Create a session with a given session id, |mesh_session_uuid|.

        Args:
            session_id: |mesh_session_uuid|

        Note:
            This is only happens locally. No communication with the server is involved. Any subsequent use of the session object will communicate with the Mesh server. If the given session_id is a valid open session on the Mesh server, the session is now open and can be used.
        If the session_id is *not* a valid open session an exception will be raised when trying to use the session.

        """
        return self.Session(self.mesh_service, session_id)
