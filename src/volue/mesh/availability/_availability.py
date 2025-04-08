import datetime
import uuid
from typing import Optional, Union

from volue.mesh._object import Object
from volue.mesh.availability import Recurrence, _base_availability
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc


class _Availability(_base_availability._Availability):
    def __init__(
        self,
        availability_service: availability_pb2_grpc.AvailabilityServiceStub,
        session_id: Optional[uuid.UUID],
    ):
        super().__init__(availability_service, session_id)

    def create_revision(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        local_id: str,
        reason: str,
    ) -> _base_availability.Revision:
        request = super()._prepare_create_revision_request(
            target, event_id, local_id, reason
        )
        proto_revision = self.availability_service.CreateRevision(request)
        return _base_availability.Revision._from_proto(proto_revision)

    def add_revision_recurrence(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence: Recurrence,
        period_start: datetime,
        period_end: datetime,
    ) -> int:
        request = super()._prepare_add_recurrence_request(
            target, event_id, recurrence, period_start, period_end
        )
        add_recurrence_response = self.availability_service.AddRevisionRecurrence(
            request
        )
        return add_recurrence_response.recurrence_id

    def get_availability_event(
        self, target: Union[uuid.UUID, str, Object], event_id: str
    ) -> Union[_base_availability.Revision]:

        request = super()._prepare_get_availability_event_request(
            target=target,
            event_id=event_id,
        )

        proto_event = self.availability_service.GetAvailabilityEvent(request)

        return _base_availability.Revision._from_proto(proto_event.revision)
