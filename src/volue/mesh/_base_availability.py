from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

import dateutil

from volue.mesh._common import _from_proto_guid, _to_proto_guid
from volue.mesh._mesh_id import _to_proto_object_mesh_id
from volue.mesh._object import Object
from volue.mesh.proto.availability.v1alpha import (
    availability_pb2,
    availability_pb2_grpc,
)


@dataclass
class RevisionRecurrence:
    id: int

    def _from_proto(cls, proto_recurrence: availability_pb2.RevisionRecurrence):
        id = proto_recurrence.recurrence_id
        # todo: add fields


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
            proto_record_info (availability_pb2.RecordInfo): The protobuf RecordInfo object.

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
        recurrence: A list of recurrence patterns associated with the revision.
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
            # recurrences = proto_availability.recurrences
        )


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
        self, target: Union[uuid.UUID, str], id: str, local_id: str, reason: str
    ) -> Revision:
        """
        Creates a new revision for a specified Mesh object.

        A revision represents a period during which a Mesh object is unavailable.
        This method allows you to define the revision by specifying its target,
        unique identifier, local identifier, and the reason for its creation.

        Args:
            target: The Mesh object to which the new revision belongs.
                This can be specified as a UUID or a string path.
            id: A unique identifier for the revision. This must be unique
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
