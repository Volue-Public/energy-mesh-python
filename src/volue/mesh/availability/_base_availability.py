from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union

import dateutil
from bidict import bidict

from volue.mesh._common import (
    _datetime_to_timestamp_pb2,
    _from_proto_guid,
    _to_proto_guid,
    _to_proto_utcinterval,
)
from volue.mesh._mesh_id import _to_proto_object_mesh_id
from volue.mesh._object import Object
from volue.mesh.proto.availability.v1alpha import (
    availability_pb2,
    availability_pb2_grpc,
)


class RecurrenceType(Enum):
    NONE = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4


class EventType(Enum):
    ALL = 0
    RESTRICTION = 1
    REVISION = 2


RECURRENCE_TYPE = bidict(
    {
        RecurrenceType.NONE: availability_pb2.RecurrenceType.NONE,
        RecurrenceType.DAILY: availability_pb2.RecurrenceType.DAILY,
        RecurrenceType.WEEKLY: availability_pb2.RecurrenceType.WEEKLY,
        RecurrenceType.MONTHLY: availability_pb2.RecurrenceType.MONTHLY,
        RecurrenceType.YEARLY: availability_pb2.RecurrenceType.YEARLY,
    }
)

EVENT_TYPE = bidict(
    {
        EventType.ALL: availability_pb2.EventType.ALL,
        EventType.RESTRICTION: availability_pb2.EventType.RESTRICTION,
        EventType.REVISION: availability_pb2.EventType.REVISION,
    }
)


@dataclass
class Recurrence:
    """
    Represents a recurrence pattern for a revision in the availability system.

    Attributes:
        status: The status of the recurrence.
        description: A description of the recurrence.
        recurrence_type: The type of recurrence (e.g., DAILY, WEEKLY, etc.).
        recur_every: The multiplier of the recurrence type (e.g., every 2 weeks).
        recur_until: The time until which the recurrence is active.
    """

    status: str
    description: str
    recurrence_type: RecurrenceType
    recur_every: Optional[int] = None
    recur_until: Optional[datetime] = None

    @classmethod
    def _from_proto(cls, proto_recurrence: availability_pb2.Recurrence) -> Recurrence:
        """
        Converts a protobuf Recurrence object into a Recurrence instance.

        Args:
            proto_recurrence: The protobuf Recurrence object.

        Returns:
            The corresponding Recurrence instance.
        """
        return cls(
            status=proto_recurrence.status,
            description=proto_recurrence.description,
            recurrence_type=RECURRENCE_TYPE.inverse[proto_recurrence.recurrence_type],
            recur_every=(
                proto_recurrence.recur_every
                if proto_recurrence.HasField("recur_every")
                else None
            ),
            recur_until=(
                proto_recurrence.recur_until.ToDatetime(dateutil.tz.UTC)
                if proto_recurrence.HasField("recur_until")
                else None
            ),
        )

    @classmethod
    def _to_proto(cls, recurrence: Recurrence) -> availability_pb2.Recurrence:
        """
        Converts a Recurrence instance into a protobuf Recurrence object.

        Args:
            recurrence: The Recurrence instance.

        Returns:
            The corresponding protobuf Recurrence object.
        """
        if recurrence.recur_until is None:
            recur_until = None
        else:
            recur_until = _datetime_to_timestamp_pb2(recurrence.recur_until)

        return availability_pb2.Recurrence(
            status=recurrence.status,
            description=recurrence.description,
            recurrence_type=RECURRENCE_TYPE[recurrence.recurrence_type],
            recur_every=recurrence.recur_every,
            recur_until=recur_until,
        )


@dataclass
class RevisionRecurrence:
    """
    Represents a recurrence associated with a revision.

    Attributes:
        id: The unique identifier of the recurrence (optional).
        recurrence: The recurrence details, including type, frequency, and description.
        period_start: The start time of the interval for which the recurrence is active.
        period_end: The end time of the interval for which the recurrence is active.
    """

    recurrence: Recurrence
    period_start: datetime
    period_end: datetime
    id: Optional[int] = None

    @classmethod
    def _from_proto(
        cls, proto_recurrence: availability_pb2.RevisionRecurrence
    ) -> RevisionRecurrence:
        """
        Converts a protobuf RevisionRecurrence object into a RevisionRecurrence instance.

        Args:
            proto_recurrence: The protobuf RevisionRecurrence object.

        Returns:
            RevisionRecurrence: The corresponding RevisionRecurrence instance.
        """
        return cls(
            id=proto_recurrence.recurrence_id,
            recurrence=Recurrence._from_proto(proto_recurrence.recurrence),
            period_start=proto_recurrence.period.start_time.ToDatetime(dateutil.tz.UTC),
            period_end=proto_recurrence.period.end_time.ToDatetime(dateutil.tz.UTC),
        )

    @classmethod
    def _to_proto(
        cls, recurrence: RevisionRecurrence
    ) -> availability_pb2.RevisionRecurrence:
        """
        Converts a RevisionRecurrence instance into a protobuf RevisionRecurrence object.

        Args:
            recurrence: The RevisionRecurrence instance.

        Returns:
            The corresponding protobuf RevisionRecurrence object.
        """

        return availability_pb2.RevisionRecurrence(
            recurrence=Recurrence._to_proto(recurrence.recurrence),
            period=_to_proto_utcinterval(
                recurrence.period_start, recurrence.period_end
            ),
        )


