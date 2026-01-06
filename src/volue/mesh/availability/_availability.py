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
from volue.mesh.availability._base_availability import Availability
from volue.mesh.proto.availability.v1alpha import availability_pb2_grpc


class Availability(Availability):
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
        created_author: str,
        created_timestamp: Optional[timestamp],
        last_changed_author: str,
    ) -> Revision:
        request = super()._prepare_create_revision_request(
            target, event_id, local_id, reason, created_author, created_timestamp, last_changed_author,
        )
        proto_revision = self.availability_service.CreateRevision(request)
        return Revision._from_proto(proto_revision)

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
    ) -> Union[Revision, Restriction]:

        request = super()._prepare_get_availability_event_request(
            target=target,
            event_id=event_id,
        )

        proto_event = self.availability_service.GetAvailabilityEvent(request)

        if proto_event.HasField("revision"):
            return Revision._from_proto(proto_event.revision)
        else:
            return Restriction._from_proto(proto_event.restriction)

    def search_availability_events(
        self,
        event_type: EventType,
        targets: list[Union[uuid.UUID, str, Object]],
    ) -> list[Union[Revision, Restriction]]:
        request = super()._prepare_search_availability_events_request(
            event_type=event_type, targets=targets
        )

        proto_events = self.availability_service.SearchAvailabilityEvents(request)

        results = []

        for proto_event in proto_events:
            if proto_event.HasField("revision"):
                results.append(Revision._from_proto(proto_event.revision))
            else:
                results.append(Restriction._from_proto(proto_event.restriction))

        return results

    def delete_revision_recurrence(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence_id: int,
    ) -> None:
        request = super()._prepare_delete_revision_recurrence_request(
            target, event_id, recurrence_id
        )
        self.availability_service.DeleteRevisionRecurrence(request)

    def delete_availability_events_by_id(
        self,
        target: Union[uuid.UUID, str, Object],
        event_ids: list[str],
    ) -> None:
        request = super()._prepare_delete_availability_events_by_id_request(
            target=target, event_ids=event_ids
        )
        self.availability_service.DeleteAvailabilityEventsById(request)

    def delete_availability_events(
        self, target: Union[uuid.UUID, str, Object], event_type: EventType
    ) -> None:
        request = super()._prepare_delete_availability_events_request(
            target=target, event_type=event_type
        )
        self.availability_service.DeleteAvailabilityEvents(request)

    def create_restriction(
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
        proto_restriction = self.availability_service.CreateRestriction(request)
        return Restriction._from_proto(proto_restriction)

    def search_instances(
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

        proto_instances = self.availability_service.SearchInstances(request)

        results = []
        for proto_instance in proto_instances:
            if proto_instance.HasField("revision_instance"):
                results.append(
                    RevisionInstance._from_proto(proto_instance.revision_instance)
                )
            else:
                results.append(
                    RestrictionInstance._from_proto(proto_instance.restriction_instance)
                )

        return results

    def update_revision(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        new_local_id: Optional[str] = None,
        new_reason: Optional[str] = None,
    ) -> None:
        request = super()._prepare_update_revision_request(
            target, event_id, new_local_id, new_reason
        )
        self.availability_service.UpdateRevision(request)

    def update_restriction(
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
        self.availability_service.UpdateRestriction(request)
