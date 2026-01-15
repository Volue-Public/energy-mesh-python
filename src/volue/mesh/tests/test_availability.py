import sys
from datetime import datetime

import dateutil
import grpc
import pytest

from volue.mesh.availability import (
    EventType,
    Recurrence,
    RecurrenceType,
    Restriction,
    RestrictionBasicRecurrence,
    RestrictionComplexRecurrence,
    RestrictionInstance,
    Revision,
    RevisionInstance,
    TimePoint,
)

THERMAL_COMPONENT_PATH = "Model/SimpleThermalTestModel/ThermalComponent"


@pytest.mark.database
def test_create_revision(connection):
    with connection.create_session() as session:
        event_id = "event_id"
        local_id = "local_id"
        reason = "reason"
        created_author = "created_author"
        created_timestamp = datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC)
        last_changed_author = "last_changed_author"

        revision = session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            event_id=event_id,
            local_id=local_id,
            reason=reason,
            created_author=created_author,
            created_timestamp=created_timestamp,
            last_changed_author=last_changed_author
        )

        assert revision.event_id == event_id
        assert revision.local_id == local_id
        assert revision.reason == reason
        assert revision.created_author == created_author
        assert revision.created_timestamp == created_timestamp
        assert revision.last_changed_author == last_changed_author

        assert revision.owner_id is not None

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
    event_id = "event_id"
    local_id = "local_id"
    reason = "reason"
    created_author = "created_author"

    revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id=event_id,
        local_id=local_id,
        reason=reason,
        created_author=created_author,
    )

    assert revision.event_id == event_id
    assert revision.local_id == local_id
    assert revision.reason == reason
    assert revision.created_author == created_author

    period_start = datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC)
    period_end = datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC)
    status = "Planned"
    description = "Test Recurrence"
    recurrence_type = RecurrenceType.NONE
    add_revision_recurrence_author = "add_revision_recurrence_author"

    recurrence_id = session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=period_start,
        period_end=period_end,
        recurrence=Recurrence(
            status=status,
            description=description,
            recurrence_type=recurrence_type,
        ),
        author=add_revision_recurrence_author,
    )

    assert recurrence_id == 0

    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )

    assert revision.created_author == created_author
    assert revision.last_changed_author == add_revision_recurrence_author

    assert len(revision.recurrences) == 1

    recurrence = revision.recurrences[0]
    assert recurrence.period_start == period_start
    assert recurrence.period_end == period_end
    assert recurrence.recurrence.status == status
    assert recurrence.recurrence.description == description
    assert recurrence.recurrence.recurrence_type == recurrence_type


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

        assert isinstance(revision, Revision)

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
            assert isinstance(result, Revision)
            if result.event_id == "search_event_id":
                found = True
                assert result.local_id == "search_local_id"
                assert result.reason == "search_reason"
                break

        assert found, "Created revision not found in search results"


@pytest.mark.database
def test_delete_revision_recurrence(session):
    event_id = "delete_recurrence_event"
    local_id = "local_id"
    reason = "reason"
    created_author = "created_author"

    # Create a revision
    revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="delete_recurrence_event",
        local_id="local_id",
        reason="reason",
        created_author=created_author,
    )

    add_revision_recurrence_author = "add_revision_recurrence_author"

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
        author=add_revision_recurrence_author,
    )

    # Verify the recurrence was added
    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )
    assert len(revision.recurrences) == 1

    assert isinstance(revision, Revision)

    assert revision.created_author == created_author
    assert revision.last_changed_author == add_revision_recurrence_author

    delete_revision_recurrence_author = "delete_revision_recurrence_author"

    # Delete the recurrence
    session.availability.delete_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        recurrence_id=recurrence_id,
        author=delete_revision_recurrence_author,
    )

    # Verify the recurrence was deleted
    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )
    assert len(revision.recurrences) == 0

    assert revision.created_author == created_author
    assert revision.last_changed_author == delete_revision_recurrence_author


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
    created_author = "created_author"

    revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="multi_recurrence_event",
        local_id="local_id",
        reason="reason",
        created_author=created_author,
    )

    add_revision_recurrence_author_1 = "add_revision_recurrence_author_1"

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
        author=add_revision_recurrence_author_1,
    )

    add_revision_recurrence_author_2 = "add_revision_recurrence_author_2"

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
        author=add_revision_recurrence_author_2,
    )

    # Verify both recurrences were added
    revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
    )

    assert len(revision.recurrences) == 2

    assert revision.created_author == created_author
    assert revision.last_changed_author == add_revision_recurrence_author_2

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