@dataclass
class AvailabilityRecordInfo:
    """
    Represents metadata about a record in the availability system.

    This class contains information about who created or last modified
    a record and when the action occurred.

    Attributes:
        author: The name or identifier of the user who created or last modified the record.
        timestamp: The date and time when the record was created or last modified.
    """

    author: str
    timestamp: datetime

    @classmethod
    def _from_proto(
        cls, proto_record_info: availability_pb2.RecordInfo
    ) -> AvailabilityRecordInfo:
        """
        Converts a protobuf RecordInfo object into an AvailabilityRecordInfo instance.

        Args:
            proto_record_info: The protobuf RecordInfo object.

        Returns:
            AvailabilityRecordInfo: The corresponding AvailabilityRecordInfo instance.
        """
        return cls(
            author=proto_record_info.author,
            timestamp=proto_record_info.timestamp.ToDatetime(dateutil.tz.UTC),
        )


@dataclass
class Revision:
    """
    Represents a revision in the availability system.

    A revision defines a period during which a Mesh object is unavailable.
    It includes metadata about the revision, such as its identifiers, reason,
    creation time, last modification time, and recurrence details.

    Attributes:
        owner_id: The unique identifier of the Mesh object to which the revision belongs.
        owner_path: The path of the Mesh object to which the revision belongs.
        event_id: A unique identifier for the revision.
        local_id: An additional identifier for the revision, which may not be unique.
        reason: A description or explanation for the revision.
        created: Metadata about when and by whom the revision was created.
        last_changed: Metadata about when and by whom the revision was last modified.
        recurrences: A list of recurrence patterns associated with the revision.
    """

    owner_id: uuid.UUID
    owner_path: str
    event_id: str
    local_id: str
    reason: str
    created: AvailabilityRecordInfo
    last_changed: AvailabilityRecordInfo
    recurrences: list[RevisionRecurrence]

    @classmethod
    def _from_proto(
        cls,
        proto_availability: availability_pb2.Revision,
    ) -> Revision:
        return cls(
            owner_id=_from_proto_guid(proto_availability.owner_id.id),
            owner_path=proto_availability.owner_id.path,
            event_id=proto_availability.event_id,
            local_id=proto_availability.local_id,
            reason=proto_availability.reason,
            created=AvailabilityRecordInfo._from_proto(proto_availability.created),
            last_changed=AvailabilityRecordInfo._from_proto(
                proto_availability.last_changed
            ),
            recurrences=[
                RevisionRecurrence._from_proto(recurrence)
                for recurrence in proto_availability.recurrences
            ],
        )


@dataclass
class RestrictionRecurrence:
    """
    Represents a recurrence pattern for a restriction in the availability system.

    Attributes:
        status: The status of the recurrence.
        description: A description of the recurrence.
        recurrence_type: The type of recurrence (e.g., DAILY, WEEKLY, etc.).
        recur_every: The multiplier of the recurrence type (e.g., every 2 weeks).
        recur_until: The time until which the recurrence is active.
    """

    status: str
    description: str
    recurrence_type: RecurrenceType
    recur_every: Optional[int] = None
    recur_until: Optional[datetime] = None


@dataclass
class RestrictionBasicRecurrence:
    """
    Represents a basic recurrence pattern for a restriction in the availability system.

    A basic recurrence defines a fixed value applied to a restricted object category
    over a specific time interval.

    Attributes:
        recurrence: The recurrence details, including type, frequency, and description.
        period_start: The start time of the interval for which the recurrence is active.
        period_end: The end time of the interval for which the recurrence is active.
        value: The fixed value applied to the restricted object category during the recurrence.
    """

    recurrence: Recurrence
    period_start: datetime
    period_end: datetime
    value: float


@dataclass
class TimePoint:
    """
    Represents a single time point with a corresponding value in the availability system.

    A time point is used in complex recurrences to define specific timestamps
    and their associated values.

    Attributes:
        value: The value applied at the specified timestamp.
        timestamp: The specific point in time for which the value is defined.
    """

    value: float
    timestamp: datetime


