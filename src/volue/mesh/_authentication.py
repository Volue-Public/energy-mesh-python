"""
Mesh authentication functionality.
"""

import base64
import threading
import typing
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from sys import platform
from typing import Optional

import grpc
from google import protobuf

from volue.mesh.proto.core.v1alpha import core_pb2, core_pb2_grpc

if platform.startswith("win32"):
    import winkerberos as kerberos
elif platform.startswith("linux"):
    import kerberos


class Authentication(grpc.AuthMetadataPlugin):
    """
    Authentication services for authentication and authorization to Mesh server using `kerberos <https://en.wikipedia.org/wiki/Kerberos_(protocol)>`_.

    The flow is as follows:

    1. Obtain token from Kerberos to access specified service (SPN) with Mesh server running on it.
    2. Send this token to Mesh gRPC server (using AuthenticateKerberos).
    3. In return Mesh may respond with:
        a. Server challenge to be verified and processed by client (using Kerberos). In this case the authentication is not yet completed and client should respond to the server with next Kerberos generated token.
        b. Mesh token - to be used in subsequent calls to Mesh that require authentication.

    Note:
        Token duration - tokens are valid for **1 hour**. After this time a new token needs to be acquired.
    """

    @dataclass
    class Parameters:
        """
        Authentication parameters.

        Args:
            service_principal: Name of an active directory service, e.g.: 'HOST/hostname.ad.examplecompany.com.
            user_principal: Name of an active directory user, e.g.: 'ad\\user.name'.
        """

        service_principal: str
        user_principal: Optional[str] = None

    class KerberosTokenIterator:
        """
        Kerberos token iterator to be used with AuthenticateKerberos streaming gRPC.
        Sends tokens to be processed by the Mesh server and processes tokens
        received from the server.
        """

        def __init__(self, service_principal: str, user_principal: str):
            """
            Args:
                service_principal: Name of an active directory service, e.g.: 'HOST/hostname.ad.examplecompany.com.
                user_principal: Name of an active directory user, e.g.: 'ad\\user.name'.
            """
            self.krb_context = None
            self.first_iteration: bool = True
            self.final_response_received: bool = False
            self.response_received = threading.Event()
            self.server_kerberos_token: Optional[bytes] = None
            self.service_principal: str = service_principal
            self.user_principal: str = user_principal
            self.exception: Optional[Exception] = None

            # there is no need to check status for failures as
            # kerberos module converts failures to exceptions
            _, self.krb_context = kerberos.authGSSClientInit(
                self.service_principal, self.user_principal, gssflags=0
            )

        def __iter__(self):
            return self

        def __next__(self) -> protobuf.wrappers_pb2.BytesValue:
            """
            Returns:
                The kerberos token.
            """
            try:
                if self.first_iteration:
                    _ = kerberos.authGSSClientStep(self.krb_context, "")
                else:
                    self.response_received.wait()
                    self.response_received.clear()
                    # no need to guard server's kerberos token as it is accessed sequentially

                    if self.final_response_received:
                        raise StopIteration()

                    # server kerberos token is in binary form, convert it to base64 string
                    # Note: all base64 characters are ASCII characters,
                    # so it is safe to decode using ASCII
                    base64_server_kerberos_token = base64.b64encode(
                        self.server_kerberos_token
                    ).decode("ascii")
                    _ = kerberos.authGSSClientStep(
                        self.krb_context, base64_server_kerberos_token
                    )

                # response is base64 encoded
                base64_client_kerberos_token = kerberos.authGSSClientResponse(
                    self.krb_context
                )

                # Mesh expects it in binary form, so decode it
                client_token = protobuf.wrappers_pb2.BytesValue(
                    value=base64.b64decode(base64_client_kerberos_token)
                )
            except Exception as ex:
                # store exception and re-throw
                # gRPC will raise its own RpcError with vague "Exception iterating requests"
                # message, but we will replace it with this detailed exception in 'get_token'
                self.exception = ex
                raise ex

            self.first_iteration = False
            return client_token

        def process_response(self, server_kerberos_token: bytes) -> None:
            """
            Sets new response from Mesh with kerberos token to be processed by client.

            Args:
                server_kerberos_token: The kerberos token.
            """
            self.server_kerberos_token = server_kerberos_token
            self.response_received.set()

        def signal_final_response_received(self) -> None:
            """
            Signals to the iterator that final response from server was received.
            Cancel any preparation (meaning exit wait) as there is no need to prepare next request.
            """
            self.final_response_received = True
            self.response_received.set()

    def __init__(
        self,
        parameters: Parameters,
        target: str,
        channel_credentials: grpc.ChannelCredentials,
    ):
        r"""
        If Mesh gRPC server is running as a service user, for example LocalSystem, NetworkService or a user account with a registered service principal name then it is enough to provide hostname as service principal, e.g.: 'HOST/hostname.ad.examplecompany.com'

        If Mesh gRPC server is running as a user account without registered service principal name then it is enough to provide user account name running Mesh server as service principal, e.g.: ad\\user.name' or r'ad\user.name'.

        Note:
            winkerberos converts service principal name if provided in RFC-2078 format. '@' is converted to '/' if there is no '/' character in the service principal name.

            E.g.: service@hostname
            Would be converted to: service/hostname

        Args:
            parameters: Authentication parameters.
            target: Mesh server host name in the form an IP or domain name.
            channel_credentials: An encapsulation of the data required to create a secure Channel.
        """

        self.service_principal: str = parameters.service_principal
        self.user_principal: Optional[str] = parameters.user_principal
        self.token: Optional[str] = None
        self.token_expiration_date: Optional[datetime] = None

        # create separate channel for getting and refreshing Mesh token
        channel = grpc.secure_channel(target=target, credentials=channel_credentials)
        self.mesh_service = core_pb2_grpc.MeshServiceStub(channel)

        # get token in initialization to avoid spending
        # extra time while executing first call to Mesh
        self.get_token()

    def __call__(self, context, callback):
        if not self.is_token_valid():
            self.get_token()
        callback((("authorization", "Bearer " + self.token),), None)

    def is_token_valid(self) -> bool:
        """
        Checks if current token is still valid.

        Returns:
            Flag if token is valid.
        """
        if self.token_expiration_date is None:
            return False

        # use UTC to avoid corner cases with Daylight Saving Time
        return self.token_expiration_date > datetime.now(timezone.utc)

    def get_token(self) -> None:
        """
        Gets Mesh token used for authorization in other calls to Mesh server.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
            (win)kerberos.GSSError: Errors from kerberos.
            RuntimeError: Invalid token duration.
        """

        # save current time - will be used to compute token expiration date
        auth_request_call_timestamp = datetime.now(timezone.utc)

        try:
            kerberos_token_iterator = self.KerberosTokenIterator(
                self.service_principal, self.user_principal
            )
            mesh_responses = self.mesh_service.AuthenticateKerberos(
                kerberos_token_iterator
            )
            for mesh_response in mesh_responses:
                if not mesh_response.bearer_token:
                    kerberos_token_iterator.process_response(
                        mesh_response.kerberos_token
                    )
                else:
                    kerberos_token_iterator.signal_final_response_received()

                    # shorten the token duration time by 1 minute to
                    # have some margin for transport duration, etc.
                    duration_margin = timedelta(seconds=60)
                    token_duration = mesh_response.token_duration.ToTimedelta()

                    if token_duration <= duration_margin:
                        raise RuntimeError("Invalid Mesh token duration")

                    adjusted_token_duration = token_duration - duration_margin
                    self.token_expiration_date = (
                        auth_request_call_timestamp + adjusted_token_duration
                    )
                    self.token = mesh_response.bearer_token
        except grpc.RpcError as ex:
            if kerberos_token_iterator.exception is not None:
                # replace vague RpcError with more detailed exception
                # that happened in request iterator
                raise kerberos_token_iterator.exception
            # otherwise the exception happened elsewhere, re-throw it
            raise ex

    def delete_access_token(self):
        """
        Deletes (resets) current Mesh token if no longer needed.
        mesh_service.RevokeAccessToken call is made in Connection classes.
        """
        self.token = None
        self.token_expiration_date = None