@pytest.mark.database
def test_create_restriction_with_basic_recurrence(connection):
    event_id = "basic_restriction_event"
    local_id = "basic_restriction_local_id"
    reason = "Basic restriction reason"
    category = "DischargeMin[m3/s]"

    status = "SelfImposed"
    description = "Basic test restriction"
    recurrence_type = RecurrenceType.NONE
    period_start = datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC)
    period_end = datetime(2023, 1, 10, tzinfo=dateutil.tz.UTC)
    value = 0.5

    with connection.create_session() as session:
        # Create a restriction with basic recurrence
        restriction = session.availability.create_restriction(
            target=THERMAL_COMPONENT_PATH,
            event_id=event_id,
            local_id=local_id,
            reason=reason,
            category=category,
            recurrence=RestrictionBasicRecurrence(
                recurrence=Recurrence(
                    status=status,
                    description=description,
                    recurrence_type=recurrence_type,
                ),
                period_start=period_start,
                period_end=period_end,
                value=value,
            ),
        )

        assert isinstance(restriction, Restriction)

        # Assert basic fields
        assert restriction.event_id == event_id
        assert restriction.local_id == local_id
        assert restriction.reason == reason
        assert restriction.category == category

        assert restriction.owner_id is not None

        # Assert recurrence details
        assert isinstance(restriction.recurrence, RestrictionBasicRecurrence)
        assert restriction.recurrence.recurrence.status == status
        assert restriction.recurrence.recurrence.description == description
        assert restriction.recurrence.recurrence.recurrence_type == recurrence_type
        assert restriction.recurrence.period_start == period_start
        assert restriction.recurrence.period_end == period_end
        assert restriction.recurrence.value == value


@pytest.mark.database
def test_create_restriction_with_complex_recurrence(connection):
    with connection.create_session() as session:
        # Create a restriction with complex recurrence
        time_points = [
            TimePoint(
                value=80.0, timestamp=datetime(2023, 1, 1, 8, 0, tzinfo=dateutil.tz.UTC)
            ),
            TimePoint(
                value=60.0,
                timestamp=datetime(2023, 1, 1, 12, 0, tzinfo=dateutil.tz.UTC),
            ),
            TimePoint(
                value=70.0,
                timestamp=datetime(2023, 1, 1, 16, 0, tzinfo=dateutil.tz.UTC),
            ),
            TimePoint(
                value=90.0,
                timestamp=datetime(2023, 1, 1, 20, 0, tzinfo=dateutil.tz.UTC),
            ),
        ]

        restriction = session.availability.create_restriction(
            target=THERMAL_COMPONENT_PATH,
            event_id="complex_restriction_event",
            local_id="complex_restriction_local_id",
            reason="Complex restriction reason",
            category="DischargeMin[m3/s]",
            recurrence=RestrictionComplexRecurrence(
                recurrence=Recurrence(
                    status="SelfImposed",
                    description="Complex test restriction",
                    recurrence_type=RecurrenceType.DAILY,
                    recur_every=1,
                    recur_until=datetime(2023, 1, 15, tzinfo=dateutil.tz.UTC),
                ),
                time_points=time_points,
            ),
        )

        # Assert basic fields
        assert restriction.event_id == "complex_restriction_event"
        assert restriction.local_id == "complex_restriction_local_id"
        assert restriction.reason == "Complex restriction reason"
        assert restriction.category == "DischargeMin[m3/s]"
        assert restriction.owner_id is not None

        # Assert recurrence details
        assert isinstance(restriction.recurrence, RestrictionComplexRecurrence)
        assert restriction.recurrence.recurrence.status == "SelfImposed"
        assert (
            restriction.recurrence.recurrence.description == "Complex test restriction"
        )
        assert restriction.recurrence.recurrence.recurrence_type == RecurrenceType.DAILY
        assert restriction.recurrence.recurrence.recur_every == 1
        assert restriction.recurrence.recurrence.recur_until == datetime(
            2023, 1, 15, tzinfo=dateutil.tz.UTC
        )

        # Assert time points
        assert len(restriction.recurrence.time_points) == 4

        # Verify the time points are preserved
        time_point_values = [tp.value for tp in restriction.recurrence.time_points]
        time_point_timestamps = [
            tp.timestamp for tp in restriction.recurrence.time_points
        ]

        assert 80.0 in time_point_values
        assert 60.0 in time_point_values
        assert 70.0 in time_point_values
        assert 90.0 in time_point_values