@dataclass
class RestrictionComplexRecurrence:
    """
    Represents a complex recurrence pattern for a restriction in the availability system.

    A complex recurrence defines multiple time points with corresponding values
    that are applied to a restricted object category. These time points can be
    repeated using recurrence patterns.

    Attributes:
        recurrence: The recurrence details, including type, frequency, and description.
        time_points: A list of time points, each with a specific timestamp and value.
    """

    recurrence: Recurrence
    time_points: list[TimePoint]


@dataclass
class Restriction:
    """
    Represents a restriction in the availability system.

    A restriction defines a period during which a Mesh object is unavailable
    due to external factors. It includes metadata about the restriction,
    such as its identifiers, reason, creation time, last modification time,
    and recurrence details.

    Attributes:
        owner_id: The unique identifier of the Mesh object to which the restriction belongs.
        owner_path: The path of the Mesh object to which the restriction belongs.
        event_id: A unique identifier for the restriction.
        local_id: An additional identifier for the restriction, which may not be unique.
        reason: A description or explanation for the restriction.
        category: The category of the restriction.
        recurrence: The recurrence details, which can be either basic or complex.
    """

    owner_id: uuid.UUID
    owner_path: str
    event_id: str
    local_id: str
    reason: str
    category: str
    recurrence: Union[RestrictionBasicRecurrence, RestrictionComplexRecurrence]


