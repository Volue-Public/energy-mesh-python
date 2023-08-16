"""
Tests for volue.mesh.RatingCurveSegment and volue.mesh.RatingCurveVersion.
"""

import operator
import sys
from datetime import datetime, timedelta

import grpc
import pytest
from dateutil import tz

from volue import mesh
from volue.mesh import _base_session

ATTRIBUTE_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.RatingCurveAtt"


def generate_rating_curve_version(seed: int, valid_from_time: datetime):
    x = 0.0
    segments = []

    for i in range(seed):
        segments.append(
            mesh.RatingCurveSegment(
                x_range_until=2 * x + seed + 1,
                factor_a=x + seed + i,
                factor_b=x - seed + i,
                factor_c=-x - seed + i,
            )
        )
        x += 0.5

    return mesh.RatingCurveVersion(
        x_range_from=x,
        valid_from_time=valid_from_time.replace(tzinfo=tz.UTC),
        x_value_segments=segments,
    )


def verify_version_1(version: mesh.RatingCurveVersion):
    """Verify existing rating curve version from the the SimpleThermalModel"""
    assert version.valid_from_time == datetime(2000, 1, 1, tzinfo=tz.UTC)
    assert version.x_range_from == 2.0
    for i, segment in enumerate(version.x_value_segments):
        assert segment.x_range_until == (i + 1) * 10
        assert segment.factor_a == i * 3 + 1
        assert segment.factor_b == i * 3 + 2
        assert segment.factor_c == i * 3 + 3


def verify_version_2(version: mesh.RatingCurveVersion):
    """Verify existing rating curve version from the the SimpleThermalModel"""
    assert version.valid_from_time == datetime(2010, 1, 1, tzinfo=tz.UTC)
    assert version.x_range_from == 4.0
    for i, segment in enumerate(version.x_value_segments):
        assert segment.x_range_until == (i + 1) * 10 + 10
        assert segment.factor_a == -(i * 3 + 1)
        assert segment.factor_b == -(i * 3 + 2)
        assert segment.factor_c == -(i * 3 + 3)


def get_new_rating_curve_version(
    x_range_from=2.0,
    valid_from_time=datetime.now(tz.UTC) + timedelta(days=2),
    x_value_segments=None,
) -> mesh.RatingCurveVersion:
    """Helper function update rating curve tests."""
    if x_value_segments is None:
        x_value_segments = [mesh.RatingCurveSegment(5.0, 1.0, 1.0, 1.0)]
    return mesh.RatingCurveVersion(x_range_from, valid_from_time, x_value_segments)


def get_targets(session):
    """
    Return all possible targets for attribute APIs, like: ID or path.
    ID is always the first element in the returned target list.
    """
    # ID is auto-generated when creating an attribute, so
    # first we need to read it.
    attribute = session.get_attribute(ATTRIBUTE_PATH)
    return [attribute.id, ATTRIBUTE_PATH, attribute]


@pytest.mark.database
@pytest.mark.parametrize(
    "start_time", [datetime.min, datetime(2000, 1, 1), datetime(2009, 12, 31)]
)
@pytest.mark.parametrize(
    "end_time", [datetime.max, datetime(2020, 1, 1), datetime(2010, 1, 2)]
)
def test_get_all_rating_curve_versions(
    session: _base_session.Session, start_time: datetime, end_time: datetime
):
    versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=start_time, end_time=end_time
    )

    assert len(versions) == 2
    verify_version_1(versions[0])
    verify_version_2(versions[1])


@pytest.mark.database
@pytest.mark.parametrize("start_time", [datetime(2000, 1, 1), datetime(2005, 1, 1)])
@pytest.mark.parametrize("end_time", [datetime(2006, 1, 1), datetime(2010, 1, 1)])
def test_get_one_rating_curve_version_with_limited_interval(
    session: _base_session.Session, start_time: datetime, end_time: datetime
):
    versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=start_time, end_time=end_time
    )

    assert len(versions) == 1
    verify_version_1(versions[0])