@pytest.mark.database
def test_create_restriction_with_invalid_target(connection):
    with connection.create_session() as session:
        with pytest.raises(grpc.RpcError, match="object not found"):
            session.availability.create_restriction(
                target="Invalid/Path",
                event_id="invalid_restriction_event",
                local_id="local_id",
                reason="reason",
                category="Capacity",
                recurrence=RestrictionBasicRecurrence(
                    recurrence=Recurrence(
                        status="Active",
                        description="Test restriction",
                        recurrence_type=RecurrenceType.NONE,
                    ),
                    period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
                    period_end=datetime(2023, 1, 10, tzinfo=dateutil.tz.UTC),
                    value=75.5,
                ),
            )


@pytest.mark.database
def test_search_and_get_restriction(session):
    # Create a restriction
    restriction = session.availability.create_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="searchable_restriction_event",
        local_id="searchable_restriction_local_id",
        reason="Searchable restriction reason",
        category="DischargeMin[m3/s]",
        recurrence=RestrictionBasicRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="Searchable test restriction",
                recurrence_type=RecurrenceType.NONE,
            ),
            period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
            period_end=datetime(2023, 1, 10, tzinfo=dateutil.tz.UTC),
            value=75.5,
        ),
    )

    # Search for the restriction
    results = session.availability.search_availability_events(
        event_type=EventType.RESTRICTION,
        targets=[THERMAL_COMPONENT_PATH],
    )

    # Assert we found at least one restriction
    assert len(results) > 0

    # Find our specific restriction in results
    found = False
    for result in results:

        assert isinstance(result, Restriction)

        if result.event_id == "searchable_restriction_event":
            found = True
            assert result.local_id == "searchable_restriction_local_id"
            assert result.reason == "Searchable restriction reason"
            assert result.category == "DischargeMin[m3/s]"
            break

    assert found, "Created restriction not found in search results"

    # Get the restriction directly
    retrieved_restriction = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="searchable_restriction_event",
    )

    assert isinstance(result, Restriction)

    # Verify it matches what we created
    assert retrieved_restriction.event_id == "searchable_restriction_event"
    assert retrieved_restriction.local_id == "searchable_restriction_local_id"
    assert retrieved_restriction.reason == "Searchable restriction reason"
    assert retrieved_restriction.category == "DischargeMin[m3/s]"

    # Verify recurrence details
    assert isinstance(retrieved_restriction.recurrence, RestrictionBasicRecurrence)


@pytest.mark.database
def test_search_instances(session):
    # Create a revision with a recurrence that repeats daily for 5 days
    revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="search_instances_event",
        local_id="search_instances_local_id",
        reason="Search instances test",
    )

    # Add a repeating recurrence
    session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 1, 1, 8, 0, tzinfo=dateutil.tz.UTC),  # 8 AM
        period_end=datetime(2023, 1, 1, 16, 0, tzinfo=dateutil.tz.UTC),  # 4 PM
        recurrence=Recurrence(
            status="Planned",
            description="Daily Recurrence for Search Test",
            recurrence_type=RecurrenceType.DAILY,
            recur_every=1,
            recur_until=datetime(
                2023, 1, 5, 23, 59, tzinfo=dateutil.tz.UTC
            ),  # For 5 days
        ),
    )

    # Search for all instances in a 3-day period
    search_start = datetime(2023, 1, 2, 0, 0, tzinfo=dateutil.tz.UTC)  # Day 2
    search_end = datetime(2023, 1, 4, 23, 59, tzinfo=dateutil.tz.UTC)  # Day 4

    instances = session.availability.search_instances(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=search_start,
        period_end=search_end,
    )

    # We should have 3 instances (for days 2, 3, and 4)
    assert len(instances) == 3

    expected_day = 2
    for i, instance in enumerate(instances):
        assert isinstance(instance, RevisionInstance)

        # Each instance should be from 8 AM to 4 PM on consecutive days
        expected_start = datetime(2023, 1, expected_day, 8, 0, tzinfo=dateutil.tz.UTC)
        expected_end = datetime(2023, 1, expected_day, 16, 0, tzinfo=dateutil.tz.UTC)
        expected_day += 1
        assert instance.period_start == expected_start
        assert instance.period_end == expected_end


