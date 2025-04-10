import sys
from datetime import datetime

import dateutil
import grpc
import pytest

from volue.mesh.availability import Recurrence, RecurrenceType, RevisionRecurrence

THERMAL_COMPONENT_PATH = "Model/SimpleThermalTestModel/ThermalComponent"


@pytest.mark.database
def test_create_revision(connection):
    with connection.create_session() as session:
        revision = session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            event_id="event_id",
            local_id="local_id",
            reason="reason",
        )

        # Assert basic fields
        assert revision.event_id == "event_id"
        assert revision.local_id == "local_id"
        assert revision.reason == "reason"
        assert revision.owner_id is not None

        # Assert created record info
        assert revision.created.author is not None
        assert isinstance(revision.created.timestamp, datetime)

        # Assert last_changed record info
        assert revision.last_changed.author is not None
        assert isinstance(revision.last_changed.timestamp, datetime)

        assert revision.recurrences == []


@pytest.mark.database
def test_create_revision_with_invalid_target(connection):
    with connection.create_session() as session:
        with pytest.raises(grpc.RpcError, match="object not found"):
            session.availability.create_revision(
                target="Invalid/Path",
                event_id="event_id",
                local_id="local_id",
                reason="reason",
            )


@pytest.mark.database
def test_create_revision_with_missing_fields(connection):
    with connection.create_session() as session:
        with pytest.raises(grpc.RpcError, match="no event id provided"):
            session.availability.create_revision(
                target=THERMAL_COMPONENT_PATH,
                event_id=None,  # Missing required field
                local_id="local_id",
                reason="reason",
            )


@pytest.mark.database
def test_create_revision_with_duplicate_id(connection):
    with connection.create_session() as session:
        session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            event_id="duplicate_id",
            local_id="local_id_1",
            reason="reason_1",
        )
        with pytest.raises(grpc.RpcError, match="event with event id"):
            session.availability.create_revision(
                target=THERMAL_COMPONENT_PATH,
                event_id="duplicate_id",  # Duplicate ID
                local_id="local_id_2",
                reason="reason_2",
            )


@pytest.mark.database
def test_create_revision_with_empty_reason(connection):
    with connection.create_session() as session:
        revision = session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            event_id="event_id_empty_reason",
            local_id="local_id",
            reason="",  # Empty reason
        )

        # Assert basic fields
        assert revision.reason == ""
        assert revision.event_id == "event_id_empty_reason"
        assert revision.local_id == "local_id"

        # Assert created record info
        assert revision.created.author is not None
        assert isinstance(revision.created.timestamp, datetime)

        # Assert last_changed record info
        assert revision.last_changed.author is not None
        assert isinstance(revision.last_changed.timestamp, datetime)


@pytest.mark.database
def test_add_revision_recurrence_and_get_event(session):
    revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="event_id",
        local_id="local_id",
        reason="reason",
    )

    recurrence_id = session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC),
        recurrence=Recurrence(
            status="Planned",
            description="Test Recurrence",
            recurrence_type=RecurrenceType.NONE,
        ),
    )

    assert recurrence_id == 0

    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )

    # Assert basic fields
    assert revision.event_id == "event_id"
    assert revision.local_id == "local_id"
    assert revision.reason == "reason"
    assert revision.owner_id is not None

    # Assert created record info
    assert revision.created.author is not None
    assert isinstance(revision.created.timestamp, datetime)

    # Assert last_changed record info
    assert revision.last_changed.author is not None
    assert isinstance(revision.last_changed.timestamp, datetime)

    assert len(revision.recurrences) == 1

    recurrence = revision.recurrences[0]
    assert recurrence.period_start == datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC)
    assert recurrence.period_end == datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC)
    assert recurrence.recurrence.status == "Planned"
    assert recurrence.recurrence.description == "Test Recurrence"
    assert recurrence.recurrence.recurrence_type == RecurrenceType.NONE


@pytest.mark.asyncio
@pytest.mark.database
async def test_create_revision_async(async_session):
    revision = await async_session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="event_id",
        local_id="local_id",
        reason="reason",
    )

    # Assert basic fields
    assert revision.event_id == "event_id"
    assert revision.local_id == "local_id"
    assert revision.reason == "reason"
    assert revision.owner_id is not None

    # Assert created record info
    assert revision.created.author is not None
    assert isinstance(revision.created.timestamp, datetime)

    # Assert last_changed record info
    assert revision.last_changed.author is not None
    assert isinstance(revision.last_changed.timestamp, datetime)

    recurrence_id = await async_session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC),
        recurrence=Recurrence(
            status="Planned",
            description="Test Recurrence",
            recurrence_type=RecurrenceType.NONE,
        ),
    )

    assert recurrence_id == 0

    revision_from_mesh = await async_session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )

    assert revision_from_mesh.event_id == revision.event_id
    assert revision_from_mesh.local_id == revision.local_id
    assert revision_from_mesh.reason == revision.reason
    assert revision_from_mesh.owner_id == revision.owner_id
    assert revision_from_mesh.created.author == revision.created.author
    assert revision_from_mesh.created.timestamp == revision.created.timestamp

    assert len(revision_from_mesh.recurrences) == 1

    recurrence = revision_from_mesh.recurrences[0]
    assert recurrence.period_start == datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC)
    assert recurrence.period_end == datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC)
    assert recurrence.recurrence.status == "Planned"
    assert recurrence.recurrence.description == "Test Recurrence"
    assert recurrence.recurrence.recurrence_type == RecurrenceType.NONE


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
