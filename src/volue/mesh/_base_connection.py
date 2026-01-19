import abc
import uuid
from typing import TypeVar

import grpc

from volue.mesh.proto.auth.v1alpha import auth_pb2, auth_pb2_grpc
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc
from volue.mesh.proto.calc.v1alpha import calc_pb2_grpc
from volue.mesh.proto.config.v1alpha import config_pb2, config_pb2_grpc
from volue.mesh.proto.hydsim.v1alpha import hydsim_pb2_grpc
from volue.mesh.proto.model.v1alpha import model_pb2_grpc
from volue.mesh.proto.model_definition.v1alpha import model_definition_pb2_grpc
from volue.mesh.proto.session.v1alpha import session_pb2_grpc
from volue.mesh.proto.time_series.v1alpha import time_series_pb2_grpc

from . import _authentication
from ._authentication import Authentication, ExternalAccessTokenPlugin

C = TypeVar("C", bound="Connection")


class Connection(abc.ABC):
    """A connection to a Mesh server.

    There are four primary types of connections, insecure, TLS encrypted,
    Kerberos authenticated (with TLS encryption) and with providing externally
    obtained token (with TLS encryption).
    These can be instantiated as follows::

        insecure = mesh.Connection.insecure('localhost:50051')
        tls = mesh.Connection.with_tls('localhost:50051', root_certificates)
        kerberos = mesh.Connection.with_kerberos('localhost:50051',
                                                 root_certificates,
                                                 'HOST/hostname.ad.examplecompany.com',
                                                 'ad\\user.name')
        token = mesh.Connection.with_external_access_token('localhost:50051',
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

    @staticmethod
    def _get_grpc_channel_options(max_receive_message_length: int | None):
        """Create a secure gRPC channel.

        Derived classes should implement this using either grpc.aio.secure_channel
        or grpc.secure_channel depending on desired behavior.
        """
        return (
            [
                ("grpc.max_receive_message_length", max_receive_message_length),
            ]
            if max_receive_message_length
            else []
        )

    def __init__(
        self,
        host=None,
        port=None,
        tls_root_pem_cert=None,
        authentication_parameters: Authentication.Parameters | None = None,
        channel=None,
        auth_metadata_plugin=None,
    ):
        """Create a connection for communication with Mesh server.

        Args:
            host: Mesh server host name in the form an IP or domain name
            port: Mesh server port number for gRPC communication
            tls_root_pem_cert: PEM-encoded root certificate(s) as a byte string.
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
            self.auth_service = auth_pb2_grpc.AuthenticationServiceStub(channel)
            self.availability_service = availability_pb2_grpc.AvailabilityServiceStub(
                channel
            )
            self.calc_service = calc_pb2_grpc.CalculationServiceStub(channel)
            self.config_service = config_pb2_grpc.ConfigurationServiceStub(channel)
            self.hydsim_service = hydsim_pb2_grpc.HydsimServiceStub(channel)
            self.model_service = model_pb2_grpc.ModelServiceStub(channel)
            self.model_definition_service = (
                model_definition_pb2_grpc.ModelDefinitionServiceStub(channel)
            )
            self.session_service = session_pb2_grpc.SessionServiceStub(channel)
            self.time_series_service = time_series_pb2_grpc.TimeseriesServiceStub(
                channel
            )
            return

        target = f"{host}:{port}"

        # There are 4 possible connection types:
        # - insecure (without TLS)
        # - with TLS
        # - with TLS and Kerberos authentication
        #   (authentication requires TLS for encrypting auth tokens)
        # - with TLS and externally obtained access tokens
        #   (requires TLS for encrypting access tokens)
        if not tls_root_pem_cert:
            # insecure connection (without TLS)
            channel = self._insecure_grpc_channel(target=target)
        else:
            channel_credentials = grpc.ssl_channel_credentials(
                root_certificates=tls_root_pem_cert
            )

            # authentication requires TLS
            if authentication_parameters:
                self.auth_metadata_plugin = Authentication(
                    authentication_parameters, target, channel_credentials
                )
                call_credentials = grpc.metadata_call_credentials(
                    self.auth_metadata_plugin
                )

                composite_credentials = grpc.composite_channel_credentials(
                    channel_credentials,
                    call_credentials,
                )

                # connection using TLS and Kerberos authentication
                channel = self._secure_grpc_channel(
                    target=target, credentials=composite_credentials
                )
            else:
                # connection using TLS (no Kerberos authentication)
                channel = self._secure_grpc_channel(
                    target=target, credentials=channel_credentials
                )

        self.auth_service = auth_pb2_grpc.AuthenticationServiceStub(channel)
        self.availability_service = availability_pb2_grpc.AvailabilityServiceStub(
            channel
        )
        self.calc_service = calc_pb2_grpc.CalculationServiceStub(channel)
        self.config_service = config_pb2_grpc.ConfigurationServiceStub(channel)
        self.hydsim_service = hydsim_pb2_grpc.HydsimServiceStub(channel)
        self.model_service = model_pb2_grpc.ModelServiceStub(channel)
        self.model_definition_service = (
            model_definition_pb2_grpc.ModelDefinitionServiceStub(channel)
        )
        self.session_service = session_pb2_grpc.SessionServiceStub(channel)
        self.time_series_service = time_series_pb2_grpc.TimeseriesServiceStub(channel)

    @classmethod
    def insecure(
        cls: C, target: str, *, grpc_max_receive_message_length: int | None = None
    ) -> C:
        """Creates an insecure connection to a Mesh server.

        Args:
            target: The server address.
            grpc_max_receive_message_length: Maximum inbound gRPC message size
                in bytes. By default the maximum inbound gRPC message size is 4MB.
        """

        options = cls._get_grpc_channel_options(grpc_max_receive_message_length)
        channel = cls._insecure_grpc_channel(target=target, options=options)
        return cls(channel=channel)

    @classmethod
    def with_tls(
        cls: C,
        target: str,
        root_certificates: str | None,
        *,
        grpc_max_receive_message_length: int | None = None,
    ) -> C:
        """Creates an encrypted connection to a Mesh server.

        Args:
            target: The server address.
            root_certificates: The PEM-encoded TLS root certificates as a byte
                string, or None to retrieve them from a default location chosen
                by the gRPC runtime.
            grpc_max_receive_message_length: Maximum inbound gRPC message size
                in bytes. By default the maximum inbound gRPC message size is 4MB.
        """
        credentials = grpc.ssl_channel_credentials(root_certificates)
        options = cls._get_grpc_channel_options(grpc_max_receive_message_length)
        channel = cls._secure_grpc_channel(
            target=target, credentials=credentials, options=options
        )
        return cls(channel=channel)

    @classmethod
    def with_kerberos(
        cls: C,
        target: str,
        root_certificates: str | None,
        service_principal: str,
        user_principal: str | None = None,
        *,
        grpc_max_receive_message_length: int | None = None,
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
            grpc_max_receive_message_length: Maximum inbound gRPC message size
                in bytes. By default the maximum inbound gRPC message size is 4MB.
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
        options = cls._get_grpc_channel_options(grpc_max_receive_message_length)
        channel = cls._secure_grpc_channel(
            target=target, credentials=credentials, options=options
        )
        return cls(channel=channel, auth_metadata_plugin=auth_metadata_plugin)

    @classmethod
    def with_external_access_token(
        cls: C,
        target: str,
        root_certificates: str | None,
        access_token: str,
        *,
        grpc_max_receive_message_length: int | None = None,
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
            grpc_max_receive_message_length: Maximum inbound gRPC message size
                in bytes. By default the maximum inbound gRPC message size is 4MB.
        """
        ssl_credentials = grpc.ssl_channel_credentials(root_certificates)
        auth_metadata_plugin = ExternalAccessTokenPlugin(access_token)
        call_credentials = grpc.metadata_call_credentials(auth_metadata_plugin)
        credentials = grpc.composite_channel_credentials(
            ssl_credentials, call_credentials
        )
        options = cls._get_grpc_channel_options(grpc_max_receive_message_length)
        channel = cls._secure_grpc_channel(
            target=target, credentials=credentials, options=options
        )
        return cls(channel=channel, auth_metadata_plugin=auth_metadata_plugin)

    @abc.abstractmethod
    def get_version(self) -> config_pb2.VersionInfo:
        """Request version information of the connected Mesh server.

        Note:
            Does not require an open session.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def get_user_identity(self) -> auth_pb2.UserIdentity:
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
