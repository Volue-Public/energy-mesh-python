import uuid
from datetime import datetime
from typing import Optional, Union

from volue.mesh._object import Object
from volue.mesh.availability import (
    EventType,
    Recurrence,
    Restriction,
    RestrictionBasicRecurrence,
    RestrictionComplexRecurrence,
    RestrictionInstance,
    Revision,
    RevisionInstance,
)
from volue.mesh.availability._base_availability import _Availability
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc


class _Availability(_Availability):
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
    ) -> Union[Revision, Restriction]:

        request = super()._prepare_get_availability_event_request(
            target=target,
            event_id=event_id,
        )

        proto_event = await self.availability_service.GetAvailabilityEvent(request)

        if proto_event.HasField("revision"):
            return Revision._from_proto(proto_event.revision)
        else:
            return Restriction._from_proto(proto_event.restriction)

    async def search_availability_events(
        self,
        event_type: EventType,
        targets: list[Union[uuid.UUID, str, Object]],
    ) -> list[Union[Revision, Restriction]]:
        request = super()._prepare_search_availability_events_request(
            event_type=event_type,
            targets=targets,
        )

        # Get the stream call
        proto_events_stream = self.availability_service.SearchAvailabilityEvents(
            request
        )

        # Create the results list
        results = []

        # Use async for to iterate through the stream responses
        async for proto_event in proto_events_stream:
            if proto_event.HasField("revision"):
                results.append(Revision._from_proto(proto_event.revision))
            else:
                results.append(Restriction._from_proto(proto_event.restriction))

        return results

    async def delete_revision_recurrence(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence_id: int,
    ) -> None:
        request = super()._prepare_delete_revision_recurrence_request(
            target, event_id, recurrence_id
        )

        await self.availability_service.DeleteRevisionRecurrence(request)

    async def delete_availability_events_by_id(
        self,
        target: Union[uuid.UUID, str, Object],
        event_ids: list[str],
    ) -> None:
        request = super()._prepare_delete_availability_events_by_id_request(
            target=target, event_ids=event_ids
        )
        await self.availability_service.DeleteAvailabilityEventsById(request)

    async def delete_availability_events(
        self, target: Union[uuid.UUID, str, Object], event_type: EventType
    ) -> None:
        request = super()._prepare_delete_availability_events_request(
            target=target, event_type=event_type
        )
        await self.availability_service.DeleteAvailabilityEvents(request)

    async def create_restriction(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        local_id: str,
        reason: str,
        category: str,
        recurrence: Union[RestrictionBasicRecurrence, RestrictionComplexRecurrence],
    ) -> Restriction:
        request = super()._prepare_create_restriction_request(
            target, event_id, local_id, reason, category, recurrence
        )
        proto_restriction = await self.availability_service.CreateRestriction(request)
        return Restriction._from_proto(proto_restriction)

    async def search_instances(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Union[list[RevisionInstance], list[RestrictionInstance]]:
        request = super()._prepare_search_instances_request(
            target=target,
            event_id=event_id,
            period_start=period_start,
            period_end=period_end,
        )

        proto_instances_stream = self.availability_service.SearchInstances(request)

        results = []

        async for proto_instance in proto_instances_stream:
            if proto_instance.HasField("revision_instance"):
                results.append(
                    RevisionInstance._from_proto(proto_instance.revision_instance)
                )
            else:
                results.append(
                    RestrictionInstance._from_proto(proto_instance.restriction_instance)
                )

        return results

    async def update_revision(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        new_local_id: Optional[str] = None,
        new_reason: Optional[str] = None,
    ) -> None:
        request = super()._prepare_update_revision_request(
            target, event_id, new_local_id, new_reason
        )
        await self.availability_service.UpdateRevision(request)

    async def update_restriction(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        new_local_id: Optional[str] = None,
        new_reason: Optional[str] = None,
        new_category: Optional[str] = None,
        new_restriction_recurrence: Optional[
            Union[RestrictionBasicRecurrence, RestrictionComplexRecurrence]
        ] = None,
    ) -> None:
        request = super()._prepare_update_restriction_request(
            target,
            event_id,
            new_local_id,
            new_reason,
            new_category,
            new_restriction_recurrence,
        )
        await self.availability_service.UpdateRestriction(request)
