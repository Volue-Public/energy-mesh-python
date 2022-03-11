from volue.mesh._common import *
from volue.mesh import Authentication, Credentials, Timeseries
from volue.mesh.calc.forecast import ForecastFunctions
from volue.mesh.calc.history import HistoryFunctions
from volue.mesh.calc.statistical import StatisticalFunctions
from volue.mesh.calc.transform import TransformFunctions
from volue.mesh.proto.core.v1alpha import core_pb2, core_pb2_grpc
from typing import Optional, List
from google import protobuf
import datetime
import grpc
import uuid


class Connection:
    """Represents a connection to a Mesh server."""

    class Session:
        """
        This class supports the with statement, because it's a contextmanager.
        """

        def __init__(
                self,
                mesh_service: core_pb2_grpc.MeshServiceStub,
                session_id: uuid = None):
            """
            Initialize a session object for working with the Mesh server.
            Args:
                mesh_service: the gRPC generated mesh service use to communicate with the Mesh server
                session_id:  the id of the session you are (or want to) be connected to
            """
            self.session_id: uuid = session_id
            self.mesh_service: core_pb2_grpc.MeshServiceStub = mesh_service

        def __enter__(self):
            """
            Used by the 'with' statement to open a session when entering 'with'
            """
            self.open()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            Used by the 'with' statement to close a session when exiting 'with'
            """
            self.close()

        def open(self) -> None:
            """
            Request to open a new session on the Mesh server
            Raises:
                grpc.RpcError: Error message raised if request could not be completed
            """
            reply = self.mesh_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = from_proto_guid(reply)

        def close(self) -> None:
            """
            Request to close a session on the Mesh server
            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            self.mesh_service.EndSession(to_proto_guid(self.session_id))
            self.session_id = None

        def read_timeseries_points(self,
                                   start_time: datetime,
                                   end_time: datetime,
                                   timskey: int = None,
                                   uuid_id: uuid.UUID = None,
                                   full_name: str = None) -> Timeseries:
            """
            Reads time series points for the specified timeseries in the given interval.

            Raises:
                grpc.RpcError: error message raised if request could not be completed
                RuntimeError: error message raised if the input is not valid
                TypeError: error message raised if the returned result from the request is not as expected
            """
            object_id = core_pb2.ObjectId()
            if timskey is not None:
                object_id.timskey = timskey
            elif uuid_id is not None:
                object_id.guid.CopyFrom(to_proto_guid(uuid_id))
            elif full_name is not None:
                object_id.full_name = full_name
            else:
                raise TypeError("need to specify either timskey, uuid_id or full_name")

            response = self.mesh_service.ReadTimeseries(
                core_pb2.ReadTimeseriesRequest(
                    session_id=to_proto_guid(self.session_id),
                    object_id=object_id,
                    interval=to_protobuf_utcinterval(start_time, end_time)
                ))

            timeseries = read_proto_reply(response)
            if len(timeseries) != 1:
                raise RuntimeError(
                    f"invalid result from 'read_timeseries_points', expected 1 timeseries, but got {len(timeseries)}")

            return timeseries[0]

        def write_timeseries_points(self, timeserie: Timeseries) -> None:
            """
            Writes time series points for the specified timeseries in the given interval.

            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            self.mesh_service.WriteTimeseries(
                core_pb2.WriteTimeseriesRequest(
                    session_id=to_proto_guid(self.session_id),
                    object_id=to_proto_object_id(timeserie),
                    timeseries=to_proto_timeseries(timeserie)
                ))

        def get_timeseries_resource_info(self,
                                         uuid_id: uuid.UUID = None,
                                         path: str = None,
                                         timskey: int = None,
                                         ) -> core_pb2.TimeseriesEntry:
            """
            Request information associated with a raw time series entry

            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            entry_id = core_pb2.TimeseriesEntryId()
            if timskey is not None:
                entry_id.timeseries_key = timskey
            elif uuid_id is not None:
                entry_id.guid.CopyFrom(to_proto_guid(uuid_id))
            elif path is not None:
                entry_id.path = path
            else:
                raise Exception("Need to specify either uuid_id, timeseries_key or path.")

            reply = self.mesh_service.GetTimeseriesEntry(
                core_pb2.GetTimeseriesEntryRequest(
                    session_id=to_proto_guid(self.session_id),
                    entry_id=entry_id
                ))
            return reply

        def update_timeseries_resource_info(self,
                                            uuid_id: uuid.UUID = None,
                                            path: str = None,
                                            timskey: int = None,
                                            new_path: str = None,
                                            new_curve_type: Timeseries.Curve = None,
                                            new_unit_of_measurement: str = None
                                            ) -> None:
            """
            Request information associated with a Mesh object which has a link to a time series, either calulated or raw

            Specify either uuid_id, path or timskey to a timeseries entry. Only one is needed.

            Specify which ever of the new_* fields you want to update.

            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            entry_id = core_pb2.TimeseriesEntryId()
            if timskey is not None:
                entry_id.timeseries_key = timskey
            elif uuid_id is not None:
                entry_id.guid.CopyFrom(to_proto_guid(uuid_id))
            elif path is not None:
                entry_id.path = path
            else:
                raise Exception("Need to specify either uuid_id, timeseries_key or path.")

            request = core_pb2.UpdateTimeseriesEntryRequest(
                session_id=to_proto_guid(self.session_id),
                entry_id=entry_id
            )

            paths = []
            if new_path is not None:
                request.new_path = new_path
                paths.append("new_path")
            if new_curve_type is not None:
                request.new_curve_type.CopyFrom(to_proto_curve_type(new_curve_type))
                paths.append("new_curve_type")
            if new_unit_of_measurement is not None:
                request.new_unit_of_measurement = new_unit_of_measurement
                paths.append("new_unit_of_measurement")

            request.field_mask.CopyFrom(protobuf.field_mask_pb2.FieldMask(paths=paths))

            self.mesh_service.UpdateTimeseriesEntry(request)

        def get_timeseries_attribute(self,
                                     model: str = None,
                                     uuid_id: uuid.UUID = None,
                                     path: str = None
                                     ) -> core_pb2.TimeseriesAttribute:
            """
            Request information associated with a Mesh object attribute

            Specify model and either uuid_id or path to a timeseries attribute. Only one or uuid_id and path is needed

            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            attribute_id = core_pb2.AttributeId()
            if uuid_id is not None:
                attribute_id.id.CopyFrom(to_proto_guid(uuid_id))
            elif path is not None:
                attribute_id.path = path
            else:
                raise Exception("Need to specify either uuid_id or path.")

            reply = self.mesh_service.GetTimeseriesAttribute(
                core_pb2.GetTimeseriesAttributeRequest(
                    session_id=to_proto_guid(self.session_id),
                    model=model,
                    attribute_id=attribute_id
                )
            )
            return reply

        def update_timeseries_attribute(self,
                                        uuid_id: uuid.UUID = None,
                                        path: str = None,
                                        new_local_expression: str = None,
                                        new_timeseries_entry_id: core_pb2.TimeseriesEntryId = None,
                                        ) -> None:
            """
            Update information associated with a Mesh object attribute

            Specify either uuid_id or path to a timeseries attribute you want to update. Only one or uuid_id and path is needed.

            Specify a new entry and/or a new local expression for the attribute.

            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            attribute_id = core_pb2.AttributeId()
            if uuid_id is not None:
                attribute_id.id.CopyFrom(to_proto_guid(uuid_id))
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

            self.mesh_service.UpdateTimeseriesAttribute(
                core_pb2.UpdateTimeseriesAttributeRequest(
                    session_id=to_proto_guid(self.session_id),
                    attribute_id=attribute_id,
                    field_mask=field_mask,
                    new_timeseries_entry_id=new_timeseries_entry_id,
                    new_local_expression=new_local_expression
                )
            )

        def search_for_timeseries_attribute(self,
                                            model: str,
                                            query: str,
                                            start_object_path: str = None,
                                            start_object_guid: uuid.UUID = None
                                            ) -> List[core_pb2.TimeseriesAttribute]:
            """
            Use the Mesh search language to find Mesh object attributes in the Mesh object model

            Specify a model, a query using mesh query language and start object to start the search from,
            using either a path or a guid.

            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            request = core_pb2.SearchTimeseriesAttributesRequest(
                session_id=to_proto_guid(self.session_id),
                model_name=model,
                query=query
            )
            if start_object_path is not None:
                request.start_object_path = start_object_path
            elif start_object_guid is not None:
                request.start_object_guid.CopyFrom(to_proto_guid(start_object_guid))
            else:
                raise Exception("Need to specify either start_object_path or start_object_guid")

            replies = self.mesh_service.SearchTimeseriesAttributes(request)
            ret_val = []
            for reply in replies:
                ret_val.append(reply)
            return ret_val

        def rollback(self) -> None:
            """
            Discard changes in the session.

            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            self.mesh_service.Rollback(to_proto_guid(self.session_id))

        def commit(self) -> None:
            """
            Commit changes made in the session to the shared storage

            Raises:
                grpc.RpcError: error message raised if request could not be completed
            """
            self.mesh_service.Commit(to_proto_guid(self.session_id))

        def forecast_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> ForecastFunctions:
            """Access to all forecast functions"""
            return ForecastFunctions(self, relative_to, start_time, end_time)

        def history_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> HistoryFunctions:
            """Access to all history functions"""
            return HistoryFunctions(self, relative_to, start_time, end_time)

        def statistical_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> StatisticalFunctions:
            """Access to all statistical functions"""
            return StatisticalFunctions(self, relative_to, start_time, end_time)

        def transform_functions(self, relative_to: MeshObjectId, start_time: datetime, end_time: datetime) -> TransformFunctions:
            """Access to all transformation functions"""
            return TransformFunctions(self, relative_to, start_time, end_time)

    def __init__(self, host, port, root_pem_certificate: str = None,
                 authentication_parameters: Authentication.Parameters = None):
        """Create a synchronous connection for communication with Mesh server.

        Args:
            host: Mesh gRPC server host name.
            port: Mesh gRPC server port.
            root_pem_certificates: PEM-encoded root certificate(s) as a byte string.
                If this argument is set then a secured connection will be created,
                otherwise it will be an insecure connection.
            authentication_parameters: Authentication parameters.

        Returns:
            A synchronous connection object.
        """
        target = f'{host}:{port}'
        self.auth_metadata_plugin = None

        # There are 3 possible connection types:
        # - insecure (without TLS)
        # - with TLS
        # - with TLS and Kerberos authentication
        #   (authentication requires TLS for encrypting auth tokens)
        if not root_pem_certificate:
            # insecure connection (without TLS)
            channel = grpc.insecure_channel(
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
                channel = grpc.secure_channel(
                    target=target,
                    credentials=composite_credentials
                )
            else:
                # connection using TLS (no Kerberos authentication)
                channel = grpc.secure_channel(
                    target=target,
                    credentials=credentials.channel_creds
                )

        self.mesh_service = core_pb2_grpc.MeshServiceStub(channel)

    def get_version(self) -> core_pb2.VersionInfo:
        """
        Request version information of the connected Mesh server.

        Note: does not require a session.

        Raises:
            grpc.RpcError: error message raised if request could not be completed
        """
        response = self.mesh_service.GetVersion(protobuf.empty_pb2.Empty())
        return response

    def get_user_identity(self) -> core_pb2.UserIdentity:
        """
        Request information about the user authorized to work with the Mesh server.

        Note: does not require a session.

        Raises:
            grpc.RpcError: error message raised if request could not be completed
        """
        response = self.mesh_service.GetUserIdentity(protobuf.empty_pb2.Empty())
        return response

    def revoke_access_token(self) -> None:
        """
        Revokes Mesh token if user no longer should be authenticated.

        Note: does not require a session.

        Raises:
            RuntimeError: authentication not configured
            grpc.RpcError: error message raised if request could not be completed
        """
        if self.auth_metadata_plugin is None:
            raise RuntimeError('Authentication not configured for this connection')

        self.mesh_service.RevokeAccessToken(
            protobuf.wrappers_pb2.StringValue(value = self.auth_metadata_plugin.token))
        self.auth_metadata_plugin.delete_access_token()

    def create_session(self) -> Optional[Session]:
        """
        Create a new session.

        Note: this is only happens locally,
        you will need to open the session before it will be created on the Mesh server
        """
        return self.connect_to_session(session_id=None)

    def connect_to_session(self, session_id: uuid) -> Optional[Session]:
        """
        Create a session with a given id.

        If the given session_id is a valid open session on the Mesh server, the session is now open and can be used.
        If the session_id is *not* a valid open session an exception will be raised when trying to use the session.

        Note: This is only happens locally.
        Any subsequent use of the session object will communicate with the Mesh server.

        """
        return self.Session(self.mesh_service, session_id)