def authenticate_fake(
    service: core_pb2_grpc.MeshServiceStub, name: str
) -> typing.Tuple[str, datetime]:
    """Authenticate to Mesh with a fake identity.

    Requires Mesh configuration. Internal use only.

    Args:
        service: A mesh service stub.
        name: The display name of the fake user.

    Returns:
        A pair (token, expiration) where token is a valid Mesh authorization
        token, and expiration is the datetime for the expiration of that token.

    Raises:
        grpc.RpcError: If the remote procedure call fails.
    """
    request = core_pb2.AuthenticateFakeRequest(
        display_name=name, token_duration=protobuf.duration_pb2.Duration(seconds=3600)
    )
    now = datetime.now(timezone.utc)
    response = service.AuthenticateFake(request)
    return response.bearer_token, now + response.token_duration.ToTimedelta()


class FakeIdentityPlugin(grpc.AuthMetadataPlugin):
    """A grpc.AuthMetadataPlugin for fake Mesh authentication.

    Requires Mesh configuration. Internal use only.
    """

    def __init__(
        self, grpc_target: str, grpc_credentials: grpc.ChannelCredentials, name: str
    ):
        self.name = name
        self.token: str = ""
        self.token_expiration: datetime = datetime.now(timezone.utc)

        channel = grpc.secure_channel(target=grpc_target, credentials=grpc_credentials)
        self.mesh_service = core_pb2_grpc.MeshServiceStub(channel)

    def __call__(self, context, callback):
        if self.token_expiration < datetime.now(timezone.utc) + timedelta(minutes=1):
            self.token, self.token_expiration = authenticate_fake(
                self.mesh_service, self.name
            )
        callback((("authorization", "Bearer " + self.token),), None)
