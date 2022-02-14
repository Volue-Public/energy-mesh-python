from volue.mesh._common import *
from volue.mesh import Authentication, Credentials, Timeseries
from volue.mesh.calc import history as History
from volue.mesh.calc import transform as Transform
from volue.mesh.proto.core.v1alpha import core_pb2, core_pb2_grpc
from typing import Optional, List
from google import protobuf
import datetime
import grpc
import uuid


class Connection:
    """ """

    class Session:
        """
        This class supports the with statement, because it's a contextmanager.
        """

        def __init__(
                self,
                mesh_service: core_pb2_grpc.MeshServiceStub,
                session_id: uuid = None):
            self.session_id: uuid = session_id
            self.mesh_service: core_pb2_grpc.MeshServiceStub = mesh_service

        def __enter__(self):
            """
            """
            self.open()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            """
            self.close()

        def open(self) -> None:
            """
            Raises:
                grpc.RpcError:
            """
            reply = self.mesh_service.StartSession(protobuf.empty_pb2.Empty())
            self.session_id = from_proto_guid(reply)

        def close(self) -> None:
            """
            Raises:
                grpc.RpcError:
            """
            self.mesh_service.EndSession(to_proto_guid(self.session_id))
            self.session_id = None

        def read_timeseries_points(self,
                                   start_time: datetime,
                                   end_time: datetime,
                                   timskey: int = None,
                                   uuid_id: uuid.UUID = None,
                                   full_name: str = None,
                                   history: History.Parameters = None,
                                   transformation: Transform.Parameters = None) -> Timeseries:
            """
            Reads timeseries points for the specified timeseries in the given interval.
            Transformed timeseries (returned when a `transformation` or `history` argument is provided)
            does not have the following fields set:
            - timskey
            - uuid_id
            - full_name

            Raises:
                grpc.RpcError:
                RuntimeError:
                TypeError:
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

            if history is not None and transformation is not None:
                raise TypeError("you cannot specify 'history' and 'transformation' at the same time")

            if history is not None:
                request = History.prepare_request(
                    self.session_id, start_time, end_time, object_id, history)
                response = self.mesh_service.RunCalculation(request)
                return History.parse_response(response)

            if transformation is not None:
                request = Transform.prepare_request(
                    self.session_id, start_time, end_time, object_id, transformation)
                response = self.mesh_service.RunCalculation(request)
                return Transform.parse_response(response)

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
            Raises:
                grpc.RpcError:
            """
            self.mesh_service.WriteTimeseries(
                core_pb2.WriteTimeseriesRequest(
                    session_id=to_proto_guid(self.session_id),
                    object_id=to_proto_object_id(timeserie),
                    timeseries=to_proto_timeseries(timeserie)
                ))

        # TODO: wrap core_pb2.TimeseriesEntry
        def get_timeseries_resource_info(self,
                                         uuid_id: uuid.UUID = None,
                                         path: str = None,
                                         timskey: int = None,
                                         ) -> core_pb2.TimeseriesEntry:
            """ """
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

        # TODO: is this a good name???
        def update_timeseries_resource_info(self,
                                            uuid_id: uuid.UUID = None,
                                            path: str = None,
                                            timskey: int = None,
                                            new_path: str = None,
                                            new_curve_type: Timeseries.Curve = None,
                                            new_unit_of_measurement: str = None
                                            ) -> None:
            """
            Specify either uuid_id, path or timskey to a timeseries entry. Only one is needed.

            Specify which ever of the new_* fields you want to update.
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

        # TODO: wrap  core_pb2.TimeseriesAttribute
        def get_timeseries_attribute(self,
                                     model: str = None,
                                     uuid_id: uuid.UUID = None,
                                     path: str = None
                                     ) -> core_pb2.TimeseriesAttribute:
            """
            Specify model and either uuid_id or path to a timeseries attribute. Only one or uuid_id and path is needed
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

        # TODO: Remove core_pb2 from interface
        def update_timeseries_attribute(self,
                                        uuid_id: uuid.UUID = None,
                                        path: str = None,
                                        new_local_expression: str = None,
                                        new_timeseries_entry_id: core_pb2.TimeseriesEntryId = None,
                                        ) -> None:
            """
            Specify either uuid_id or path to a timeseries attribute you want to update. Only one or uuid_id and path is needed.

            Specify a new entry and/or a new local expression for the attribute.
            Raises:
                grpc.RpcError:
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
            Specify a model, a query using mesh query language and start object to start the search from,
            using either a path or a guid.
            Args:
                model:
                query:
                start_object_path:
                start_object_guid:

            Returns:

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
            Raises:
                grpc.RpcError:
            """
            self.mesh_service.Rollback(to_proto_guid(self.session_id))

        def commit(self) -> None:
            """
            Raises:
                grpc.RpcError:
            """
            self.mesh_service.Commit(to_proto_guid(self.session_id))

    def __init__(self, host, port, secure_connection: bool,
                 authentication_parameters: Authentication.Parameters = None):
        """
        """
        target = f'{host}:{port}'
        self.auth_metadata_plugin = None

        # There are 3 possible connection types:
        # - insecure (without TLS)
        # - with TLS
        # - with TLS and Kerberos authentication
        #   (authentication requires TLS for encrypting auth tokens)
        if not secure_connection:
            # insecure connection (without TLS)
            channel = grpc.insecure_channel(
                target=target
            )
        else:
            credentials: Credentials = Credentials()

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

    # TODO wrap core_pb2.VersionInfo
    def get_version(self) -> core_pb2.VersionInfo:
        """
        """
        response = self.mesh_service.GetVersion(protobuf.empty_pb2.Empty())
        return response

    # TODO wrap core_pb2.UserIdentity
    def get_user_identity(self) -> core_pb2.UserIdentity:
        """
        """
        response = self.mesh_service.GetUserIdentity(protobuf.empty_pb2.Empty())
        return response

    def revoke_access_token(self) -> None:
        """
        Revokes Mesh token if no longer needed.

        Raises:
            RuntimeError: authentication not configured
        """
        if self.auth_metadata_plugin is None:
            raise RuntimeError('Authentication not configured for this connection')

        self.mesh_service.RevokeAccessToken(
            protobuf.wrappers_pb2.StringValue(value = self.auth_metadata_plugin.token))
        self.auth_metadata_plugin.delete_access_token()

    def create_session(self) -> Optional[Session]:
        """
        Raises:
            grpc.RpcError:
        """
        return self.connect_to_session(session_id=None)

    def connect_to_session(self, session_id: uuid) -> Optional[Session]:
        """
        """
        return self.Session(self.mesh_service, session_id)
