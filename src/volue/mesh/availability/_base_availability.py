from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union

import dateutil
from bidict import bidict
from google import protobuf

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
class RevisionInstance:
    """
    Represents a specific instance of a revision in the availability system.
    """

    period_start: datetime
    period_end: datetime

    @classmethod
    def _from_proto(
        cls, proto_instance: availability_pb2.RevisionInstance
    ) -> RevisionInstance:
        """
        Converts a protobuf RevisionInstance object into a RevisionInstance instance.

        Args:
            proto_instance: The protobuf RevisionInstance object.

        Returns:
            The corresponding RevisionInstance instance.
        """
        return cls(
            period_start=proto_instance.period.start_time.ToDatetime(dateutil.tz.UTC),
            period_end=proto_instance.period.end_time.ToDatetime(dateutil.tz.UTC),
        )


@dataclass
class RestrictionInstance:
    """
    Represents a specific instance of a restriction in the availability system.
    """

    period_start: datetime
    period_end: datetime
    value: float

    @classmethod
    def _from_proto(
        cls, proto_instance: availability_pb2.RestrictionInstance
    ) -> RestrictionInstance:
        """
        Converts a protobuf RestrictionInstance object into a RestrictionInstance instance.

        Args:
            proto_instance: The protobuf RestrictionInstance object.

        Returns:
            The corresponding RestrictionInstance instance.
        """
        return cls(
            period_start=proto_instance.period.start_time.ToDatetime(dateutil.tz.UTC),
            period_end=proto_instance.period.end_time.ToDatetime(dateutil.tz.UTC),
            value=proto_instance.value,
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

    @classmethod
    def _from_proto(
        cls,
        proto_recurrence: availability_pb2.RestrictionBasicRecurrence,
    ) -> RestrictionBasicRecurrence:
        return cls(
            recurrence=Recurrence._from_proto(proto_recurrence.recurrence),
            period_start=proto_recurrence.period.start_time.ToDatetime(dateutil.tz.UTC),
            period_end=proto_recurrence.period.end_time.ToDatetime(dateutil.tz.UTC),
            value=proto_recurrence.value,
        )

    @classmethod
    def _to_proto(
        cls, recurrence: RestrictionBasicRecurrence
    ) -> availability_pb2.RestrictionBasicRecurrence:
        return availability_pb2.RestrictionBasicRecurrence(
            recurrence=Recurrence._to_proto(recurrence.recurrence),
            period=_to_proto_utcinterval(
                recurrence.period_start, recurrence.period_end
            ),
            value=recurrence.value,
        )


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

    @classmethod
    def _from_proto(
        cls,
        proto_recurrence: availability_pb2.RestrictionComplexRecurrence,
    ) -> RestrictionComplexRecurrence:
        return cls(
            recurrence=Recurrence._from_proto(proto_recurrence.recurrence),
            time_points=[
                TimePoint(
                    value=point.value,
                    timestamp=point.timestamp.ToDatetime(dateutil.tz.UTC),
                )
                for point in proto_recurrence.values
            ],
        )

    @classmethod
    def _to_proto(
        cls, recurrence: RestrictionComplexRecurrence
    ) -> availability_pb2.RestrictionComplexRecurrence:
        return availability_pb2.RestrictionComplexRecurrence(
            recurrence=Recurrence._to_proto(recurrence.recurrence),
            values=[
                availability_pb2.TimePoint(
                    value=point.value,
                    timestamp=_datetime_to_timestamp_pb2(point.timestamp),
                )
                for point in recurrence.time_points
            ],
        )


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
        created: Metadata about when and by whom the restriction was created, containing
                 author name and timestamp information.
        last_changed: Metadata about when and by whom the restriction was last modified,
                      containing author name and timestamp information.
        category: The category of the restriction.
        recurrence: The recurrence details, which can be either basic or complex.
    """

    owner_id: uuid.UUID
    owner_path: str
    event_id: str
    local_id: str
    reason: str
    category: str
    created: AvailabilityRecordInfo
    last_changed: AvailabilityRecordInfo
    recurrence: Union[RestrictionBasicRecurrence, RestrictionComplexRecurrence]

    @classmethod
    def _from_proto(
        cls,
        proto_availability: availability_pb2.Restriction,
    ) -> Restriction:
        return cls(
            owner_id=_from_proto_guid(proto_availability.owner_id.id),
            owner_path=proto_availability.owner_id.path,
            event_id=proto_availability.event_id,
            local_id=proto_availability.local_id,
            reason=proto_availability.reason,
            category=proto_availability.category,
            created=AvailabilityRecordInfo._from_proto(proto_availability.created),
            last_changed=AvailabilityRecordInfo._from_proto(
                proto_availability.last_changed
            ),
            recurrence=(
                RestrictionBasicRecurrence._from_proto(
                    proto_availability.restriction_recurrence.basic_recurrence
                )
                if proto_availability.restriction_recurrence.WhichOneof(
                    "recurrence_oneof"
                )
                == "basic_recurrence"
                else RestrictionComplexRecurrence._from_proto(
                    proto_availability.restriction_recurrence.complex_recurrence
                )
            ),
        )


class Availability(abc.ABC):
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
        created_author: str = None,
        created_timestamp: datetime = None,
        last_changed_author: str = None,
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
            created_author: User who created this event.
            created_timestamp: When this event was created.
            last_changed_author: Last user who edited this event.

        Returns:
            Revision: An object representing the newly created revision, including
            details such as event ID, local ID, reason, owner ID, creation time,
            last modification time, and recurrence information.

        Raises:
            Exception: If the target is invalid or the revision cannot be created.
            TypeError: If required fields are missing or invalid types are provided.
        """

    def _prepare_create_revision_request(
        self,
        target: Union[uuid.UUID, str, Object],
        id: str,
        local_id: str,
        reason: str,
        created_author: str = None,
        created_timestamp: datetime = None,
        last_changed_author: str = None,
    ) -> availability_pb2.CreateRevisionRequest:
        request = availability_pb2.CreateRevisionRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=id,
            local_id=local_id,
            reason=reason,
            created_author=created_author,
            created_timestamp=(
                _datetime_to_timestamp_pb2(created_timestamp)
                if created_timestamp != None
                else None
            ),
            last_changed_author=last_changed_author,
        )
        return request

    @abc.abstractmethod
    def create_restriction(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        local_id: str,
        reason: str,
        category: str,
        recurrence: Union[RestrictionBasicRecurrence, RestrictionComplexRecurrence],
    ) -> Restriction:
        """
        Creates a new restriction for a specified Mesh object.

        A restriction defines a period during which a Mesh object is unavailable
        due to external factors. This method allows you to define the restriction
        by specifying its target, unique identifier, local identifier, reason,
        category, and recurrence details.

        Args:
            target: The Mesh object to which the new restriction belongs.
                This can be specified as a UUID or a string path.
            event_id: A unique identifier for the restriction. This must be unique
                among all restrictions belonging to the same target object.
            local_id: An additional identifier for the restriction. This does not
                need to be unique and can be used for external system references.
            reason: A description or explanation for creating the restriction.
            category: The category of the restriction.
            recurrence: The recurrence details, which can be either basic or complex.
            created_author: User who created this event.
            created_timestamp: When this event was created.
            last_changed_author: Last user who edited this event.

        Returns:
            Restriction: An object representing the newly created restriction,
            including details such as event ID, local ID, reason, owner ID,
            creation time, last modification time, and recurrence information.

        Raises:
            Exception: If the target is invalid or the restriction cannot be created.
            TypeError: If required fields are missing or invalid types are provided.
        """

    def _prepare_create_restriction_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        local_id: str,
        reason: str,
        category: str,
        recurrence: Union[RestrictionBasicRecurrence, RestrictionComplexRecurrence],
        created_author: str = None,
        created_timestamp: datetime = None,
        last_changed_author: str = None,
    ) -> availability_pb2.CreateRestrictionRequest:
        proto_recurrence = availability_pb2.RestrictionRecurrence()

        # Set the appropriate field based on the recurrence type
        if isinstance(recurrence, RestrictionBasicRecurrence):
            proto_recurrence.basic_recurrence.CopyFrom(
                RestrictionBasicRecurrence._to_proto(recurrence)
            )
        else:  # RestrictionComplexRecurrence
            proto_recurrence.complex_recurrence.CopyFrom(
                RestrictionComplexRecurrence._to_proto(recurrence)
            )

        request = availability_pb2.CreateRestrictionRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
            local_id=local_id,
            reason=reason,
            category=category,
            restriction_recurrence=proto_recurrence,
            created_author=created_author,
            created_timestamp=created_timestamp,
            last_changed_author=last_changed_author,
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
        author: str = None,
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
            author: The user who requested this change.

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
        author: str = None,
    ) -> availability_pb2.AddRevisionRecurrenceRequest:

        revision_recurrence = RevisionRecurrence(
            recurrence=recurrence, period_start=period_start, period_end=period_end
        )

        request = availability_pb2.AddRevisionRecurrenceRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
            revision_recurrence=RevisionRecurrence._to_proto(revision_recurrence),
            author=author,
        )
        return request

    @abc.abstractmethod
    def get_availability_event(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
    ) -> Union[Revision, Restriction]:
        """
        Retrieves a specific availability event (Revision or Restriction) for a given Mesh object.

        This method fetches the details of an availability event, such as a Revision or Restriction,
        based on the provided Mesh object and event identifier.

        Args:
            target: The Mesh object to which the availability event belongs.
                This can be specified as a UUID, a string path, or an Object instance.
            event_id: The unique identifier of the availability event to retrieve.

        Returns:
            The availability event as a `Revision` or `Restriction` object if found.

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
    ) -> list[Union[Revision, Restriction]]:
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
        author: str = None,
    ) -> None:
        """
        Deletes a specific recurrence associated with a revision.

        This method allows you to remove a recurrence pattern from an existing revision.

        Args:
            target: The Mesh object to which the revision belongs.
                This can be specified as a UUID, a string path, or an Object instance.
            event_id: The unique identifier of the revision from which the recurrence will be deleted.
            recurrence_id: The unique identifier of the recurrence to be deleted.
            author: The user who requested this change.

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            Exception: If the target, event_id, or recurrence_id is invalid.
        """

    def _prepare_delete_revision_recurrence_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        recurrence_id: int,
        author: str = None,
    ) -> availability_pb2.DeleteRevisionRecurrenceRequest:
        request = availability_pb2.DeleteRevisionRecurrenceRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
            recurrence_id=recurrence_id,
            author=author,
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

    @abc.abstractmethod
    def search_instances(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> Union[list[RevisionInstance], list[RestrictionInstance]]:
        """
        Searches for instances of availability events (Revisions or Restrictions) within a specific time period.

        This method retrieves the specific instances of an availability event that occur within the specified
        time period. This is particularly useful for recurring events where you want to find all occurrences
        within a date range.

        Args:
            target: The Mesh object to which the availability event belongs.
                This can be specified as a UUID, a string path, or an Object instance.
            event_id: The unique identifier of the availability event.
            period_start: The start date/time of the period to search for instances.
            period_end: The end date/time of the period to search for instances.

        Returns:
            A list of instances of the event that occur within the specified time period.
            Each instance contains information about when the event occurs and, for restriction instances, the applied value.

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            Exception: If the target or event_id is invalid or if the date range is invalid.
        """

    def _prepare_search_instances_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> availability_pb2.SearchInstancesRequest:
        request = availability_pb2.SearchInstancesRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
            interval=_to_proto_utcinterval(period_start, period_end),
        )
        return request

    @abc.abstractmethod
    def update_revision(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        new_local_id: Optional[str] = None,
        new_reason: Optional[str] = None,
        author: str = None,
    ) -> None:
        """
        Updates an existing revision with new information.

        This method allows you to modify specific fields of an existing revision,
        such as its local ID or reason. You can update either one or both fields.

        Args:
            target: The Mesh object to which the revision belongs.
                This can be specified as a UUID, a string path, or an Object instance.
            event_id: The unique identifier of the revision to be updated.
            new_local_id: The new local identifier for the revision. If None,
                the local ID will remain unchanged.
            new_reason: The new reason or description for the revision. If None,
                the reason will remain unchanged.
            author: The user who requested this change.

        Returns:
            None

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            ValueError: If neither new_local_id nor new_reason are provided.
            Exception: If the target or event_id is invalid.

        Note:
            At least one of new_local_id or new_reason must be provided.
            The updated revision will have an updated last_changed timestamp.
        """

    def _prepare_update_revision_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        new_local_id: Optional[str] = None,
        new_reason: Optional[str] = None,
        author: str = None,
    ) -> availability_pb2.UpdateRevisionRequest:

        if new_local_id is None and new_reason is None:
            raise ValueError(
                "At least one of new_local_id or new_reason must be provided"
            )

        request = availability_pb2.UpdateRevisionRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
            author=author,
        )

        fields_to_update = []

        if new_local_id is not None:
            request.new_local_id = new_local_id
            fields_to_update.append("new_local_id")

        if new_reason is not None:
            request.new_reason = new_reason
            fields_to_update.append("new_reason")

        request.field_mask.CopyFrom(
            protobuf.field_mask_pb2.FieldMask(paths=fields_to_update)
        )

        return request

    @abc.abstractmethod
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
        author: str = None,
    ) -> None:
        """
        Updates an existing restriction with new information.

        This method allows you to modify specific fields of an existing restriction,
        such as its local ID, reason, category, or recurrence details. You can update
        any combination of these fields.

        Args:
            target: The Mesh object to which the restriction belongs.
                This can be specified as a UUID, a string path, or an Object instance.
            event_id: The unique identifier of the restriction to be updated.
            new_local_id: The new local identifier for the restriction. If None,
                the local ID will remain unchanged.
            new_reason: The new reason or description for the restriction. If None,
                the reason will remain unchanged.
            new_category: The new category for the restriction. If None,
                the category will remain unchanged.
            new_restriction_recurrence: The new recurrence details for the restriction. If None,
                the recurrence details will remain unchanged.
            author: The user who requested this change.

        Raises:
            grpc.RpcError: If the gRPC request fails or the server returns an error.
            ValueError: If none of the update fields are provided.
            Exception: If the target or event_id is invalid.

        Note:
            At least one of new_local_id, new_reason, new_category, or new_restriction_recurrence
            must be provided. The updated restriction will have an updated last_changed timestamp.
        """

    def _prepare_update_restriction_request(
        self,
        target: Union[uuid.UUID, str, Object],
        event_id: str,
        new_local_id: Optional[str] = None,
        new_reason: Optional[str] = None,
        new_category: Optional[str] = None,
        new_restriction_recurrence: Optional[
            Union[RestrictionBasicRecurrence, RestrictionComplexRecurrence]
        ] = None,
        author: str = None,
    ) -> availability_pb2.UpdateRestrictionRequest:
        if (
            new_local_id is None
            and new_reason is None
            and new_category is None
            and new_restriction_recurrence is None
        ):
            raise ValueError(
                "At least one of new_local_id, new_reason, new_category, or "
                "new_restriction_recurrence must be provided"
            )

        request = availability_pb2.UpdateRestrictionRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_object_mesh_id(target),
            event_id=event_id,
            author=author,
        )

        fields_to_update = []

        if new_local_id is not None:
            request.new_local_id = new_local_id
            fields_to_update.append("new_local_id")

        if new_reason is not None:
            request.new_reason = new_reason
            fields_to_update.append("new_reason")

        if new_category is not None:
            request.new_category = new_category
            fields_to_update.append("new_category")

        if new_restriction_recurrence is not None:
            if isinstance(new_restriction_recurrence, RestrictionBasicRecurrence):
                proto_recurrence = RestrictionBasicRecurrence._to_proto(
                    new_restriction_recurrence
                )
                request.new_restriction_recurrence.basic_recurrence.CopyFrom(
                    proto_recurrence
                )
            else:
                proto_recurrence = RestrictionComplexRecurrence._to_proto(
                    new_restriction_recurrence
                )
                request.new_restriction_recurrence.complex_recurrence.CopyFrom(
                    proto_recurrence
                )

            fields_to_update.append("new_restriction_recurrence")

        request.field_mask.CopyFrom(
            protobuf.field_mask_pb2.FieldMask(paths=fields_to_update)
        )

        return request
