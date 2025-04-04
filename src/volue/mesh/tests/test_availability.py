import sys
from datetime import datetime

import pytest

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


@pytest.mark.database
def test_create_revision_with_invalid_target(connection):
    with connection.create_session() as session:
        with pytest.raises(Exception) as exc_info:
            session.availability.create_revision(
                target="Invalid/Path",
                id="event_id",
                local_id="local_id",
                reason="reason",
            )
        assert "object not found" in str(exc_info.value)


@pytest.mark.database
def test_create_revision_with_missing_fields(connection):
    with connection.create_session() as session:
        with pytest.raises(Exception) as exc_info:
            session.availability.create_revision(
                target=THERMAL_COMPONENT_PATH,
                id=None,  # Missing required field
                local_id="local_id",
                reason="reason",
            )
        assert "no event id provided" in str(exc_info.value)


@pytest.mark.database
def test_create_revision_with_duplicate_id(connection):
    with connection.create_session() as session:
        session.availability.create_revision(
            target=THERMAL_COMPONENT_PATH,
            id="duplicate_id",
            local_id="local_id_1",
            reason="reason_1",
        )
        with pytest.raises(Exception) as exc_info:
            session.availability.create_revision(
                target=THERMAL_COMPONENT_PATH,
                id="duplicate_id",  # Duplicate ID
                local_id="local_id_2",
                reason="reason_2",
            )
        assert "event with event id" in str(exc_info.value)


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


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