class _Availability(abc.ABC):
    def __init__(
        self,
        availability_service: availability_pb2_grpc.AvailabilityServiceStub,
        session_id: Optional[uuid.UUID],
    ):
        self.session_id: Optional[uuid.UUID] = session_id
        self.availability_service: availability_pb2_grpc.AvailabilityServiceStub = (
            availability_service
        )

    @abc.abstractmethod
    def create_revision(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        local_id: str,
        reason: str,
    ) -> Revision:
        """
        Creates a new revision for a specified Mesh object.

        A revision represents a period during which a Mesh object is unavailable.
        This method allows you to define the revision by specifying its target,
        unique identifier, local identifier, and the reason for its creation.

        Args:
            target: The Mesh object to which the new revision belongs.
                This can be specified as a UUID or a string path.
            event_id: A unique identifier for the revision. This must be unique
                among all revisions belonging to the same target object.
            local_id: An additional identifier for the revision. This does not
                need to be unique and can be used for external system references.
            reason: A description or explanation for creating the revision.

        Returns:
            Revision: An object representing the newly created revision, including
            details such as event ID, local ID, reason, owner ID, creation time,
            last modification time, and recurrence information.

        Raises:
            Exception: If the target is invalid or the revision cannot be created.
            TypeError: If required fields are missing or invalid types are provided.
        """

    def _prepare_create_revision_request(
        self, target: Union[uuid.UUID, str, Object], id: str, local_id: str, reason: str
    ) -> availability_pb2.CreateRevisionRequest:
        request = availability_pb2.CreateRevisionRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=id,
            local_id=local_id,
            reason=reason,
        )
        return request

    @abc.abstractmethod
    def add_revision_recurrence(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence: Recurrence,
        period_start: datetime,
        period_end: datetime,
    ) -> int:
        """
        Adds a recurrence pattern to an existing revision.

        This method allows you to associate a recurrence pattern with a specific
        revision of a Mesh object, defining the period during which the recurrence
        is active.

        Args:
            target: The Mesh object to which the revision belongs.
                This can be specified as a UUID, a string path, or an Object instance.
            event_id: The unique identifier of the revision to which the recurrence
                will be added.
            recurrence: The recurrence pattern to be added, including details such as
                type, frequency, and description.
            period_start: The start time of the period during which the recurrence is active.
            period_end: The end time of the period during which the recurrence is active.

        Returns:
            int: The unique identifier of the newly created recurrence.

        Raises:
            Exception: If the target is invalid or the recurrence cannot be added.
            TypeError: If required fields are missing or invalid types are provided.
        """

    def _prepare_add_recurrence_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence: Recurrence,
        period_start: datetime,
        period_end: datetime,
    ) -> availability_pb2.AddRevisionRecurrenceRequest:

        revision_recurrence = RevisionRecurrence(
            recurrence=recurrence, period_start=period_start, period_end=period_end
        )

        request = availability_pb2.AddRevisionRecurrenceRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
            revision_recurrence=RevisionRecurrence._to_proto(revision_recurrence),
        )
        return request

    @abc.abstractmethod
    def get_availability_event(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
    ) -> Union[Revision]:
        """
        Retrieves a specific availability event (Revision or Restriction) for a given Mesh object.

        This method fetches the details of an availability event, such as a Revision or Restriction,
        based on the provided Mesh object and event identifier.

        Args:
            target: The Mesh object to which the availability event belongs.
                This can be specified as a UUID, a string path, or an Object instance.
            event_id: The unique identifier of the availability event to retrieve.

        Returns:
            Union[Revision]: The availability event as a `Revision` object if found.

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            Exception: If the target or event_id is invalid.
        """

    def _prepare_get_availability_event_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
    ) -> availability_pb2.GetAvailabilityEventRequest:
        request = availability_pb2.GetAvailabilityEventRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
        )
        return request

    @abc.abstractmethod
    def search_availability_events(
        self,
        event_type: EventType,
        targets: list[Union[uuid.UUID, str, Object]],
    ) -> Union[list[Revision]]:
        """
        Searches for availability events (Revisions or Restrictions) in specified Mesh objects.

        This method allows you to search for specific types of availability events (e.g., Revisions or Restrictions)
        across multiple Mesh objects.

        Args:
            event_type: The type of availability event to search for. Can be one of the following:
                - EventType.ALL: Search for all types of events.
                - EventType.RESTRICTION: Search for restrictions only.
                - EventType.REVISION: Search for revisions only.
            targets: A list of Mesh objects to search for events. Each target can be specified as a UUID, a string path,
                or an Object instance.

        Returns:
            A list of `Revision` or `Restriction` objects representing the availability events found.

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            ValueError: If the `targets` list is empty or invalid.
        """

    def _prepare_search_availability_events_request(
        self,
        event_type: EventType,
        targets: list[Union[uuid.UUID, str, Object]],
    ) -> availability_pb2.SearchAvailabilityEventsRequest:
        request = availability_pb2.SearchAvailabilityEventsRequest(
            session_id=_to_proto_guid(self.session_id),
            event_type=EVENT_TYPE[event_type],
            owner_ids=[_to_proto_object_mesh_id(target) for target in targets],
        )
        return request

    @abc.abstractmethod
    def delete_revision_recurrence(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence_id: int,
    ) -> None:
        """
        Deletes a specific recurrence associated with a revision.

        This method allows you to remove a recurrence pattern from an existing revision.

        Args:
            target: The Mesh object to which the revision belongs.
                This can be specified as a UUID, a string path, or an Object instance.
            event_id: The unique identifier of the revision from which the recurrence will be deleted.
            recurrence_id: The unique identifier of the recurrence to be deleted.

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            Exception: If the target, event_id, or recurrence_id is invalid.
        """

    def _prepare_delete_revision_recurrence_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence_id: int,
    ) -> availability_pb2.DeleteRevisionRecurrenceRequest:
        request = availability_pb2.DeleteRevisionRecurrenceRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
            recurrence_id=recurrence_id,
        )
        return request

    @abc.abstractmethod
    def delete_availability_events_by_id(
        self,
        target: Union[uuid.UUID, str, Object],
        event_ids: list[str],
    ) -> None:
        """
        Deletes availability events (Revisions or Restrictions) for a given Mesh object.

        This method allows you to delete one or more availability events (e.g., Revisions or Restrictions)
        associated with a specific Mesh object.

        Args:
            target: The Mesh object to which the availability events belong.
                This can be specified as a UUID, a string path, or an Object instance.
            event_ids: A list of unique identifiers for the availability events to be deleted.

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            ValueError: If the `event_ids` list is empty or invalid.
            Exception: If the target or event_ids are invalid.
        """

    def _prepare_delete_availability_events_by_id_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_ids: list[str],
    ) -> availability_pb2.DeleteAvailabilityEventsByIdRequest:
        request = availability_pb2.DeleteAvailabilityEventsByIdRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_ids=event_ids,
        )
        return request

    @abc.abstractmethod
    def delete_availability_events(
        self, target: Union[uuid.UUID, str, Object], event_type: EventType
    ) -> None:
        """
        Deletes all availability events (Revisions or Restrictions) of a specific type for a given Mesh object.

        This method removes all availability events of the specified type (e.g., Revisions or Restrictions)
        associated with the given Mesh object.

        Args:
            target: The Mesh object to which the availability events belong.
                This can be specified as a UUID, a string path, or an Object instance.
            event_type: The type of availability events to delete. Can be one of the following:
                - EventType.ALL: Deletes all types of availability events.
                - EventType.RESTRICTION: Deletes only restriction events.
                - EventType.REVISION: Deletes only revision events.

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            ValueError: If the `event_type` is invalid.
            Exception: If the target is invalid or the deletion cannot be performed.
        """

    def _prepare_delete_availability_events_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_type: EventType,
    ) -> availability_pb2.DeleteAvailabilityEventsRequest:
        request = availability_pb2.DeleteAvailabilityEventsRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_type=EVENT_TYPE[event_type],
        )
        return request