@pytest.mark.database
def test_search_restriction_instances(session):
    # Create a restriction with a complex recurrence pattern
    restriction = session.availability.create_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="search_restriction_instances",
        local_id="search_restriction_local_id",
        reason="Search restriction instances test",
        category="DischargeMin[m3/s]",
        recurrence=RestrictionBasicRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="Weekly Recurrence for Restriction Test",
                recurrence_type=RecurrenceType.WEEKLY,
                recur_every=1,
                recur_until=datetime(2023, 2, 15, tzinfo=dateutil.tz.UTC),
            ),
            period_start=datetime(2023, 1, 5, tzinfo=dateutil.tz.UTC),
            period_end=datetime(2023, 1, 6, tzinfo=dateutil.tz.UTC),
            value=42.5,
        ),
    )

    # Search for instances over a 4-week period
    search_start = datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC)
    search_end = datetime(2023, 1, 31, tzinfo=dateutil.tz.UTC)

    instances = session.availability.search_instances(
        target=THERMAL_COMPONENT_PATH,
        event_id=restriction.event_id,
        period_start=search_start,
        period_end=search_end,
    )

    # We should have multiple instances (one per week)
    assert len(instances) >= 4

    # Verify each instance has the correct value
    for instance in instances:
        assert isinstance(instance, RestrictionInstance)
        assert instance.value == 42.5

        # Each instance should be exactly 1 day long
        instance_duration = instance.period_end - instance.period_start
        assert instance_duration.days == 1

        # Instances should be on Thursday-Friday (day 5-6) each week
        assert instance.period_start.weekday() == 3  # Thursday (0=Monday, 3=Thursday)


@pytest.mark.database
def test_update_revision(session):
    # Create a revision
    original_revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_revision_event",
        local_id="original_local_id",
        reason="Original reason",
    )

    # Update the revision with new values
    session.availability.update_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_revision_event",
        new_local_id="updated_local_id",
        new_reason="Updated reason",
    )

    # Fetch the revision to confirm update
    retrieved_revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_revision_event",
    )

    # Verify retrieved revision has updated values
    assert retrieved_revision.local_id == "updated_local_id"
    assert retrieved_revision.reason == "Updated reason"

    # Verify timestamps reflect the update
    assert retrieved_revision.created.timestamp == original_revision.created.timestamp
    assert (
        retrieved_revision.last_changed.timestamp
        >= original_revision.last_changed.timestamp
    )


@pytest.mark.database
def test_update_revision_partial(session):
    # Create a revision
    original_revision = session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_revision_partial_event",
        local_id="original_local_id",
        reason="Original reason",
    )

    # Update only the local_id
    session.availability.update_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_revision_partial_event",
        new_local_id="updated_local_id",
        new_reason=None,  # Don't update reason
    )

    # Fetch the revision to verify partial update
    retrieved_revision = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_revision_partial_event",
    )

    # Verify only local_id was updated
    assert retrieved_revision.local_id == "updated_local_id"
    assert retrieved_revision.reason == "Original reason"


@pytest.mark.database
def test_update_restriction(session):
    # Create a basic restriction
    original_restriction = session.availability.create_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_event",
        local_id="original_local_id",
        reason="Original reason",
        category="DischargeMin[m3/s]",
        recurrence=RestrictionBasicRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="Original restriction",
                recurrence_type=RecurrenceType.NONE,
            ),
            period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
            period_end=datetime(2023, 1, 10, tzinfo=dateutil.tz.UTC),
            value=0.5,
        ),
    )

    # Update the restriction with new values
    new_recurrence = RestrictionBasicRecurrence(
        recurrence=Recurrence(
            status="SelfImposed",
            description="Updated restriction",
            recurrence_type=RecurrenceType.NONE,
        ),
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 10, tzinfo=dateutil.tz.UTC),
        value=1.0,
    )

    session.availability.update_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_event",
        new_local_id="updated_local_id",
        new_reason="Updated reason",
        new_category="DischargeMax[m3/s]",
        new_restriction_recurrence=new_recurrence,
    )

    # Get the restriction to verify updates
    updated_restriction = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_event",
    )

    # Verify the restriction was updated
    assert updated_restriction.event_id == "update_restriction_event"
    assert updated_restriction.local_id == "updated_local_id"
    assert updated_restriction.reason == "Updated reason"
    assert updated_restriction.category == "DischargeMax[m3/s]"

    # Verify recurrence details were updated
    assert isinstance(updated_restriction.recurrence, RestrictionBasicRecurrence)
    assert (
        updated_restriction.recurrence.recurrence.description == "Updated restriction"
    )
    assert updated_restriction.recurrence.period_start == datetime(
        2023, 2, 1, tzinfo=dateutil.tz.UTC
    )
    assert updated_restriction.recurrence.period_end == datetime(
        2023, 2, 10, tzinfo=dateutil.tz.UTC
    )
    assert updated_restriction.recurrence.value == 1.0

    # Verify timestamps reflect the update
    assert (
        updated_restriction.created.timestamp == original_restriction.created.timestamp
    )
    assert (
        updated_restriction.last_changed.timestamp
        >= original_restriction.last_changed.timestamp
    )