@pytest.mark.database
def test_get_rating_curve_versions_with_versions_only(session: _base_session.Session):
    versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime.min,
        end_time=datetime.max,
        versions_only=True,
    )

    assert len(versions) == 2
    assert versions[0].valid_from_time == datetime(2000, 1, 1, tzinfo=tz.UTC)
    assert versions[1].valid_from_time == datetime(2010, 1, 1, tzinfo=tz.UTC)

    # check that only `valid_from_time` is set
    for version in versions:
        assert len(version.x_value_segments) == 0
        assert version.x_range_from == 0.0


@pytest.mark.database
def test_get_rating_curve_versions_invalid_input(session: _base_session.Session):
    # [start_time, end_time) must be a valid interval
    with pytest.raises(
        grpc.RpcError, match="UtcInterval .* is invalid, start_time > end_time"
    ):
        session.get_rating_curve_versions(
            target=ATTRIBUTE_PATH,
            start_time=datetime(2020, 1, 1),
            end_time=datetime(2000, 1, 1),
        )


@pytest.mark.database
def test_update_rating_curve_versions_remove_one_version(
    session: _base_session.Session,
):
    # provide all possible attribute target types, like path or ID
    targets = get_targets(session)

    for target in targets:
        session.update_rating_curve_versions(
            target=target,
            start_time=datetime(2006, 1, 1),
            end_time=datetime(2022, 1, 1),
            new_versions=[],
        )

        versions = session.get_rating_curve_versions(
            target=target, start_time=datetime.min, end_time=datetime.max
        )

        assert len(versions) == 1
        verify_version_1(versions[0])

        session.rollback()


@pytest.mark.database
def test_update_rating_curve_versions_remove_all_versions(
    session: _base_session.Session,
):
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime.min,
        end_time=datetime.max,
        new_versions=[],
    )

    versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(versions) == 0


@pytest.mark.database
@pytest.mark.parametrize("start_time", [datetime.min, datetime(1990, 1, 1)])
@pytest.mark.parametrize("end_time", [datetime(1999, 12, 31), datetime(2000, 1, 1)])
def test_update_rating_curve_versions_remove_versions_before_current_versions(
    session: _base_session.Session, start_time: datetime, end_time: datetime
):
    """
    Originally there are 2 versions from: 2000, from: 2010.
    Send empty update requests with intervals before current
    versions, i.e. < 2000
    """
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=start_time, end_time=end_time, new_versions=[]
    )

    versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(versions) == 2
    verify_version_1(versions[0])
    verify_version_2(versions[1])


@pytest.mark.database
@pytest.mark.parametrize("start_time", [datetime(1999, 12, 31), datetime(2000, 1, 1)])
@pytest.mark.parametrize("end_time", [datetime(2010, 1, 2), datetime(2011, 1, 1)])
def test_update_rating_curve_versions_replace_two_old_versions_with_one_longer(
    session: _base_session.Session, start_time: datetime, end_time: datetime
):
    """
    Originally there are 2 versions from: 2000, from: 2010.
    Send update requests with single version, with intervals
    outside or equal to current versions, i.e. <= 2000 && > 2010
    """
    new_versions = [generate_rating_curve_version(3, datetime(2010, 1, 1))]
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=start_time,
        end_time=end_time,
        new_versions=new_versions,
    )

    updated_versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(updated_versions) == 1
    assert updated_versions == new_versions


@pytest.mark.database
def test_update_rating_curve_versions_with_new_versions_in_the_middle(
    session: _base_session.Session,
):
    new_versions = [
        generate_rating_curve_version(1, datetime(2005, 1, 1)),
        generate_rating_curve_version(5, datetime(2008, 1, 1)),
    ]
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime(2005, 1, 1),
        end_time=datetime(2010, 1, 1),
        new_versions=new_versions,
    )

    updated_versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(updated_versions) == 4
    verify_version_1(updated_versions[0])
    assert updated_versions[1:3] == new_versions
    verify_version_2(updated_versions[3])


