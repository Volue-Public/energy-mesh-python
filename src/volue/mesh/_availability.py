import uuid
from typing import Optional, Union

from volue.mesh import _base_availability
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc


class _Availability(_base_availability._Availability):
    def __init__(
        self,
        availability_service: availability_pb2_grpc.AvailabilityServiceStub,
        session_id: Optional[uuid.UUID],
    ):
        super().__init__(availability_service, session_id)

    def create_revision(
        self, target: Union[uuid.UUID, str], id: str, local_id: str, reason: str
    ) -> _base_availability.Revision:
        request = super()._prepare_create_revision_request(target, id, local_id, reason)
        proto_revision = self.availability_service.CreateRevision(request)
        return _base_availability.Revision._from_proto(proto_revision.revision)
