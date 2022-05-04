import abc
import uuid

import grpc

from ._authentication import Authentication
from ._credentials import Credentials
from .proto.core.v1alpha import core_pb2, core_pb2_grpc


class Connection(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def _insecure_grpc_channel(*args, **kwargs):
        """Create an insecure gRPC channel.

        Derived classes should implement this using either grpc.aio.insecure_channel
        or grpc.insecure_channel depending on desired behaviour.
        """

    @staticmethod
    @abc.abstractmethod
    def _secure_grpc_channel(*args, **kwargs):
        """Create an insecure gRPC channel.

        Derived classes should implement this using either grpc.aio.secure_channel
        or grpc.secure_channel depending on desired behaviour.
        """

    def __init__(self, host, port, root_pem_certificate=None,
                 authentication_parameters: Authentication.Parameters = None):
        """Create a connection for communication with Mesh server.

        Args:
            host (str): Mesh server host name in the form an IP or domain name
            port (int): Mesh server port number for gRPC communication
            root_pem_certificate (str): PEM-encoded root certificate(s) as a byte string.
                If this argument is set then a secured connection will be created,
                otherwise it will be an insecure connection.
            authentication_parameters (Authentication.Parameters): TODO

        Note:
            There are 3 possible connection types:
            - insecure (without TLS)
            - with TLS
            - with TLS and Kerberos authentication (authentication requires TLS for encrypting auth tokens)
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
            channel = self._insecure_grpc_channel(
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
                channel = self._secure_grpc_channel(
                    target=target,
                    credentials=composite_credentials
                )
            else:
                # connection using TLS (no Kerberos authentication)
                channel = self._secure_grpc_channel(
                    target=target,
                    credentials=credentials.channel_creds
                )

        self.mesh_service = core_pb2_grpc.MeshServiceStub(channel)

    @abc.abstractmethod
    def get_version(self) -> core_pb2.VersionInfo:
        """Request version information of the connected Mesh server.

        Note:
            Does not require an open session.

        Raises:
            grpc.RpcError:  Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def get_user_identity(self) -> core_pb2.UserIdentity:
        """Request information about the user authorized to work with the Mesh server.

        Note:
            Does not require an open session.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not
                be completed
        """

    @abc.abstractmethod
    def revoke_access_token(self) -> None:
        """Revokes Mesh token if user no longer should be authenticated.

        Note:
            Does not require an open session.

        Raises:
            RuntimeError: Error message raised if the input is not valid and
                the authentication is not configured
            grpc.RpcError: Error message raised if the gRPC request could not
                be completed
        """

    @abc.abstractmethod
    def create_session(self):
        """Create a new session.

        Note:
            This is handled locally. No communication with the server is involved.
            You will need to open the session before it will be created on the Mesh server
        """

    @abc.abstractmethod
    def connect_to_session(self, session_id: uuid.UUID):
        """Create a session with a given session id, the id of the session you are (or want to be) connected to.

        Args:
            session_id (uuid.UUID): The id of the session you are (or want to be) connected to.

        Note:
            This is handled locally. No communication with the server is involved.
            Any subsequent use of the session object will communicate with the
            Mesh server. If the given session_id is a valid open session on the
            Mesh server, the session is now open and can be used. If the session_id
            is *not* a valid open session an exception will be raised when trying to
            use the session.
        """
