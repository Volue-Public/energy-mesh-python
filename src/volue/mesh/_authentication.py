import base64
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from sys import platform
from google import protobuf

from volue.mesh.proto import mesh_pb2_grpc

if platform.startswith('win32'):
    import winkerberos as kerberos
elif platform.startswith('linux'):
    import kerberos


class Authentication:
    """ Authentication services for authentication and authorization to Mesh server.
        The flow is as follows:
        1. Obtain ticket from Kerberos to access specified service (SPN) with Mesh server running on it.
        2. Send this ticket to Mesh (using AuthenticateKerberos).
        3. In return Mesh may respond with:
            a. Server challenge to be verified and processed by client (using Kerberos)
               In this case the authentication is not yet completed and client should respond with
               next ticket (Kerberos generated) and send it to Mesh (using AuthenticateKerberos).
            b. Token to be used in subsequent calls to Mesh that required authentication.
               Token duration - tokens are valid for 1 hour.
                                After this time a new token needs to be aquired.
               Kerberos ticket - optionally can be checked by client for mutual authentication.
                                 In this case it is skipped as server authentication is
                                 ensured by gRPC TLS connection.
               This step is the final step of authentication from server side.
    """

    @dataclass
    class Parameters:  
        service_principal: str
        user_principal: str = None


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
            RuntimeError: invalid token duration
        """
        # there is no need to check status for failures as
        # kerberos module converts failures to exceptions
        _, krb_context = kerberos.authGSSClientInit(self.service_principal, self.user_principal, gssflags = 0)
        # in first step do not provide server challenge
        _ = kerberos.authGSSClientStep(krb_context, '')

        # response is base64 encoded
        base64_response = kerberos.authGSSClientResponse(krb_context)

        # Mesh expects it in binary form, so decode it
        binary_response = base64.b64decode(base64_response)
        ticket = protobuf.wrappers_pb2.BytesValue(value = binary_response)

        # for now support only Mesh server running as a service user,
        # for example LocalSystem, NetworkService or a user account
        # with a registered service principal name.
        # (flow: server -> client -> server)
        mesh_responses = self.mesh_service.AuthenticateKerberos(iter((ticket, )))

        for mesh_response in mesh_responses:
            if not mesh_response.bearer_token:
                raise RuntimeError(
                        'Client side authentication by Mesh server was not completed in one step.')

            # shorten the token duration time by 1 minute to
            # have some margin for transport duration, etc.
            duration_margin = timedelta(seconds = 60)
            token_duration = mesh_response.token_duration.ToTimedelta()

            if token_duration <= duration_margin:
                raise RuntimeError('Invalid Mesh token duration')

            adjusted_token_duration = token_duration - duration_margin
            self.token_expiration_date = datetime.now(timezone.utc) + adjusted_token_duration

            mesh_token = 'Bearer ' + mesh_response.bearer_token

        return mesh_token

    def revoke_access_token(self):
        """
        Revokes Mesh token if no longer needed.
        """
        # To-do: TBD
        pass
