import base64
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from sys import platform

import grpc
from google import protobuf

from volue.mesh.proto import mesh_pb2_grpc

if platform.startswith('win32'):
    import winkerberos as kerberos
elif platform.startswith('linux'):
    import kerberos


class Authentication(grpc.AuthMetadataPlugin):
    """ Authentication services for authentication and authorization to Mesh server.
        The flow is as follows:

        1. Obtain token from Kerberos to access specified service (SPN)
           with Mesh server running on it.
        2. Send this token to Mesh gRPC server (using AuthenticateKerberos).
        3. In return Mesh may respond with:

            a. Server challenge to be verified and processed by client (using Kerberos).
               In this case the authentication is not yet completed and client should respond
               to the server with next Kerberos generated token.
            b. Mesh token - to be used in subsequent calls to Mesh that require authentication.
               Token duration - tokens are valid for 1 hour. After this time a new token
               needs to be acquired.

               This step is the final step of authentication from server side.
    """

    @dataclass
    class Parameters:
        """
        Authentication parameters.
        """
        service_principal: str
        user_principal: str = None


    class KerberosTokenIterator():
        """
        Kerberos token iterator to be used with AuthenticateKerberos streaming gRPC.
        Sends tokens to be processed by the Mesh server and processes tokens
        received from the server.
        """
        def __init__(self, service_principal: str, user_principal: str):
            self.krb_context = None
            self.first_iteration: bool = True
            self.final_response_received: bool = False
            self.response_received = threading.Event()
            self.server_kerberos_token: bytes = None
            self.service_principal: str = service_principal
            self.user_principal: str = user_principal
            self.exception: Exception = None

            # there is no need to check status for failures as
            # kerberos module converts failures to exceptions
            _, self.krb_context = kerberos.authGSSClientInit(
                self.service_principal, self.user_principal, gssflags = 0)

        def __iter__(self):
            return self

        def __next__(self) -> protobuf.wrappers_pb2.BytesValue:
            try:
                if self.first_iteration:
                    _ = kerberos.authGSSClientStep(self.krb_context, '')
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
                        self.server_kerberos_token).decode('ascii')
                    _ = kerberos.authGSSClientStep(
                        self.krb_context, base64_server_kerberos_token)

                # response is base64 encoded
                base64_client_kerberos_token = kerberos.authGSSClientResponse(self.krb_context)

                # Mesh expects it in binary form, so decode it
                client_token = protobuf.wrappers_pb2.BytesValue(
                    value = base64.b64decode(base64_client_kerberos_token))
            except Exception as ex:
                # store exception and re-throw
                # gRPC will raise its own RpcError with vague "Exception iterating requests"
                # message, but we will replace it with this detailed exception in 'get_token'
                self.exception = ex
                raise ex

            self.first_iteration = False
            return client_token

        def process_response(self, server_kerberos_token: bytes):
            """
            Sets new response from Mesh with kerberos token to be processed by client.
            """
            self.server_kerberos_token = server_kerberos_token
            self.response_received.set()

        def signal_final_response_received(self):
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
        channel_credentials: grpc.ChannelCredentials):

        self.service_principal: str = parameters.service_principal
        self.user_principal: str = parameters.user_principal
        self.token: str = None
        self.token_expiration_date: datetime = None

        # create separate channel for getting and refreshing Mesh token
        channel = grpc.secure_channel(
            target=target,
            credentials=channel_credentials
        )
        self.mesh_service = mesh_pb2_grpc.MeshServiceStub(channel)

        # get token in initialization to avoid spending
        # extra time while executing first call to Mesh
        self.get_token()


    def __call__(self, context, callback):
        if not self.is_token_valid():
            self.get_token()
        callback((('authorization', 'Bearer ' + self.token),), None)


    def is_token_valid(self) -> bool:
        """
        Checks if current token is still valid.
        """
        if self.token_expiration_date is None:
            return False

        # use UTC to avoid corner cases with Daylight Saving Time
        return self.token_expiration_date > datetime.now(timezone.utc)


    def get_token(self) -> None:
        """
        Gets Mesh token used for authorization in other calls to Mesh server.

        Raises:
            grpc.RpcError:
            (win)kerberos.GSSError:
            RuntimeError: invalid token duration
        """

        # save current time - will be used to compute token expiration date
        auth_request_call_timestamp = datetime.now(timezone.utc)

        try:
            kerberos_token_iterator = self.KerberosTokenIterator(
                self.service_principal, self.user_principal)
            mesh_responses = self.mesh_service.AuthenticateKerberos(kerberos_token_iterator)
            for mesh_response in mesh_responses:
                if not mesh_response.bearer_token:
                    kerberos_token_iterator.process_response(mesh_response.kerberos_token)
                else:
                    kerberos_token_iterator.signal_final_response_received()

                    # shorten the token duration time by 1 minute to
                    # have some margin for transport duration, etc.
                    duration_margin = timedelta(seconds = 60)
                    token_duration = mesh_response.token_duration.ToTimedelta()

                    if token_duration <= duration_margin:
                        raise RuntimeError('Invalid Mesh token duration')

                    adjusted_token_duration = token_duration - duration_margin
                    self.token_expiration_date: datetime = auth_request_call_timestamp + adjusted_token_duration
                    self.token: str = mesh_response.bearer_token
        except grpc.RpcError as ex:
            if kerberos_token_iterator.exception is not None:
                # replace vague RpcError with more detailed exception
                # that happened in request iterator
                raise kerberos_token_iterator.exception
            # otherwise the exception happened elsewhere, re-throw it
            raise ex


    def delete_access_token(self) -> str:
        """
        Deletes (resets) current Mesh token if no longer needed.
        mesh_service.RevokeAccessToken call is made in Connection classes.
        """
        self.token = None
        self.token_expiration_date = None