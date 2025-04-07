import sys
from datetime import datetime

import grpc
import pytest

from volue.mesh._base_availability import Recurrence, RecurrenceType, RevisionRecurrence

THERMAL_COMPONENT_PATH = "Model/SimpleThermalTestModel/ThermalComponent"


@pytest.mark.database
def test_create_revision(connection):
    with connection.create_session() as session:
        revision = session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            id="event_id",
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
                id="event_id",
                local_id="local_id",
                reason="reason",
            )


@pytest.mark.database
def test_create_revision_with_missing_fields(connection):
    with connection.create_session() as session:
        with pytest.raises(grpc.RpcError, match="no event id provided"):
            session.availability.create_revision(
                target=THERMAL_COMPONENT_PATH,
                id=None,  # Missing required field
                local_id="local_id",
                reason="reason",
            )


@pytest.mark.database
def test_create_revision_with_duplicate_id(connection):
    with connection.create_session() as session:
        session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            id="duplicate_id",
            local_id="local_id_1",
            reason="reason_1",
        )
        with pytest.raises(grpc.RpcError, match="event with event id"):
            session.availability.create_revision(
                target=THERMAL_COMPONENT_PATH,
                id="duplicate_id",  # Duplicate ID
                local_id="local_id_2",
                reason="reason_2",
            )


@pytest.mark.database
def test_create_revision_with_empty_reason(connection):
    with connection.create_session() as session:
        revision = session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            id="event_id_empty_reason",
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
def test_add_revision_recurrence(session):
    revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        id="event_id",
        local_id="local_id",
        reason="reason",
    )

    recurrence = session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        recurrence=RevisionRecurrence(
            period_start=datetime(2023, 1, 1),
            period_end=datetime(2023, 1, 2),
            recurrence=Recurrence(
                status="Planned",
                description="Test Recurrence",
                recurrence_type=RecurrenceType.NONE,
            ),
        ),
    )

    assert recurrence == 0

    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )

    assert len(revision.recurrences) == 1


@pytest.mark.asyncio
@pytest.mark.database
async def test_create_revision_async(async_session):
    revision = await async_session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        id="event_id",
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


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