@pytest.mark.database
def test_update_restriction_partial(session):
    # Create a restriction
    original_restriction = session.availability.create_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_partial_event",
        local_id="original_local_id",
        reason="Original reason",
        category="DischargeMin[m3/s]",
        recurrence=RestrictionBasicRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="Original restriction",
                recurrence_type=RecurrenceType.NONE,
            ),
            period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
            period_end=datetime(2023, 1, 10, tzinfo=dateutil.tz.UTC),
            value=0.5,
        ),
    )

    # Update only the category and reason
    session.availability.update_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_partial_event",
        new_category="DischargeMax[m3/s]",
        new_reason="Updated reason",
        new_local_id=None,  # Don't update local_id
        new_restriction_recurrence=None,  # Don't update recurrence
    )

    # Fetch the restriction to verify partial update
    retrieved_restriction = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_partial_event",
    )

    # Verify only category and reason were updated
    assert retrieved_restriction.category == "DischargeMax[m3/s]"
    assert retrieved_restriction.reason == "Updated reason"
    assert retrieved_restriction.local_id == "original_local_id"

    # Verify recurrence details were not updated
    assert isinstance(retrieved_restriction.recurrence, RestrictionBasicRecurrence)
    assert (
        retrieved_restriction.recurrence.recurrence.description
        == "Original restriction"
    )
    assert retrieved_restriction.recurrence.period_start == datetime(
        2023, 1, 1, tzinfo=dateutil.tz.UTC
    )
    assert retrieved_restriction.recurrence.period_end == datetime(
        2023, 1, 10, tzinfo=dateutil.tz.UTC
    )
    assert retrieved_restriction.recurrence.value == 0.5


@pytest.mark.database
def test_update_restriction_complex_to_basic(session):
    # Create a complex restriction
    complex_restriction = session.availability.create_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_complex_to_basic",
        local_id="complex_local_id",
        reason="Complex reason",
        category="DischargeMin[m3/s]",
        recurrence=RestrictionComplexRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="Complex restriction",
                recurrence_type=RecurrenceType.DAILY,
                recur_every=1,
                recur_until=datetime(2023, 1, 15, tzinfo=dateutil.tz.UTC),
            ),
            time_points=[
                TimePoint(
                    value=80.0,
                    timestamp=datetime(2023, 1, 1, 8, 0, tzinfo=dateutil.tz.UTC),
                ),
                TimePoint(
                    value=60.0,
                    timestamp=datetime(2023, 1, 1, 12, 0, tzinfo=dateutil.tz.UTC),
                ),
            ],
        ),
    )

    # Update to a basic restriction
    basic_recurrence = RestrictionBasicRecurrence(
        recurrence=Recurrence(
            status="SelfImposed",
            description="Basic restriction",
            recurrence_type=RecurrenceType.NONE,
        ),
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 10, tzinfo=dateutil.tz.UTC),
        value=1.0,
    )

    # Update the restriction - returns None
    session.availability.update_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_complex_to_basic",
        new_restriction_recurrence=basic_recurrence,
    )

    # Fetch the updated restriction
    retrieved_restriction = session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="update_restriction_complex_to_basic",
    )

    # Verify the restriction was updated from complex to basic
    assert isinstance(retrieved_restriction.recurrence, RestrictionBasicRecurrence)
    assert (
        retrieved_restriction.recurrence.recurrence.description == "Basic restriction"
    )
    assert retrieved_restriction.recurrence.value == 1.0


@pytest.mark.database
def test_update_revision_throws_exception_when_no_parameters(session):

    # Test that an exception is raised when no parameters provided
    with pytest.raises(
        ValueError, match="At least one of new_local_id or new_reason must be provided"
    ):
        session.availability._prepare_update_revision_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_revision_test",
            new_local_id=None,
            new_reason=None,
        )

    # Test that no exception is raised when at least one parameter is provided
    try:
        # With only new_local_id
        session.availability._prepare_update_revision_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_revision_test",
            new_local_id="new_id",
            new_reason=None,
        )

        # With only new_reason
        session.availability._prepare_update_revision_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_revision_test",
            new_local_id=None,
            new_reason="new reason",
        )

        # With both parameters
        session.availability._prepare_update_revision_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_revision_test",
            new_local_id="new_id",
            new_reason="new reason",
        )
    except ValueError:
        pytest.fail("ValueError was raised unexpectedly!")