@pytest.mark.database
def test_update_rating_curve_versions_with_new_versions_before(
    session: _base_session.Session,
):
    new_versions = [generate_rating_curve_version(2, datetime(1995, 1, 1))]
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime(1990, 1, 1),
        end_time=datetime(2000, 1, 1),
        new_versions=new_versions,
    )

    updated_versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(updated_versions) == 3
    # use [0:1] instead of [0] to get a list
    assert updated_versions[0:1] == new_versions
    verify_version_1(updated_versions[1])
    verify_version_2(updated_versions[2])


@pytest.mark.database
def test_update_rating_curve_versions_with_new_versions_after(
    session: _base_session.Session,
):
    new_versions = [generate_rating_curve_version(8, datetime(2022, 1, 1))]
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime(2012, 1, 1),
        end_time=datetime(2025, 1, 1),
        new_versions=new_versions,
    )

    updated_versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(updated_versions) == 3
    verify_version_1(updated_versions[0])
    verify_version_2(updated_versions[1])
    # use [0:1] instead of [0] to get a list
    assert updated_versions[2:3] == new_versions


@pytest.mark.database
def test_update_rating_curve_versions_replace_all_existing_versions_with_new_ones(
    session: _base_session.Session,
):
    new_versions = [
        generate_rating_curve_version(3, datetime(1995, 1, 1)),
        generate_rating_curve_version(1, datetime(2012, 1, 1)),
        generate_rating_curve_version(5, datetime(2022, 1, 1)),
    ]
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime(1990, 1, 1),
        end_time=datetime(2025, 1, 1),
        new_versions=new_versions,
    )

    updated_versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(updated_versions) == 3
    assert updated_versions == new_versions


@pytest.mark.database
def test_update_rating_curve_versions_remove_last_version(
    session: _base_session.Session,
):
    # if interval contains `from` of last version the last version should be removed
    # i.e. the end interval does not need to be UtcDateTime::Max
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime(2005, 1, 1),
        end_time=datetime(2015, 1, 1),
        new_versions=[],
    )

    updated_versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(updated_versions) == 1
    verify_version_1(updated_versions[0])


@pytest.mark.database
def test_update_rating_curve_versions_unsorted_versions(session: _base_session.Session):
    new_versions = [
        generate_rating_curve_version(3, datetime(1999, 1, 1)),
        generate_rating_curve_version(2, datetime(1992, 1, 1)),
        generate_rating_curve_version(4, datetime(1997, 1, 1)),
    ]

    # Starting with Mesh 2.10 the new rating curve versions must be sorted.
    with pytest.raises(grpc.RpcError, match="new rating curve versions are not sorted"):
        session.update_rating_curve_versions(
            target=ATTRIBUTE_PATH,
            start_time=datetime(1990, 1, 1),
            end_time=datetime(1999, 12, 1),
            new_versions=new_versions,
        )


@pytest.mark.database
def test_update_rating_curve_versions_unsorted_segments(session: _base_session.Session):
    new_segments = [
        mesh.RatingCurveSegment(5.0, 1.0, 1.0, 1.0),
        mesh.RatingCurveSegment(3.0, 1.0, 1.0, 1.0),
        mesh.RatingCurveSegment(6.0, 1.0, 1.0, 1.0),
    ]
    new_versions = [
        mesh.RatingCurveVersion(2.0, datetime(2022, 5, 10, tzinfo=tz.UTC), new_segments)
    ]
    session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime(2022, 1, 1),
        end_time=datetime(2022, 12, 1),
        new_versions=new_versions,
    )

    updated_versions = session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    new_versions[0].x_value_segments = sorted(
        new_segments, key=operator.attrgetter("x_range_until")
    )

    assert len(updated_versions) == 3
    verify_version_1(updated_versions[0])
    verify_version_2(updated_versions[1])
    # use [2:3] instead of [2] to get a list
    assert updated_versions[2:3] == new_versions


