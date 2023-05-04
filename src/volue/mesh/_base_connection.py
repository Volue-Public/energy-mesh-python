import abc
import uuid
from typing import Optional, TypeVar

import grpc

from . import _authentication
from ._authentication import Authentication, ExternalAccessTokenPlugin
from ._credentials import Credentials
from .proto.core.v1alpha import core_pb2, core_pb2_grpc

C = TypeVar("C", bound="Connection")


class Connection(abc.ABC):
    """A connection to a Mesh server.

    There are four primary types of connections, insecure, TLS encrypted,
    Kerberos authenticated (with TLS encryption) and with providing externally
    obtained token (with TLS encryption).
    These can be instantiated as follows::

        insecure = mesh.Connection.insecure('localhost:50051')
        tls = mesh.Connection.with_tls('localhost:50051', root_certificates)
        kerberos = mesh.Connection.with_kerberos('localhost',
                                                 root_certificates,
                                                 'HOST/hostname.ad.examplecompany.com',
                                                 'ad\\user.name')
        token = mesh.Connection.with_external_access_token('localhost',
                                                           root_certificates,
                                                           'eyJ0eXAiOi...')

    The target address uses `gRPC Name Resolution <naming>`_. In general this
    means that 'host:port' works as expected.

    See :py:meth:`Connection.insecure()`, :py:meth:`Connection.with_tls()`,
    :py:meth:`Connection.with_kerberos()` and
    :py:meth:`Connection.with_external_access_token()` for more information on
    the connection variants.

    .. _naming: https://github.com/grpc/grpc/blob/master/doc/naming.md
    """

    @staticmethod
    @abc.abstractmethod
    def _insecure_grpc_channel(*args, **kwargs):
        """Create an insecure gRPC channel.

        Derived classes should implement this using either grpc.aio.insecure_channel
        or grpc.insecure_channel depending on desired behavior.
        """

    @staticmethod
    @abc.abstractmethod
    def _secure_grpc_channel(*args, **kwargs):
        """Create a secure gRPC channel.

        Derived classes should implement this using either grpc.aio.secure_channel
        or grpc.secure_channel depending on desired behavior.
        """

    def __init__(
        self,
        host=None,
        port=None,
        root_pem_certificate=None,
        authentication_parameters: Optional[Authentication.Parameters] = None,
        channel=None,
        auth_metadata_plugin=None,
    ):
        """Create a connection for communication with Mesh server.

        Args:
            host: Mesh server host name in the form an IP or domain name
            port: Mesh server port number for gRPC communication
            root_pem_certificate: PEM-encoded root certificate(s) as a byte string.
                If this argument is set then a secured connection will be created,
                otherwise it will be an insecure connection.
            authentication_parameters: TODO

        Note:
            There are 4 possible connection types:
            - insecure (without TLS)
            - with TLS
            - with TLS and Kerberos authentication (authentication requires TLS for encrypting auth tokens)
            - with TLS and externally obtained access tokens (requires TLS for encrypting access tokens)
        """
        self.auth_metadata_plugin = auth_metadata_plugin

        if channel is not None:
            self.mesh_service = core_pb2_grpc.MeshServiceStub(channel)
            return

        target = f"{host}:{port}"

        # There are 4 possible connection types:
        # - insecure (without TLS)
        # - with TLS
        # - with TLS and Kerberos authentication
        #   (authentication requires TLS for encrypting auth tokens)
        # - with TLS and externally obtained access tokens
        #   (requires TLS for encrypting access tokens)
        if not root_pem_certificate:
            # insecure connection (without TLS)
            channel = self._insecure_grpc_channel(target=target)
        else:
            credentials: Credentials = Credentials(root_pem_certificate)

            # authentication requires TLS
            if authentication_parameters:
                self.auth_metadata_plugin = Authentication(
                    authentication_parameters, target, credentials.channel_creds
                )
                call_credentials = grpc.metadata_call_credentials(
                    self.auth_metadata_plugin
                )

                composite_credentials = grpc.composite_channel_credentials(
                    credentials.channel_creds,
                    call_credentials,
                )

                # connection using TLS and Kerberos authentication
                channel = self._secure_grpc_channel(
                    target=target, credentials=composite_credentials
                )
            else:
                # connection using TLS (no Kerberos authentication)
                channel = self._secure_grpc_channel(
                    target=target, credentials=credentials.channel_creds
                )

        self.mesh_service = core_pb2_grpc.MeshServiceStub(channel)

    @classmethod
    def insecure(cls: C, target: str) -> C:
        """Creates an insecure connection to a Mesh server.

        Args:
            target: The server address.
        """
        channel = cls._insecure_grpc_channel(target)
        return cls(channel=channel)

    @classmethod
    def with_tls(cls: C, target: str, root_certificates: Optional[str]) -> C:
        """Creates an encrypted connection to a Mesh server.

        Args:
            target: The server address.
            root_certificates: The PEM-encoded TLS root certificates as a byte
                string, or None to retrieve them from a default location chosen
                by the gRPC runtime.
        """
        credentials = grpc.ssl_channel_credentials(root_certificates)
        channel = cls._secure_grpc_channel(target, credentials)
        return cls(channel=channel)

    @classmethod
    def with_kerberos(
        cls: C,
        target: str,
        root_certificates: Optional[str],
        service_principal: str,
        user_principal: str,
    ) -> C:
        """Creates an encrypted and authenticated connection to a Mesh server.

        This call will perform a Kerberos authentication flow towards Active
        Directory and the Mesh server using the supplied principal names. If
        successful the returned connection will then use that authenticated
        identity for all calls to the Mesh service.

        The authentication is time-limited. When close to expiration the
        library will perform another authentication flow as part of the next
        gRPC call. This will lead to increased latency on calls where a
        re-authentication is necessary, but should otherwise be invisible to
        the user.

        Args:
            target: The server address.
            root_certificates: The PEM-encoded TLS root certificates as a byte
                string, or None to retrieve them from a default location chosen
                by the gRPC runtime.
            service_principal: The Kerberos service principal name for the Mesh
                service. For example 'HOST\\server.at.host'.
            user_principal: The Kerberos user principal name. For example
                'ad\\user`.
        """
        ssl_credentials = grpc.ssl_channel_credentials(root_certificates)
        auth_params = _authentication.Authentication.Parameters(
            service_principal, user_principal
        )
        auth_metadata_plugin = Authentication(auth_params, target, ssl_credentials)
        call_credentials = grpc.metadata_call_credentials(auth_metadata_plugin)
        credentials = grpc.composite_channel_credentials(
            ssl_credentials, call_credentials
        )
        channel = cls._secure_grpc_channel(target, credentials)
        return cls(channel=channel, auth_metadata_plugin=auth_metadata_plugin)

    @classmethod
    def with_external_access_token(
        cls: C, target: str, root_certificates: Optional[str], access_token: str
    ) -> C:
        """Creates an encrypted connection to a Mesh server and will add
        provided access token to authorization header to each server request.

        This is used for setups with external identity providers that generate
        access tokens to the Mesh server.

        Args:
            target: The server address.
            root_certificates: The PEM-encoded TLS root certificates as a byte
                string, or None to retrieve them from a default location chosen
                by the gRPC runtime.
            access_token: Token obtained externally, used to get access to Mesh
                server.
        """
        ssl_credentials = grpc.ssl_channel_credentials(root_certificates)
        auth_metadata_plugin = ExternalAccessTokenPlugin(access_token)
        call_credentials = grpc.metadata_call_credentials(auth_metadata_plugin)
        credentials = grpc.composite_channel_credentials(
            ssl_credentials, call_credentials
        )
        channel = cls._secure_grpc_channel(target, credentials)
        return cls(channel=channel, auth_metadata_plugin=auth_metadata_plugin)

    @classmethod
    def _with_fake_identity(
        cls, target: str, root_certificates: Optional[str], name: str
    ):
        ssl_credentials = grpc.ssl_channel_credentials(root_certificates)
        auth_metadata_plugin = _authentication.FakeIdentityPlugin(
            target, ssl_credentials, name
        )
        call_credentials = grpc.metadata_call_credentials(auth_metadata_plugin)
        credentials = grpc.composite_channel_credentials(
            ssl_credentials, call_credentials
        )
        channel = cls._secure_grpc_channel(target, credentials)
        return cls(channel=channel, auth_metadata_plugin=auth_metadata_plugin)

    @abc.abstractmethod
    def get_version(self) -> core_pb2.VersionInfo:
        """Request version information of the connected Mesh server.

        Note:
            Does not require an open session.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def get_user_identity(self) -> core_pb2.UserIdentity:
        """Request information about the user authorized to work with the Mesh server.

        Note:
            Does not require an open session.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not
                be completed.
        """

    @abc.abstractmethod
    def update_external_access_token(self, access_token: str) -> None:
        """Updates external access token used for connection to Mesh.

        Args:
            access_token: New access token to be added to authorization header
                to each server request.

        Note:
            Does not require an open session.

        Raises:
            RuntimeError: Error message raised if the connection is not using
                external access token.
        """

    @abc.abstractmethod
    def revoke_access_token(self) -> None:
        """Revokes Mesh token if user no longer should be authenticated.

        Note:
            Does not require an open session.

        Raises:
            RuntimeError: Error message raised if the connection is not using
                Kerberos authentication.
            grpc.RpcError: Error message raised if the gRPC request could not
                be completed.
        """

    @abc.abstractmethod
    def create_session(self):
        """Create a new session.

        Note:
            This is handled locally. No communication with the server is involved.
            You will need to open the session before it will be created on the Mesh server.
        """

    @abc.abstractmethod
    def connect_to_session(self, session_id: uuid.UUID):
        """Create a session with a given session id, the id of the session you are (or want to be) connected to.

        Args:
            session_id: The id of the session you are (or want to be) connected to.

        Note:
            This is handled locally. No communication with the server is involved.
            Any subsequent use of the session object will communicate with the
            Mesh server. If the given session_id is a valid open session on the
            Mesh server, the session is now open and can be used. If the session_id
            is *not* a valid open session an exception will be raised when trying to
            use the session.
        """
