import datetime
import uuid
from typing import Optional, Union

from volue.mesh._object import Object
from volue.mesh.availability import EventType, Recurrence, Revision, _base_availability
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc


class _Availability(_base_availability._Availability):
    def __init__(
        self,
        availability_service: availability_pb2_grpc.AvailabilityServiceStub,
        session_id: Optional[uuid.UUID],
    ):
        super().__init__(availability_service, session_id)

    async def create_revision(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        local_id: str,
        reason: str,
    ) -> Revision:
        request = super()._prepare_create_revision_request(
            target, event_id, local_id, reason
        )
        proto_revision = await self.availability_service.CreateRevision(request)
        return Revision._from_proto(proto_revision)

    async def add_revision_recurrence(
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
        add_recurrence_response = await self.availability_service.AddRevisionRecurrence(
            request
        )
        return add_recurrence_response.recurrence_id

    async def get_availability_event(
        self, target: Union[uuid.UUID, str, Object], event_id: str
    ) -> Union[Revision]:

        request = super()._prepare_get_availability_event_request(
            target=target,
            event_id=event_id,
        )

        proto_event = await self.availability_service.GetAvailabilityEvent(request)

        return Revision._from_proto(proto_event.revision)

    async def search_availability_events(
        self,
        event_type: EventType,
        targets: list[Union[uuid.UUID, str, Object]],
    ) -> Union[list[Revision]]:
        request = super()._prepare_search_availability_events_request(
            event_type=event_type,
            targets=targets,
        )

        proto_events = await self.availability_service.SearchAvailabilityEvents(request)

        return [Revision._from_proto(proto_event) for proto_event in proto_events]

    async def delete_revision_recurrence(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence_id: int,
    ) -> None:
        request = super()._prepare_delete_recurrence_request(
            target, event_id, recurrence_id
        )

        await self.availability_service.DeleteRevisionRecurrence(request)

    async def delete_availability_events_by_id(
        self,
        target: Union[uuid.UUID, str, Object],
        event_ids: list[str],
    ) -> None:
        request = super()._prepare_delete_availability_events_by_id_request(
            target=target,
            event_ids=event_ids,
        )
        await self.availability_service.DeleteAvailabilityEventsById(request)

    async def delete_availability_events(
        self, target: Union[uuid.UUID, str, Object], event_type: EventType
    ) -> None:
        request = super()._prepare_delete_availability_events_request(
            target=target,
            event_type=event_type,
        )
        await self.availability_service.DeleteAvailabilityEvents(request)
