from typing import Optional
import uuid

from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc


class _Availability:
    def __init__(
        self,
        availability_service: availability_pb2_grpc.AvailabilityServiceStub,
        session_id: Optional[uuid.UUID],
    ):
        self.session_id: Optional[uuid.UUID] = session_id
        self.availability_service: availability_pb2_grpc.AvailabilityServiceStub = (
            availability_service
        )

    def PrepareRevisionRequest():
        print("PrepareRevisionRequest")