@pytest.mark.database
def test_update_restriction_throws_exception_when_no_parameters(session):

    with pytest.raises(
        ValueError,
        match="At least one of new_local_id, new_reason, new_category, or new_restriction_recurrence must be provided",
    ):
        session.availability._prepare_update_restriction_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_restriction_test",
            new_local_id=None,
            new_reason=None,
            new_category=None,
            new_restriction_recurrence=None,
        )

    # Test that no exception is raised when at least one parameter is provided
    try:
        # With only new_local_id
        session.availability._prepare_update_restriction_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_restriction_test",
            new_local_id="new_id",
            new_reason=None,
            new_category=None,
            new_restriction_recurrence=None,
        )

        # With only new_reason
        session.availability._prepare_update_restriction_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_restriction_test",
            new_local_id=None,
            new_reason="new reason",
            new_category=None,
            new_restriction_recurrence=None,
        )

        # With only new_category
        session.availability._prepare_update_restriction_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_restriction_test",
            new_local_id=None,
            new_reason=None,
            new_category="new category",
            new_restriction_recurrence=None,
        )

        # With only new_restriction_recurrence
        basic_recurrence = RestrictionBasicRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="New restriction",
                recurrence_type=RecurrenceType.NONE,
            ),
            period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
            period_end=datetime(2023, 2, 10, tzinfo=dateutil.tz.UTC),
            value=1.0,
        )
        session.availability._prepare_update_restriction_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_restriction_test",
            new_local_id=None,
            new_reason=None,
            new_category=None,
            new_restriction_recurrence=basic_recurrence,
        )

        # With multiple parameters
        session.availability._prepare_update_restriction_request(
            target=THERMAL_COMPONENT_PATH,
            event_id="update_restriction_test",
            new_local_id="new_id",
            new_reason="new reason",
            new_category="new category",
            new_restriction_recurrence=None,
        )
    except ValueError:
        pytest.fail("ValueError was raised unexpectedly!")


@pytest.mark.asyncio
@pytest.mark.database
async def test_revision_async(async_session):
    # 1. Create a revision
    revision = await async_session.availability.create_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_event_id",
        local_id="async_local_id",
        reason="Async revision reason",
    )

    # Verify creation succeeded
    assert revision.event_id == "async_event_id"
    assert revision.local_id == "async_local_id"
    assert revision.reason == "Async revision reason"
    assert revision.owner_id is not None
    assert revision.created.author is not None
    assert isinstance(revision.created.timestamp, datetime)
    assert revision.last_changed.author is not None
    assert isinstance(revision.last_changed.timestamp, datetime)
    assert len(revision.recurrences) == 0

    # 2. Add a recurrence to the revision
    recurrence_id = await async_session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC),
        recurrence=Recurrence(
            status="Planned",
            description="Async Test Recurrence",
            recurrence_type=RecurrenceType.NONE,
        ),
    )
    assert recurrence_id == 0

    # 3. Get the revision and verify recurrence was added
    revision_with_recurrence = await async_session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_event_id",
    )
    assert len(revision_with_recurrence.recurrences) == 1
    assert revision_with_recurrence.recurrences[0].recurrence.status == "Planned"
    assert (
        revision_with_recurrence.recurrences[0].recurrence.description
        == "Async Test Recurrence"
    )

    # 4. Add another recurrence with a different pattern
    second_recurrence_id = await async_session.availability.add_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 2, tzinfo=dateutil.tz.UTC),
        recurrence=Recurrence(
            status="Planned",
            description="Second Async Recurrence",
            recurrence_type=RecurrenceType.DAILY,
            recur_every=2,
            recur_until=datetime(2023, 2, 15, tzinfo=dateutil.tz.UTC),
        ),
    )
    assert second_recurrence_id == 1

    # 5. Search for the revision using search_availability_events
    search_results = await async_session.availability.search_availability_events(
        event_type=EventType.REVISION,
        targets=[THERMAL_COMPONENT_PATH],
    )
    found = False
    for result in search_results:
        if result.event_id == "async_event_id":
            found = True
            assert result.local_id == "async_local_id"
            break
    assert found, "Created revision not found in search results"

    # 6. Search for instances of the revision
    instances = await async_session.availability.search_instances(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_event_id",
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 15, tzinfo=dateutil.tz.UTC),
    )
    # Should have instances for days with recurrences
    assert len(instances) > 0

    # 7. Update the revision
    await async_session.availability.update_revision(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_event_id",
        new_local_id="updated_async_local_id",
        new_reason="Updated async reason",
    )

    # Verify update worked
    updated_revision = await async_session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_event_id",
    )
    assert updated_revision.local_id == "updated_async_local_id"
    assert updated_revision.reason == "Updated async reason"
    assert updated_revision.created.timestamp == revision.created.timestamp
    assert updated_revision.last_changed.timestamp >= revision.last_changed.timestamp

    # 8. Delete a specific recurrence
    await async_session.availability.delete_revision_recurrence(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_event_id",
        recurrence_id=second_recurrence_id,
    )

    # Verify recurrence was deleted
    revision_after_delete = await async_session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_event_id",
    )
    assert len(revision_after_delete.recurrences) == 1
    assert revision_after_delete.recurrences[0].id == recurrence_id

    # 9. Finally, delete the revision using delete_availability_events_by_id
    await async_session.availability.delete_availability_events_by_id(
        target=THERMAL_COMPONENT_PATH,
        event_ids=["async_event_id"],
    )

    # Verify deletion by searching for events
    search_results_after_delete = (
        await async_session.availability.search_availability_events(
            event_type=EventType.REVISION,
            targets=[THERMAL_COMPONENT_PATH],
        )
    )
    found_after_delete = False
    for result in search_results_after_delete:
        if result.event_id == "async_event_id":
            found_after_delete = True
            break
    assert not found_after_delete, "Revision should have been deleted"


