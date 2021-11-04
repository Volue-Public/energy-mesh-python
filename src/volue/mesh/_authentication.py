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


class Authentication:
    """ Authentication services for authentication and authorization to Mesh server.
        The flow is as follows:
        1. Obtain ticket from Kerberos to access specified service (SPN) with Mesh server
           running on it.
        2. Send this ticket to Mesh (using AuthenticateKerberos).
        3. In return Mesh may respond with:
            a. Server challenge to be verified and processed by client (using Kerberos)
               In this case the authentication is not yet completed and client should respond with
               next ticket (Kerberos generated) and send it to Mesh (using AuthenticateKerberos).
            b. Token to be used in subsequent calls to Mesh that required authentication.
               Token duration - tokens are valid for 1 hour.
                                After this time a new token needs to be acquired.
               Kerberos ticket - optionally can be checked by client for mutual authentication.
                                 In this case it is skipped as server authentication is
                                 ensured by gRPC TLS connection.
               This step is the final step of authentication from server side.
    """

    @dataclass
    class Parameters:
        """
        Authentication parameters.
        """
        service_principal: str
        user_principal: str = None


    class KerberosTicketIterator():
        """
        Kerberos ticket/challenge iterator to be used with AuthenticateKerberos streaming gRPC.
        Sends tickets to be processed by the Mesh server and processes tickets
        received from the server.
        """
        def __init__(self, service_principal: str, user_principal: str):
            self.krb_context = None
            self.first_iteration: bool = True
            self.response_received = threading.Condition()
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
                    with self.response_received:
                        self.response_received.wait()
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
            with self.response_received:
                self.server_kerberos_token = server_kerberos_token
                self.response_received.notify()


    # Decorator
    @staticmethod
    def check_token_for_renewal(grpc_call):
        """
        Decorator to be used in functions calling gRPCs requiring authorization.
        If authorization is enabled it checks if the current token has expired and
        generates a new one if it has.
        """
        def wrapper(*args, **kwargs):
            self = args[0]  # Connection (regular or aio) and Session

            if self.auth is not None:
                if not self.auth.is_token_valid():
                    self.grpc_metadata = (
                        ('authorization', self.auth.get_token()),
                    )

            return grpc_call(*args, **kwargs)
        return wrapper


    def __init__(
        self,
        mesh_service: mesh_pb2_grpc.MeshServiceStub,
        parameters: Parameters):

        self.mesh_service: mesh_pb2_grpc.MeshServiceStub = mesh_service
        self.service_principal: str = parameters.service_principal
        self.user_principal: str = parameters.user_principal
        self.token_expiration_date: datetime = None


    def is_token_valid(self) -> bool:
        """
        Checks if current token is still valid.

        Raises:
            RuntimeError: No token was generated
        """
        if self.token_expiration_date is None:
            raise RuntimeError("Failed to check if token is valid: no token was generated.")

        # use UTC to avoid corner cases with Daylight Saving Time
        return self.token_expiration_date > datetime.now(timezone.utc)


    def get_token(self) -> str:
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
            kerberos_ticket_iterator = self.KerberosTicketIterator(
                self.service_principal, self.user_principal)
            mesh_responses = self.mesh_service.AuthenticateKerberos(kerberos_ticket_iterator)
            for mesh_response in mesh_responses:
                if not mesh_response.bearer_token:
                    kerberos_ticket_iterator.process_response(mesh_response.kerberos_token)
                else:
                    # shorten the token duration time by 1 minute to
                    # have some margin for transport duration, etc.
                    duration_margin = timedelta(seconds = 60)
                    token_duration = mesh_response.token_duration.ToTimedelta()

                    if token_duration <= duration_margin:
                        raise RuntimeError('Invalid Mesh token duration')

                    adjusted_token_duration = token_duration - duration_margin
                    self.token_expiration_date = auth_request_call_timestamp + adjusted_token_duration
                    mesh_token = 'Bearer ' + mesh_response.bearer_token
        except grpc.RpcError as ex:
            if kerberos_ticket_iterator.exception is not None:
                # replace vague RpcError with more detailed exception
                # that happened in request iterator
                raise kerberos_ticket_iterator.exception
            # otherwise the exception happend elsewhere re-throw it
            raise ex

        return mesh_token

    def revoke_access_token(self):
        """
        Revokes Mesh token if no longer needed.
        """
        # To-do: TBD
        pass
