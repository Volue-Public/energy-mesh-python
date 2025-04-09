import sys
from datetime import datetime

import dateutil
import grpc
import pytest

from volue.mesh.availability import (
    EventType,
    Recurrence,
    RecurrenceType,
    RevisionRecurrence,
)

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


@pytest.mark.database
def test_search_availability_events(connection):
    with connection.create_session() as session:
        # Create a revision
        revision = session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            event_id="search_event_id",
            local_id="search_local_id",
            reason="search_reason",
        )

        # Search for the revision
        results = session.availability.search_availability_events(
            event_type=EventType.REVISION,
            targets=[THERMAL_COMPONENT_PATH],
        )

        # Assert that the search returned at least one result
        assert len(results) > 0

        # Find our specific revision in results
        found = False
        for result in results:
            if result.event_id == "search_event_id":
                found = True
                assert result.local_id == "search_local_id"
                assert result.reason == "search_reason"
                break

        assert found, "Created revision not found in search results"


@pytest.mark.database
def test_delete_revision_recurrence(session):
    # Create a revision
    revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="delete_recurrence_event",
        local_id="local_id",
        reason="reason",
    )

    # Add a recurrence
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

    # Verify the recurrence was added
    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )
    assert len(revision.recurrences) == 1

    # Delete the recurrence
    session.availability.delete_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        recurrence_id=recurrence_id,
    )

    # Verify the recurrence was deleted
    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )
    assert len(revision.recurrences) == 0


@pytest.mark.database
def test_delete_availability_events_by_id(session):
    # Create two revisions
    revision1 = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="delete_event_1",
        local_id="local_id_1",
        reason="reason_1",
    )

    revision2 = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="delete_event_2",
        local_id="local_id_2",
        reason="reason_2",
    )

    # Delete one revision by ID
    session.availability.delete_availability_events_by_id(
        target=THERMAL_COMPONENT_PATH,
        event_ids=["delete_event_1"],
    )

    # Search for revisions to verify deletion
    results = session.availability.search_availability_events(
        event_type=EventType.REVISION,
        targets=[THERMAL_COMPONENT_PATH],
    )

    # Check that delete_event_1 is gone but delete_event_2 still exists
    found_event_1 = False
    found_event_2 = False

    for revision in results:
        if revision.event_id == "delete_event_1":
            found_event_1 = True
        if revision.event_id == "delete_event_2":
            found_event_2 = True

    assert not found_event_1, "Event 1 should have been deleted"
    assert found_event_2, "Event 2 should still exist"


@pytest.mark.database
def test_delete_all_availability_events(session):
    # Create unique event IDs for this test to avoid conflicts
    test_id_prefix = "delete_all_test_"

    # Create multiple revisions with unique IDs
    for i in range(3):
        session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            event_id=f"{test_id_prefix}{i}",
            local_id=f"local_id_{i}",
            reason=f"reason_{i}",
        )

    # Verify revisions were created
    results_before = session.availability.search_availability_events(
        event_type=EventType.REVISION,
        targets=[THERMAL_COMPONENT_PATH],
    )

    test_revisions_before = [
        r for r in results_before if r.event_id.startswith(test_id_prefix)
    ]
    assert len(test_revisions_before) == 3

    # Delete all revisions for the target
    session.availability.delete_availability_events(
        target=THERMAL_COMPONENT_PATH,
        event_type=EventType.REVISION,
    )

    # Verify all revisions were deleted
    results_after = session.availability.search_availability_events(
        event_type=EventType.REVISION,
        targets=[THERMAL_COMPONENT_PATH],
    )

    test_revisions_after = [
        r for r in results_after if r.event_id.startswith(test_id_prefix)
    ]
    assert len(test_revisions_after) == 0


@pytest.mark.database
def test_add_multiple_recurrences(session):
    # Create a revision
    revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="multi_recurrence_event",
        local_id="local_id",
        reason="reason",
    )

    # Add multiple recurrences with different patterns
    recurrence_id1 = session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC),
        recurrence=Recurrence(
            status="Planned",
            description="Daily Recurrence",
            recurrence_type=RecurrenceType.DAILY,
            recur_every=1,
            recur_until=datetime(2023, 1, 15, tzinfo=dateutil.tz.UTC),
        ),
    )

    recurrence_id2 = session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 2, tzinfo=dateutil.tz.UTC),
        recurrence=Recurrence(
            status="Planned",
            description="Weekly Recurrence",
            recurrence_type=RecurrenceType.WEEKLY,
            recur_every=2,
            recur_until=datetime(2023, 2, 15, tzinfo=dateutil.tz.UTC),
        ),
    )

    # Verify both recurrences were added
    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )

    assert len(revision.recurrences) == 2

    # Verify recurrence details
    recurrences_by_id = {r.id: r for r in revision.recurrences}

    assert (
        recurrences_by_id[recurrence_id1].recurrence.description == "Daily Recurrence"
    )
    assert (
        recurrences_by_id[recurrence_id1].recurrence.recurrence_type
        == RecurrenceType.DAILY
    )
    assert recurrences_by_id[recurrence_id1].recurrence.recur_every == 1

    assert (
        recurrences_by_id[recurrence_id2].recurrence.description == "Weekly Recurrence"
    )
    assert (
        recurrences_by_id[recurrence_id2].recurrence.recurrence_type
        == RecurrenceType.WEEKLY
    )
    assert recurrences_by_id[recurrence_id2].recurrence.recur_every == 2


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
