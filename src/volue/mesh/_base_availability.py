from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

import dateutil
import dateutil.tz
from google.protobuf.timestamp_pb2 import Timestamp

from volue.mesh._common import _from_proto_guid, _to_proto_guid
from volue.mesh._mesh_id import _to_proto_mesh_id
from volue.mesh.proto.availability.v1alpha import (
    availability_pb2,
    availability_pb2_grpc,
)


class RevisionRecurrence:
    def __init__(self, proto_recurrence: availability_pb2.RevisionRecurrence):
        self.id: int = proto_recurrence.recurrence_id
        # todo: add fields


@dataclass
class AvailabilityRecordInfo:
    """Record information for availability revisions."""

    author: str
    timestamp: datetime

    @classmethod
    def _from_proto(
        cls, proto_record_info: availability_pb2.RecordInfo
    ) -> AvailabilityRecordInfo:
        return cls(
            author=proto_record_info.author,
            timestamp=proto_record_info.timestamp.ToDatetime(dateutil.tz.UTC),
        )


class Revision:
    def __init__(
        self,
        proto_availability: availability_pb2.Revision,
    ):
        self.owner_id: uuid.UUID = _from_proto_guid(proto_availability.owner_id.id)
        self.owner_path: str = proto_availability.owner_id.path
        self.event_id: str = proto_availability.event_id
        self.local_id: str = proto_availability.local_id
        self.reason: str = proto_availability.reason
        self.created: AvailabilityRecordInfo = AvailabilityRecordInfo._from_proto(
            proto_availability.created
        )
        self.last_changed: AvailabilityRecordInfo = AvailabilityRecordInfo._from_proto(
            proto_availability.last_changed
        )
        self.recurrence: list[RevisionRecurrence] = proto_availability.recurrences


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
            target (Union[uuid.UUID, str]): The Mesh object to which the new revision belongs.
                This can be specified as a UUID or a string path.
            id (str): A unique identifier for the revision. This must be unique
                among all revisions belonging to the same target object.
            local_id (str): An additional identifier for the revision. This does not
                need to be unique and can be used for external system references.
            reason (str): A description or explanation for creating the revision.

        Returns:
            Revision: An object representing the newly created revision, including
            details such as event ID, local ID, reason, owner ID, creation time,
            last modification time, and recurrence information.

        Raises:
            Exception: If the target is invalid or the revision cannot be created.
            TypeError: If required fields are missing or invalid types are provided.
        """

    def _prepare_create_revision_request(
        self, target: Union[uuid.UUID, str], id: str, local_id: str, reason: str
    ) -> availability_pb2.CreateRevisionRequest:
        request = availability_pb2.CreateRevisionRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_mesh_id(target),
            event_id=id,
            local_id=local_id,
            reason=reason,
        )
        return request
