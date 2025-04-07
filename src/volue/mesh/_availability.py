import datetime
import uuid
from typing import Optional, Union

from volue.mesh import _base_availability
from volue.mesh._object import Object
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc


class _Availability(_base_availability._Availability):
    def __init__(
        self,
        availability_service: availability_pb2_grpc.AvailabilityServiceStub,
        session_id: Optional[uuid.UUID],
    ):
        super().__init__(availability_service, session_id)

    def create_revision(
        self, target: Union[uuid.UUID, str, Object], id: str, local_id: str, reason: str
    ) -> _base_availability.Revision:
        request = super()._prepare_create_revision_request(target, id, local_id, reason)
        proto_revision = self.availability_service.CreateRevision(request)
        return _base_availability.Revision._from_proto(proto_revision)

    def add_revision_recurrence(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence: _base_availability.RevisionRecurrence,
    ) -> int:
        request = super()._prepare_add_recurrence_request(target, event_id, recurrence)
        add_recurrence_response = self.availability_service.AddRevisionRecurrence(
            request
        )
        return add_recurrence_response.recurrence_id

    def get_availability_event(
        self, target: Union[uuid.UUID, str, Object], event_id: str
    ) -> Union[_base_availability.Revision, None]:

        request = super()._prepare_get_availability_event_request(
            target=target,
            event_id=event_id,
        )

        proto_event = self.availability_service.GetAvailabilityEvent(request)
        if proto_event is None:
            return None

        return _base_availability.Revision._from_proto(proto_event.revision)
