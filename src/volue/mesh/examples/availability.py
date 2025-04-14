from datetime import datetime

import dateutil
import helpers

from volue.mesh import Connection
from volue.mesh.availability import EventType, Recurrence, RecurrenceType, Revision

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
        reason="Async revision reason",
    )

    print(f"   Created revision with ID: {revision.event_id}")
    print(f"   Owner ID: {revision.owner_id}")
    print(f"   Created by: {revision.created.author} at {revision.created.timestamp}")
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
            description="Async Test Recurrence",
            recurrence_type=RecurrenceType.NONE,
        ),
    )
    print(f"   Added recurrence with ID: {recurrence_id}")

    # 3. Get the revision
    print("\n3. Getting the revision with its new recurrence...")
    revision_with_recurrence = session.availability.get_availability_event(
        target=CHIMNEY_PATH,
        event_id="event_id",
    )
    print(f"   Retrieved revision with ID: {revision_with_recurrence.event_id}")
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
            description="Second Async Recurrence",
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
        new_reason="Updated async reason",
    )

    updated_revision = session.availability.get_availability_event(
        target=CHIMNEY_PATH, event_id="event_id"
    )
    print(f"   Updated local ID: {updated_revision.local_id}")
    print(f"   Updated reason: {updated_revision.reason}")
    print(f"   Last modified: {updated_revision.last_changed.timestamp}")

    # 8. Delete a specific recurrence
    print("\n8. Deleting the second recurrence pattern...")
    session.availability.delete_revision_recurrence(
        target=CHIMNEY_PATH,
        event_id="event_id",
        recurrence_id=second_recurrence_id,
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

    found_revisions = session.availability.search_availability_events(
        event_type=EventType.REVISION,
        targets=[CHIMNEY_PATH],
    )
    print(f"   Revisions found: {len(found_revisions)}")

    print("\n=== Revision Workflow Example Completed ===\n")


def main(address, tls_root_pem_cert):
    """Showing how to create a revision."""

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    with connection.create_session() as session:
        revision_workflow(session)


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
