from datetime import datetime

import dateutil
import helpers

from volue.mesh import Connection
from volue.mesh.availability import (
    EventType,
    Recurrence,
    RecurrenceType,
    RestrictionBasicRecurrence,
    RestrictionComplexRecurrence,
    Revision,
    TimePoint,
)

CHIMNEY_PATH = "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1/SomePowerPlantChimney2"


def revision_workflow(session: Connection.Session):
    """
    Demonstrates a complete workflow for creating, managing, and deleting revisions in Mesh.
    """
    print("\n=== Starting Revision Workflow Example ===\n")
    # 1. Create a revision
    print("1. Creating a new revision...")
    revision = session.availability.create_revision(
        target=CHIMNEY_PATH,
        event_id="event_id",
        local_id="local_id",
        reason="Revision reason",
        created_author="created_author",
        created_timestamp=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        last_changed_author="last_changed_author",
    )

    print(f"   Created revision with ID: {revision.event_id}")
    print(f"   Owner ID: {revision.owner_id}")
    print(f"   Created by: '{revision.created.author}' at {revision.created.timestamp}")
    print(
        f"   Last changed by: '{revision.last_changed.author}' at {revision.last_changed.timestamp}"
    )
    print(f"   Initial recurrences count: {len(revision.recurrences)}")

    # 2. Add a recurrence to the revision
    print("\n2. Adding a basic recurrence...")
    recurrence_id = session.availability.add_revision_recurrence(
        target=CHIMNEY_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC),
        recurrence=Recurrence(
            status="Planned",
            description="Recurrence",
            recurrence_type=RecurrenceType.NONE,
        ),
    )
    print(f"   Added recurrence with ID: {recurrence_id}")

    # 3. Get the revision
    print("\n3. Getting the revision with its new recurrence...")
    revision_with_recurrence = session.availability.get_availability_event(
        target=CHIMNEY_PATH,
        event_id=revision.event_id,
    )
    print(f"   Retrieved revision with ID: {revision_with_recurrence.event_id}")
    print(
        f"   Created by: {revision_with_recurrence.created.author} at {revision_with_recurrence.created.timestamp}"
    )
    print(
        f"   Last changed by: {revision_with_recurrence.last_changed.author} at {revision_with_recurrence.last_changed.timestamp}"
    )
    print(f"   Recurrences count: {len(revision_with_recurrence.recurrences)}")
    if revision_with_recurrence.recurrences:
        recurrence = revision_with_recurrence.recurrences[0]
        print(f"   Recurrence status: {recurrence.recurrence.status}")
        print(f"   Recurrence description: {recurrence.recurrence.description}")
        print(
            f"   Recurrence period: {recurrence.period_start} to {recurrence.period_end}"
        )

    # 4. Add another recurrence with a different pattern
    print("\n4. Adding a daily repeating recurrence...")
    second_recurrence_id = session.availability.add_revision_recurrence(
        target=CHIMNEY_PATH,
        event_id=revision.event_id,
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 2, tzinfo=dateutil.tz.UTC),
        recurrence=Recurrence(
            status="Planned",
            description="Second Recurrence",
            recurrence_type=RecurrenceType.DAILY,
            recur_every=2,
            recur_until=datetime(2023, 2, 15, tzinfo=dateutil.tz.UTC),
        ),
    )
    print(f"   Added second recurrence with ID: {second_recurrence_id}")

    # 5. Search for the revision using search_availability_events
    print("\n5. Searching for revisions...")
    search_results = session.availability.search_availability_events(
        event_type=EventType.REVISION,
        targets=[CHIMNEY_PATH],
    )
    print(f"   Found {len(search_results)} revision events")
    for i, result in enumerate(search_results):
        if isinstance(result, Revision):
            print(
                f"   Result {i+1}: Event ID: {result.event_id}, Reason: {result.reason}"
            )

    # 6. Search for instances of the revision
    print("\n6. Searching for specific instances of the revision...")
    instances = session.availability.search_instances(
        target=CHIMNEY_PATH,
        event_id="event_id",
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 15, tzinfo=dateutil.tz.UTC),
    )
    print(f"   Found {len(instances)} instances")
    # These are the actual occurrences based on the recurrence pattern
    for i, instance in enumerate(instances):
        print(
            f"   Instance {i+1}: Period: {instance.period_start} to {instance.period_end}"
        )

    # 7. Update the revision
    print("\n7. Updating the revision...")
    session.availability.update_revision(
        target=CHIMNEY_PATH,
        event_id="event_id",
        new_local_id="updated_local_id",
        new_reason="Updated reason",
        author="update_revision_author",
    )

    updated_revision = session.availability.get_availability_event(
        target=CHIMNEY_PATH, event_id="event_id"
    )
    print(f"   Updated local ID: {updated_revision.local_id}")
    print(f"   Updated reason: {updated_revision.reason}")
    print(
        f"   Created by: '{updated_revision.created.author}' at {updated_revision.created.timestamp}"
    )
    print(
        f"   Last changed by: '{updated_revision.last_changed.author}' at {updated_revision.last_changed.timestamp}"
    )

    # 8. Delete a specific recurrence
    print("\n8. Deleting the second recurrence pattern...")
    session.availability.delete_revision_recurrence(
        target=CHIMNEY_PATH,
        event_id="event_id",
        recurrence_id=second_recurrence_id,
        author="delete_revision_recurrence_author",
    )

    revision_after_delete = session.availability.get_availability_event(
        target=CHIMNEY_PATH, event_id="event_id"
    )
    print(f"   Recurrences remaining: {len(revision_after_delete.recurrences)}")

    # 9. Finally, delete the revision using delete_availability_events_by_id
    print("\n9. Deleting the entire revision...")
    session.availability.delete_availability_events_by_id(
        target=CHIMNEY_PATH,
        event_ids=["event_id"],
    )

    remaining_revisions = session.availability.search_availability_events(
        event_type=EventType.REVISION,
        targets=[CHIMNEY_PATH],
    )
    print(f"   Revisions found: {len(remaining_revisions)}")

    print("\n=== Revision Workflow Example Completed ===\n")