@pytest.mark.asyncio
@pytest.mark.database
async def test_restriction_async(async_session):
    """Test the async version of restriction-related functionality."""
    # 1. Create a restriction with basic recurrence
    restriction = await async_session.availability.create_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_restriction_event",
        local_id="async_restriction_local_id",
        reason="Async restriction reason",
        category="DischargeMin[m3/s]",
        recurrence=RestrictionBasicRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="Async basic restriction",
                recurrence_type=RecurrenceType.NONE,
            ),
            period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
            period_end=datetime(2023, 1, 10, tzinfo=dateutil.tz.UTC),
            value=0.75,
        ),
    )

    # Verify creation succeeded
    assert restriction.event_id == "async_restriction_event"
    assert restriction.local_id == "async_restriction_local_id"
    assert restriction.reason == "Async restriction reason"
    assert restriction.category == "DischargeMin[m3/s]"
    assert restriction.owner_id is not None
    assert restriction.created.author is not None
    assert isinstance(restriction.created.timestamp, datetime)
    assert restriction.last_changed.author is not None
    assert isinstance(restriction.last_changed.timestamp, datetime)

    # Verify recurrence details
    assert isinstance(restriction.recurrence, RestrictionBasicRecurrence)
    assert restriction.recurrence.recurrence.status == "SelfImposed"
    assert restriction.recurrence.recurrence.description == "Async basic restriction"
    assert restriction.recurrence.period_start == datetime(
        2023, 1, 1, tzinfo=dateutil.tz.UTC
    )
    assert restriction.recurrence.period_end == datetime(
        2023, 1, 10, tzinfo=dateutil.tz.UTC
    )

    # 2. Search for the restriction in all restrictions
    search_results = await async_session.availability.search_availability_events(
        event_type=EventType.RESTRICTION,
        targets=[THERMAL_COMPONENT_PATH],
    )

    found = False
    for result in search_results:
        if result.event_id == "async_restriction_event":
            found = True
            assert result.local_id == "async_restriction_local_id"
            assert result.category == "DischargeMin[m3/s]"
            break

    assert found, "Created restriction not found in search results"

    # 3. Get the restriction directly
    retrieved_restriction = await async_session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_restriction_event",
    )

    assert retrieved_restriction.event_id == "async_restriction_event"
    assert retrieved_restriction.local_id == "async_restriction_local_id"
    assert retrieved_restriction.reason == "Async restriction reason"
    assert retrieved_restriction.category == "DischargeMin[m3/s]"

    # 4. Search for instances within a time interval
    instances = await async_session.availability.search_instances(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_restriction_event",
        period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 1, 15, tzinfo=dateutil.tz.UTC),
    )

    # Should have at least one instance
    assert len(instances) > 0

    # Verify instance properties
    instance = instances[0]
    assert instance.period_start <= datetime(2023, 1, 10, tzinfo=dateutil.tz.UTC)
    assert instance.period_end >= datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC)
    assert instance.value == 0.75

    # 5. Update the restriction with new values
    await async_session.availability.update_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_restriction_event",
        new_local_id="updated_async_local_id",
        new_reason="Updated async reason",
        new_category="DischargeMax[m3/s]",
    )

    # Verify the update worked
    updated_restriction = await async_session.availability.get_availability_event(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_restriction_event",
    )

    assert updated_restriction.local_id == "updated_async_local_id"
    assert updated_restriction.reason == "Updated async reason"
    assert updated_restriction.category == "DischargeMax[m3/s]"
    assert updated_restriction.created.timestamp == restriction.created.timestamp
    assert (
        updated_restriction.last_changed.timestamp >= restriction.last_changed.timestamp
    )

    # 6. Update the recurrence of the restriction
    new_recurrence = RestrictionBasicRecurrence(
        recurrence=Recurrence(
            status="SelfImposed",
            description="Updated async recurrence",
            recurrence_type=RecurrenceType.WEEKLY,
            recur_every=1,
            recur_until=datetime(2023, 3, 1, tzinfo=dateutil.tz.UTC),
        ),
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 3, tzinfo=dateutil.tz.UTC),
        value=1.25,
    )

    await async_session.availability.update_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_restriction_event",
        new_restriction_recurrence=new_recurrence,
    )

    # Verify recurrence was updated
    restriction_after_recurrence_update = (
        await async_session.availability.get_availability_event(
            target=THERMAL_COMPONENT_PATH,
            event_id="async_restriction_event",
        )
    )

    assert isinstance(
        restriction_after_recurrence_update.recurrence, RestrictionBasicRecurrence
    )
    assert (
        restriction_after_recurrence_update.recurrence.recurrence.status
        == "SelfImposed"
    )
    assert (
        restriction_after_recurrence_update.recurrence.recurrence.description
        == "Updated async recurrence"
    )
    assert (
        restriction_after_recurrence_update.recurrence.recurrence.recurrence_type
        == RecurrenceType.WEEKLY
    )
    assert restriction_after_recurrence_update.recurrence.recurrence.recur_every == 1
    assert restriction_after_recurrence_update.recurrence.period_start == datetime(
        2023, 2, 1, tzinfo=dateutil.tz.UTC
    )
    assert restriction_after_recurrence_update.recurrence.period_end == datetime(
        2023, 2, 3, tzinfo=dateutil.tz.UTC
    )

    # 7. Create a complex restriction
    complex_restriction = await async_session.availability.create_restriction(
        target=THERMAL_COMPONENT_PATH,
        event_id="async_complex_restriction",
        local_id="async_complex_local_id",
        reason="Async complex restriction",
        category="DischargeMin[m3/s]",
        recurrence=RestrictionComplexRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="Async complex pattern",
                recurrence_type=RecurrenceType.DAILY,
                recur_every=1,
                recur_until=datetime(2023, 2, 15, tzinfo=dateutil.tz.UTC),
            ),
            time_points=[
                TimePoint(
                    value=50.0,
                    timestamp=datetime(2023, 2, 1, 8, 0, tzinfo=dateutil.tz.UTC),
                ),
                TimePoint(
                    value=75.0,
                    timestamp=datetime(2023, 2, 1, 12, 0, tzinfo=dateutil.tz.UTC),
                ),
                TimePoint(
                    value=60.0,
                    timestamp=datetime(2023, 2, 1, 16, 0, tzinfo=dateutil.tz.UTC),
                ),
            ],
        ),
    )

    # Verify complex restriction creation
    assert complex_restriction.event_id == "async_complex_restriction"
    assert isinstance(complex_restriction.recurrence, RestrictionComplexRecurrence)
    assert len(complex_restriction.recurrence.time_points) == 3

    # 8. Finally, delete both restrictions
    await async_session.availability.delete_availability_events(
        target=THERMAL_COMPONENT_PATH,
        event_type=EventType.ALL,
    )

    # Verify deletion by searching for events
    search_results_after_delete = (
        await async_session.availability.search_availability_events(
            event_type=EventType.RESTRICTION,
            targets=[THERMAL_COMPONENT_PATH],
        )
    )

    for result in search_results_after_delete:
        assert (
            result.event_id != "async_restriction_event"
        ), "Basic restriction should have been deleted"
        assert (
            result.event_id != "async_complex_restriction"
        ), "Complex restriction should have been deleted"


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