@pytest.mark.database
def test_update_rating_curve_versions_invalid_input(session: _base_session.Session):
    now = datetime.now(tz.UTC)
    later = now + timedelta(days=365)

    # [start_time, end_time) must be a valid interval
    with pytest.raises(
        grpc.RpcError, match="UtcInterval .* is invalid, start_time > end_time"
    ):
        session.update_rating_curve_versions(
            target=ATTRIBUTE_PATH,
            start_time=later,
            end_time=now,
            new_versions=[get_new_rating_curve_version()],
        )

    kwargs = {"target": ATTRIBUTE_PATH, "start_time": now, "end_time": later}

    # One rating curve version can't have segments with duplicate `x_range_until` values

    with pytest.raises(
        grpc.RpcError,
        match="duplicate .* thresholds in segments of a new rating curve version",
    ):
        new_version = get_new_rating_curve_version(
            x_value_segments=[
                mesh.RatingCurveSegment(5.0, 1.0, 1.0, 1.0),
                mesh.RatingCurveSegment(5.0, 1.0, 1.0, 1.0),
            ]
        )
        session.update_rating_curve_versions(new_versions=[new_version], **kwargs)

    with pytest.raises(
        grpc.RpcError,
        match="duplicate .* thresholds in segments of a new rating curve version",
    ):
        new_version = get_new_rating_curve_version(
            x_value_segments=[
                mesh.RatingCurveSegment(5.0, 1.0, 1.0, 1.0),
                mesh.RatingCurveSegment(10.0, 1.0, 1.0, 1.0),
                mesh.RatingCurveSegment(5.0, 1.0, 1.0, 1.0),
            ]
        )
        session.update_rating_curve_versions(new_versions=[new_version], **kwargs)

    # Each rating curve version `x_range_from` threshold must be lesser than any segment's `x_range_until` threshold

    with pytest.raises(
        grpc.RpcError, match="rating curve version .* is not lesser than"
    ):
        new_version = get_new_rating_curve_version(x_range_from=1000.0)
        session.update_rating_curve_versions(new_versions=[new_version], **kwargs)

    with pytest.raises(
        grpc.RpcError, match="rating curve version .* is not lesser than"
    ):
        new_version = get_new_rating_curve_version(x_range_from=3.0)
        new_version.x_value_segments = [
            mesh.RatingCurveSegment(20.0, 1.0, 1.0, 1.0),
            mesh.RatingCurveSegment(1.0, 1.0, 1.0, 1.0),
            mesh.RatingCurveSegment(5.0, 1.0, 1.0, 1.0),
        ]
        session.update_rating_curve_versions(new_versions=[new_version], **kwargs)

    # Each new rating curve version must have at least one segment
    with pytest.raises(
        grpc.RpcError,
        match="each new rating curve version must have at least one segment",
    ):
        new_version = get_new_rating_curve_version(x_value_segments=[])
        session.update_rating_curve_versions(new_versions=[new_version], **kwargs)

    # New rating curve versions must be within interval
    even_later = later + timedelta(days=365)
    with pytest.raises(grpc.RpcError, match="within .* interval"):
        new_version = get_new_rating_curve_version(valid_from_time=even_later)
        session.update_rating_curve_versions(new_versions=[new_version], **kwargs)

    # Multiple rating curve versions can't have the same `valid_from_time` timestamp
    with pytest.raises(
        grpc.RpcError, match="duplicate .* timestamps in new rating curve versions"
    ):
        new_version = get_new_rating_curve_version()
        session.update_rating_curve_versions(
            new_versions=[new_version, new_version], **kwargs
        )


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_rating_curve_versions_async(async_session):
    """For async run the simplest test, implementation is the same."""
    new_versions = [
        generate_rating_curve_version(3, datetime(1992, 1, 1)),
        generate_rating_curve_version(3, datetime(2021, 1, 1)),
    ]
    await async_session.update_rating_curve_versions(
        target=ATTRIBUTE_PATH,
        start_time=datetime(1990, 1, 1),
        end_time=datetime(2025, 1, 1),
        new_versions=new_versions,
    )

    updated_versions = await async_session.get_rating_curve_versions(
        target=ATTRIBUTE_PATH, start_time=datetime.min, end_time=datetime.max
    )

    assert len(updated_versions) == 2
    assert updated_versions == new_versions


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
