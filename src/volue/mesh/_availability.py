from typing import Optional
import uuid
from volue.mesh import _base_availability
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc


class _Availability(_base_availability._Availability):
    def __init__(
        self,
        availability_service: availability_pb2_grpc.AvailabilityServiceStub,
        session_id: Optional[uuid.UUID],
    ):
        super().__init__(availability_service, session_id)

    def CreateRevision():
        print("CreateRevision")