def restriction_workflow(session: Connection.Session):
    """
    Demonstrates a complete workflow for creating, managing, and deleting restrictions in Mesh.
    """
    print("\n=== Starting Restriction Workflow Example ===\n")

    # 1. Create a basic restriction with constant value
    print("1. Creating a basic restriction...")
    basic_restriction = session.availability.create_restriction(
        target=CHIMNEY_PATH,
        event_id="basic_restriction_id",
        local_id="basic_local_id",
        reason="basic restriction",
        category="DischargeMin[m3/s]",
        recurrence=RestrictionBasicRecurrence(
            recurrence=Recurrence(
                status="SelfImposed",
                description="Basic restriction",
                recurrence_type=RecurrenceType.WEEKLY,
                recur_every=1,
                recur_until=datetime(2023, 1, 31, tzinfo=dateutil.tz.UTC),
            ),
            period_start=datetime(2023, 1, 2, tzinfo=dateutil.tz.UTC),  # Monday
            period_end=datetime(2023, 1, 3, tzinfo=dateutil.tz.UTC),  # Tuesday
            value=75.5,  # 75.5% capacity
        ),
        created_author="created_author",
        created_timestamp=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        last_changed_author="last_changed_author",
    )

    print(f"   Created basic restriction with ID: {basic_restriction.event_id}")
    print(f"   Owner ID: {basic_restriction.owner_id}")
    print(f"   Category: {basic_restriction.category}")
    print(f"   Value: {basic_restriction.recurrence.value}")
    print(
        f"   Created by: {basic_restriction.created.author} at {basic_restriction.created.timestamp}"
    )
    print(
        f"   Last changed by: {basic_restriction.last_changed.author} at {basic_restriction.last_changed.timestamp}"
    )
    print(f"   Status: {basic_restriction.recurrence.recurrence.status}")

    # 2. Create a complex restriction with multiple time points
    print("\n2. Creating a complex restriction with multiple time points...")
    complex_restriction = session.availability.create_restriction(
        target=CHIMNEY_PATH,
        event_id="complex_restriction_id",
        local_id="complex_local_id",
        reason="Complex restriction",
        category="DischargeMax[m3/s]",
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
                TimePoint(
                    value=70.0,
                    timestamp=datetime(2023, 1, 1, 16, 0, tzinfo=dateutil.tz.UTC),
                ),
                TimePoint(
                    value=90.0,
                    timestamp=datetime(2023, 1, 1, 20, 0, tzinfo=dateutil.tz.UTC),
                ),
            ],
        ),
        created_author="created_author",
        created_timestamp=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        last_changed_author="last_changed_author",
    )

    print(f"   Created complex restriction with ID: {complex_restriction.event_id}")
    print(f"   Category: {complex_restriction.category}")
    print(
        f"   Number of time points: {len(complex_restriction.recurrence.time_points)}"
    )
    print(
        f"   Recurrence type: {complex_restriction.recurrence.recurrence.recurrence_type.name}"
    )
    print(f"   Repeats until: {complex_restriction.recurrence.recurrence.recur_until}")
    print(
        f"   Created by: {complex_restriction.created.author} at {complex_restriction.created.timestamp}"
    )
    print(
        f"   Last changed by: {complex_restriction.last_changed.author} at {complex_restriction.last_changed.timestamp}"
    )

    # 3. Search for restrictions
    print("\n3. Searching for all restrictions...")
    restrictions = session.availability.search_availability_events(
        event_type=EventType.RESTRICTION,
        targets=[CHIMNEY_PATH],
    )
    print(f"   Found {len(restrictions)} restrictions")
    for i, restriction in enumerate(restrictions):
        print(
            f"   Restriction {i+1}: ID: {restriction.event_id}, Category: {restriction.category}"
        )

    # 4. Get a specific restriction by ID
    print("\n4. Getting specific restriction details...")
    retrieved_restriction = session.availability.get_availability_event(
        target=CHIMNEY_PATH,
        event_id="basic_restriction_id",
    )
    print(f"   Retrieved restriction with ID: {retrieved_restriction.event_id}")
    print(f"   Local ID: {retrieved_restriction.local_id}")
    print(f"   Reason: {retrieved_restriction.reason}")
    print(f"   Category: {retrieved_restriction.category}")

    # Check the type of recurrence and print the value accordingly
    # In this case we expect the recurrence to be of type RestrictionBasicRecurrence
    if isinstance(retrieved_restriction.recurrence, RestrictionBasicRecurrence):
        print(f"   Value: {retrieved_restriction.recurrence.value}")
    elif isinstance(retrieved_restriction.recurrence, RestrictionComplexRecurrence):
        # In case of complex recurrence we can print the time points
        for i, point in enumerate(retrieved_restriction.recurrence.values):
            print(
                f"   Time point {i+1}: Value: {point.value}, Timestamp: {point.timestamp}"
            )

    # 4.5 Get a specific restriction by ID
    print("\n4.5. Getting specific restriction details...")
    retrieved_restriction = session.availability.get_availability_event(
        target=CHIMNEY_PATH,
        event_id="complex_restriction_id",
    )
    print(f"   Retrieved restriction with ID: {retrieved_restriction.event_id}")
    print(f"   Local ID: {retrieved_restriction.local_id}")
    print(f"   Reason: {retrieved_restriction.reason}")
    print(f"   Category: {retrieved_restriction.category}")

    # Check the type of recurrence and print the value accordingly
    # In this case we expect the recurrence to be of type RestrictionComplexRecurrence
    if isinstance(retrieved_restriction.recurrence, RestrictionBasicRecurrence):
        print(f"   Value: {retrieved_restriction.recurrence.value}")
    elif isinstance(retrieved_restriction.recurrence, RestrictionComplexRecurrence):
        # In case of complex recurrence we can print the time points
        for i, point in enumerate(retrieved_restriction.recurrence.time_points):
            print(
                f"   Time point {i+1}: Value: {point.value}, Timestamp: {point.timestamp}"
            )

    # 5. Search for instances within a time period
    print("\n5. Searching for specific instances of the basic restriction...")
    instances = session.availability.search_instances(
        target=CHIMNEY_PATH,
        event_id="basic_restriction_id",
        period_start=datetime(2023, 1, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 1, 31, tzinfo=dateutil.tz.UTC),
    )
    print(f"   Found {len(instances)} instances")
    for i, instance in enumerate(instances):  # Just show first few instances
        print(
            f"   Instance {i+1}: Period: {instance.period_start} to {instance.period_end}, Value: {instance.value}"
        )

    # 6. Update restriction
    print("\n6. Updating the basic restriction...")
    session.availability.update_restriction(
        target=CHIMNEY_PATH,
        event_id="basic_restriction_id",
        new_local_id="updated_basic_id",
        new_reason="Updated basic restriction reason",
        new_category="DischargeMax[m3/s]",
        author="update_restriction_author",
    )

    # Verify the update
    updated_restriction = session.availability.get_availability_event(
        target=CHIMNEY_PATH,
        event_id="basic_restriction_id",
    )
    print(f"   Updated local ID: {updated_restriction.local_id}")
    print(f"   Updated reason: {updated_restriction.reason}")
    print(f"   Updated category: {updated_restriction.category}")
    print(
        f"   Last changed by: {updated_restriction.last_changed.author} at {updated_restriction.last_changed.timestamp}"
    )

    # 7. Update restriction recurrence
    print("\n7. Updating the restriction recurrence...")
    new_recurrence = RestrictionBasicRecurrence(
        recurrence=Recurrence(
            status="SelfImposed",
            description="Updated restriction recurrence",
            recurrence_type=RecurrenceType.NONE,
        ),
        period_start=datetime(2023, 2, 1, tzinfo=dateutil.tz.UTC),
        period_end=datetime(2023, 2, 10, tzinfo=dateutil.tz.UTC),
        value=50.0,
    )

    session.availability.update_restriction(
        target=CHIMNEY_PATH,
        event_id="basic_restriction_id",
        new_restriction_recurrence=new_recurrence,
        author="update_restriction_recurrence_author",
    )

    updated_restriction = session.availability.get_availability_event(
        target=CHIMNEY_PATH,
        event_id="basic_restriction_id",
    )
    print(
        f"   New recurrence period: {updated_restriction.recurrence.period_start} to {updated_restriction.recurrence.period_end}"
    )
    print(f"   New value: {updated_restriction.recurrence.value}")
    print(
        f"   New recurrence type: {updated_restriction.recurrence.recurrence.recurrence_type.name}"
    )
    print(
        f"   Last changed by: {updated_restriction.last_changed.author} at {updated_restriction.last_changed.timestamp}"
    )

    # 8. Delete restrictions
    print("\n8. Deleting restrictions...")
    session.availability.delete_availability_events_by_id(
        target=CHIMNEY_PATH,
        event_ids=["basic_restriction_id", "complex_restriction_id"],
    )

    # Verify deletion
    remaining_restrictions = session.availability.search_availability_events(
        event_type=EventType.RESTRICTION,
        targets=[CHIMNEY_PATH],
    )

    print(f"   Restrictions found: {len(remaining_restrictions)}")

    print("\n=== Restriction Workflow Example Completed ===\n")


def main(address, tls_root_pem_cert):
    """Showing how to create a revision."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    with connection.create_session() as session:
        revision_workflow(session)
        restriction_workflow(session)


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
