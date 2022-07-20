"""
Tests for volue.mesh.Connection
"""

from datetime import datetime, timedelta, timezone
import math
import sys
from typing import List

from dateutil import tz
import grpc
import pyarrow as pa
import pytest

from volue.mesh import Timeseries, TimeseriesResource
from volue.mesh.calc import transform as Transform
from volue.mesh.calc.common import Timezone
from volue.mesh.tests.test_utilities.utilities import get_timeseries_2, get_physical_timeseries, \
    get_virtual_timeseries, get_timeseries_attribute_2, verify_timeseries_2


@pytest.mark.database
def test_read_timeseries_points(session):
    """Check that timeseries points can be read using timeseries key, UUID and full name"""
    timeseries, start_time, end_time, _, full_name = get_timeseries_2()
    try:
        test_case_1 = {"start_time": start_time, "end_time": end_time,
                       "target": timeseries.timeseries_key}
        test_case_2 = {"start_time": start_time, "end_time": end_time,
                       "target": timeseries.id}
        test_case_3 = {"start_time": start_time, "end_time": end_time,
                       "target": full_name}

        test_cases = [test_case_1, test_case_2, test_case_3]
        for test_case in test_cases:
            reply_timeseries = session.read_timeseries_points(**test_case)
            verify_timeseries_2(reply_timeseries)
    except grpc.RpcError as error:
        pytest.fail(f"Could not read timeseries points: {error}")


@pytest.mark.database
def test_read_timeseries_points_with_different_datetime_timezones(session):
    """
    Check that timeseries points read accepts time zone aware and
    naive (treated as UTC) datetimes as input arguments.
    """
    timeseries, start_time, end_time, _, _ = get_timeseries_2()

    # confirm start_time and end_time are time zone naive
    assert start_time.tzinfo is None and end_time.tzinfo is None

    # replace to UTC, because we treat time zone naive datetime as UTC
    start_time_utc = start_time.replace(tzinfo=tz.UTC)
    end_time_utc = end_time.replace(tzinfo=tz.UTC)

    local_tzinfo = tz.gettz('Europe/Warsaw')

    # now we can convert to different time zones (from time zone aware UTC datetime)
    start_time_local = start_time_utc.astimezone(local_tzinfo)
    end_time_local = end_time_utc.astimezone(local_tzinfo)

    try:
        test_case_naive = {"start_time": start_time, "end_time": end_time,
                           "target": timeseries.timeseries_key}
        test_case_utc = {"start_time": start_time_utc, "end_time": end_time_utc,
                         "target": timeseries.timeseries_key}
        test_case_local = {"start_time": start_time_local, "end_time": end_time_local,
                           "target": timeseries.timeseries_key}
        test_case_mixed = {"start_time": start_time_local, "end_time": end_time_utc,
                           "target": timeseries.timeseries_key}

        test_cases = [test_case_naive, test_case_utc, test_case_local, test_case_mixed]
        for test_case in test_cases:
            reply_timeseries = session.read_timeseries_points(**test_case)
            verify_timeseries_2(reply_timeseries)
    except grpc.RpcError as e:
        pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.database
def test_write_timeseries_points(session):
    """
    Check that timeseries points write accepts time series with time zone aware and
    naive (treated as UTC) datetimes as input interval (start_time and end_time arguments).
    """
    ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_2()

    # confirm start_time and end_time are time zone naive
    assert start_time.tzinfo is None and end_time.tzinfo is None

    # replace to UTC, because we treat time zone naive datetime as UTC
    start_time_utc = start_time.replace(tzinfo=tz.UTC)
    end_time_utc = end_time.replace(tzinfo=tz.UTC)

    local_tzinfo = tz.gettz('Europe/Warsaw')

    # now we can convert to different time zones (from time zone aware UTC datetime)
    start_time_local = start_time_utc.astimezone(local_tzinfo)
    end_time_local = end_time_utc.astimezone(local_tzinfo)

    test_case_naive = {"start_time": start_time, "end_time": end_time}
    test_case_utc = {"start_time": start_time_utc, "end_time": end_time_utc}
    test_case_local = {"start_time": start_time_local, "end_time": end_time_local}
    test_case_mixed = {"start_time": start_time_local, "end_time": end_time_utc}
    test_case_deduct = {"start_time": None, "end_time": None}  # in this case the start and end time will be taken from PyArrow table

    test_cases = [test_case_naive, test_case_utc, test_case_local, test_case_mixed, test_case_deduct]
    for test_case in test_cases:
        timeseries = Timeseries(table=modified_table, start_time=test_case['start_time'], end_time=test_case['end_time'], full_name=full_name)
        try:
            session.write_timeseries_points(timeseries)
            written_ts = session.read_timeseries_points(target=ts_entry.id,
                                                        start_time=datetime(2016, 1, 1, 1, 0, 0),
                                                        end_time=datetime(2016, 1, 1, 3, 0, 0))
            assert written_ts.number_of_points == 3
            utc_time = written_ts.arrow_table[0]
            assert utc_time[0].as_py() == datetime(2016, 1, 1, 1, 0, 0)
            assert utc_time[1].as_py() == datetime(2016, 1, 1, 2, 0, 0)
            assert utc_time[2].as_py() == datetime(2016, 1, 1, 3, 0, 0)
            flags = written_ts.arrow_table[1]
            for flag in flags:
                assert flag.as_py() == Timeseries.PointFlags.OK.value
            values = written_ts.arrow_table[2]
            assert values[0].as_py() == 0
            assert values[1].as_py() == 10
            assert values[2].as_py() == 1000

            session.rollback()

        except grpc.RpcError as e:
            pytest.fail(f"Could not write timeseries points {e}")


@pytest.mark.database
def test_write_timeseries_points_with_different_pyarrow_table_datetime_timezones(session):
    """
    Check that timeseries points write accepts PyArrow data with time zone aware timestamps.
    """
    ts_entry, _, _, _, full_name = get_timeseries_2()

    # There is problem with using in PyArrow time zone from dateutil gettz
    # I've found some PyArrow JIRA ticket with support for dateutil time zones:
    # https://issues.apache.org/jira/browse/ARROW-5248
    # Maybe it will solve the problem observed. It should be available in PyArrow 8.0.0.
    #local_tzinfo = tz.gettz('Europe/Warsaw')

    # For now lets create tzinfo using datetime timezone
    some_tzinfo = timezone(timedelta(hours=-3))

    arrays = [
        pa.array([datetime(2016, 1, 1, 1, tzinfo=some_tzinfo), datetime(2016, 1, 1, 2, tzinfo=some_tzinfo), datetime(2016, 1, 1, 3, tzinfo=some_tzinfo)]),
        pa.array([0, 0, 0]),
        pa.array([4.0, 44.0, 444.0])]
    modified_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    timeseries = Timeseries(table=modified_table, start_time=datetime(2016, 1, 1, 1, tzinfo=some_tzinfo), end_time=datetime(2016, 1, 1, 4, tzinfo=some_tzinfo), full_name=full_name)
    try:
        session.write_timeseries_points(timeseries)
        written_ts = session.read_timeseries_points(target=ts_entry.id,
                                                    start_time=datetime(2016, 1, 1, 1, tzinfo=some_tzinfo),
                                                    end_time=datetime(2016, 1, 1, 3, tzinfo=some_tzinfo))
        assert written_ts.number_of_points == 3
        utc_time = written_ts.arrow_table[0]
        # Mesh returns timestamps in UTC format, to compare them we need to make both of them either
        # time zone aware or naive. In this case we are converting them to time zone aware objects.
        assert utc_time[0].as_py().replace(tzinfo=tz.UTC) == datetime(2016, 1, 1, 1, tzinfo=some_tzinfo).astimezone(tz.UTC)
        assert utc_time[1].as_py().replace(tzinfo=tz.UTC) == datetime(2016, 1, 1, 2, tzinfo=some_tzinfo).astimezone(tz.UTC)
        assert utc_time[2].as_py().replace(tzinfo=tz.UTC) == datetime(2016, 1, 1, 3, tzinfo=some_tzinfo).astimezone(tz.UTC)
        flags = written_ts.arrow_table[1]
        for flag in flags:
            assert flag.as_py() == Timeseries.PointFlags.OK.value
        values = written_ts.arrow_table[2]
        assert values[0].as_py() == 4
        assert values[1].as_py() == 44
        assert values[2].as_py() == 444

        session.rollback()

    except grpc.RpcError as error:
        pytest.fail(f"Could not write timeseries points {error}")


@pytest.mark.database
def test_get_timeseries_resource(session):
    """Check that time series resource can be retrieved."""

    physical_timeseries = get_physical_timeseries()
    virtual_timeseries = get_virtual_timeseries()

    test_cases = [physical_timeseries, virtual_timeseries]

    for test_case in test_cases:
        timeseries_info = session.get_timeseries_resource_info(
            timeseries_key=test_case.timeseries_key)
        assert isinstance(timeseries_info, TimeseriesResource)
        assert timeseries_info.timeseries_key == test_case.timeseries_key
        assert timeseries_info.path == test_case.path
        assert timeseries_info.name == test_case.name
        assert timeseries_info.temporary == test_case.temporary
        assert timeseries_info.curve_type == test_case.curve_type
        assert timeseries_info.resolution == test_case.resolution
        assert timeseries_info.unit_of_measurement == test_case.unit_of_measurement
        #assert timeseries_info.virtual_timeseries_expression == test_case.virtual_timeseries_expression


@pytest.mark.database
def test_update_timeseries_resource(session):
    """Check that time series resource can be updated."""

    new_curve_type = Timeseries.Curve.STAIRCASESTARTOFSTEP
    new_unit_of_measurement = "Unit1"

    timeseries = get_physical_timeseries()

    test_id = {"timeseries_key": timeseries.timeseries_key}
    test_new_curve_type = {"new_curve_type": new_curve_type}
    test_new_unit_of_measurement = {"new_unit_of_measurement": new_unit_of_measurement}
    test_cases = [
        {**test_id, **test_new_curve_type},
        {**test_id, **test_new_unit_of_measurement},
        {**test_id, **test_new_curve_type, **test_new_unit_of_measurement}
    ]

    for test_case in test_cases:
        session.update_timeseries_resource_info(**test_case)
        timeseries_info = session.get_timeseries_resource_info(**test_id)

        if "new_curve_type" in test_case:
            assert timeseries_info.curve_type == new_curve_type
        if "new_unit_of_measurement" in test_case:
            assert timeseries_info.unit_of_measurement == new_unit_of_measurement

        session.rollback()


@pytest.mark.database
def test_write_timeseries_points_using_timskey(session):
    """Check that time series can be written to the server using timskey."""

    ts_entry, start_time, end_time, modified_table, _ = get_timeseries_2()
    timeseries = Timeseries(table=modified_table, start_time=start_time, end_time=end_time,
                            timskey=ts_entry.timeseries_key)
    try:
        session.write_timeseries_points(
            timeseries=timeseries
        )
    except grpc.RpcError:
        pytest.fail("Could not write timeseries points")


@pytest.mark.database
def test_commit(connection):
    """Check that commit keeps changes between sessions"""
    attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.TsCalcAtt"
    new_local_expression = "something"

    with connection.create_session() as session1:
        try:
            # check baseline
            attribute1 = session1.get_timeseries_attribute(attribute_path)
            old_local_expression = attribute1.expression
            assert old_local_expression != new_local_expression

            # change something
            session1.update_timeseries_attribute(
                attribute_path, new_local_expression=new_local_expression)

            # commit
            session1.commit()

            # check that the change is in the session
            attribute2 = session1.get_timeseries_attribute(attribute_path)
            assert attribute2.expression == new_local_expression

            # rollback
            session1.rollback()

            # check that changes are still there
            attribute3 = session1.get_timeseries_attribute(attribute_path)
            assert attribute3.expression == new_local_expression

        except grpc.RpcError as error:
            pytest.fail(f"Could not commit changes: {error}")

    with connection.create_session() as session2:
        try:
            # check that the change is still there
            attribute4 = session2.get_timeseries_attribute(attribute_path)
            assert attribute4.expression == new_local_expression

            # change it back to what is was originally
            session2.update_timeseries_attribute(
                attribute_path, new_local_expression=old_local_expression)

            # commit
            session2.commit()

            # check that status has been restored (important to keep db clean)
            attribute5 = session2.get_timeseries_attribute(attribute_path)
            assert attribute5.expression == old_local_expression

        except grpc.RpcError as error:
            pytest.fail(f"Could not restore committed changes: {error}")


@pytest.mark.database
def test_rollback(session):
    """Check that rollback discards changes made in the current session."""

    timeseries = get_physical_timeseries()
    new_unit_of_measurement = "Unit1"

    # check baseline
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement

    # change something
    session.update_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key,
        new_unit_of_measurement=new_unit_of_measurement)

    # check that the change is in the session
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement == new_unit_of_measurement

    # rollback
    session.rollback()

    # check that changes have been discarded
    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key)
    assert timeseries_info.unit_of_measurement != new_unit_of_measurement


@pytest.mark.database
@pytest.mark.parametrize('resolution, expected_number_of_points',
    [(Timeseries.Resolution.MIN15, 33),
     (Timeseries.Resolution.HOUR, 9),
     (Timeseries.Resolution.DAY, 1),
     (Timeseries.Resolution.WEEK, 1),
     (Timeseries.Resolution.MONTH, 2),
     (Timeseries.Resolution.YEAR, 2)])
@pytest.mark.parametrize('method',
    [Transform.Method.SUM,
     Transform.Method.SUMI,
     Transform.Method.AVG,
     Transform.Method.AVGI,
     Transform.Method.FIRST,
     Transform.Method.LAST,
     Transform.Method.MIN,
     Transform.Method.MAX])
@pytest.mark.parametrize('timezone',
    [None,
     Timezone.LOCAL,
     Timezone.STANDARD,
     Timezone.UTC])
def test_read_transformed_timeseries_points(
        session,
        resolution, method, timezone,
        expected_number_of_points: int
):
    """Check that transformed timeseries points can be read"""

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    _, full_name = get_timeseries_attribute_2()

    reply_timeseries = session.transform_functions(
        full_name, start_time, end_time).transform(
            resolution, method, timezone)

    assert reply_timeseries.is_calculation_expression_result

    if resolution in [Timeseries.Resolution.HOUR,
                        Timeseries.Resolution.DAY,
                        Timeseries.Resolution.WEEK,
                        Timeseries.Resolution.MONTH,
                        Timeseries.Resolution.YEAR]:
        # logic for those resolutions is complex and depends on other parameters
        # make sure the result has at least 1 point and no error is thrown
        assert reply_timeseries.number_of_points >= 1
        return

    assert reply_timeseries.number_of_points == expected_number_of_points

    expected_date = start_time
    delta = 1 if expected_number_of_points == 1 else (end_time - start_time) / (expected_number_of_points - 1)
    index = 0
    d = reply_timeseries.arrow_table.to_pydict()

    for utc_time, flags, value in zip(d['utc_time'], d['flags'], d['value']):
        # check timestamps
        assert utc_time == expected_date

        # check flags and values
        # hours, flags
        # <1, 3> - OK
        # (3, 4) - MISSING
        # <4, 5) - NOT_OK | MISSING
        # <5, 10) - OK
        if expected_date > datetime(2016, 1, 1, 3) and expected_date < datetime(2016, 1, 1, 4):
            assert flags == Timeseries.PointFlags.MISSING.value
            assert math.isnan(value)
        elif expected_date >= datetime(2016, 1, 1, 4) and expected_date < datetime(2016, 1, 1, 5):
            expected_flags = Timeseries.PointFlags.NOT_OK.value | Timeseries.PointFlags.MISSING.value
            assert flags == expected_flags
            assert math.isnan(value)
        else:
            assert flags == Timeseries.PointFlags.OK.value
            # check values for one some combinations (method AVG and resolution MIN15)
            if method is Transform.Method.AVG and resolution is Timeseries.Resolution.MIN15:
                # the original timeseries data is in hourly resolution,
                # starts with 1 and the value is incremented with each hour up to 9
                # here we are using 15 min resolution, so the delta between each 15 min point is 0.25
                assert value == 1 + index * 0.25

        expected_date += delta
        index += 1


@pytest.mark.database
def test_read_transformed_timeseries_points_with_uuid(session):
    """
    Check that transformed timeseries read by full_name or UUID
    (both pointing to the same object) return the same data.
    """

    # set interval where there are no NaNs to comfortably use `assert ==``
    start_time = datetime(2016, 1, 1, 5, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    _, full_name = get_timeseries_attribute_2()

    # first read timeseries UUID (it is set dynamically)
    timeseries = session.read_timeseries_points(target=full_name,
                                                start_time=start_time,
                                                end_time=end_time)
    ts_uuid = timeseries.uuid

    reply_timeseries_full_name = session.transform_functions(
        full_name, start_time, end_time).transform(
            Timeseries.Resolution.MIN15, Transform.Method.SUM)

    reply_timeseries_uuid = session.transform_functions(
        ts_uuid, start_time, end_time).transform(
            Timeseries.Resolution.MIN15, Transform.Method.SUM)

    assert reply_timeseries_full_name.is_calculation_expression_result == reply_timeseries_uuid.is_calculation_expression_result
    assert len(reply_timeseries_full_name.arrow_table) == len(reply_timeseries_uuid.arrow_table)

    for column_index in range(0, 3):
        assert reply_timeseries_full_name.arrow_table[column_index] == reply_timeseries_uuid.arrow_table[column_index]


@pytest.mark.database
def test_forecast_get_all_forecasts(session):
    """
    Check that running forecast `get_all_forecasts`
    does not throw exception for any combination of parameters.
    """

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    _, full_name = get_timeseries_attribute_2()

    reply_timeseries = session.forecast_functions(
        full_name, start_time, end_time).get_all_forecasts()
    assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0


@pytest.mark.database
@pytest.mark.parametrize('forecast_start',
    [(None, None),
     (datetime(2016, 1, 2), datetime(2016, 1, 8))])
@pytest.mark.parametrize('available_at_timepoint',
    [None,
     datetime(2016, 1, 5, 17, 48, 11, 123456)])
def test_forecast_get_forecast(session, forecast_start, available_at_timepoint):
    """
    Check that running forecast `get_forecast`
    does not throw exception for any combination of parameters.
    """

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    forecast_start_min, forecast_start_max = forecast_start
    _, full_name = get_timeseries_attribute_2()

    reply_timeseries = session.forecast_functions(
        full_name, start_time, end_time).get_forecast(
            forecast_start_min, forecast_start_max, available_at_timepoint)
    assert reply_timeseries.is_calculation_expression_result


@pytest.mark.database
def test_history_get_ts_as_of_time(session):
    """
    Check that running history `get_ts_as_of_time`
    does not throw exception for any combination of parameters.
    """

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    available_at_timepoint = datetime(2016, 1, 5, 17, 48, 11, 123456)
    _, full_name = get_timeseries_attribute_2()

    reply_timeseries = session.history_functions(
        full_name, start_time, end_time).get_ts_as_of_time(
            available_at_timepoint)
    assert reply_timeseries.is_calculation_expression_result


@pytest.mark.database
@pytest.mark.parametrize('max_number_of_versions_to_get',
    [1, 2, 5])
def test_history_get_ts_historical_versions(session, max_number_of_versions_to_get):
    """
    Check that running history `get_ts_historical_versions`
    does not throw exception for any combination of parameters.
    """

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    _, full_name = get_timeseries_attribute_2()

    reply_timeseries = session.history_functions(
        full_name, start_time, end_time).get_ts_historical_versions(
            max_number_of_versions_to_get)
    assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0


@pytest.mark.database
def test_statistical_sum(session):
    """
    Check that running statistical `sum`
    does not throw exception for any combination of parameters.
    """
    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    _, full_name = get_timeseries_attribute_2()

    reply_timeseries = session.statistical_functions(
        full_name, start_time, end_time).sum(search_query='some_query')
    assert reply_timeseries.is_calculation_expression_result


@pytest.mark.database
def test_statistical_sum_single_timeseries(session):
    """
    Check that running statistical `sum_single_timeseries` works correctly.
    """
    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    _, full_name = get_timeseries_attribute_2()

    result = session.statistical_functions(
        full_name, start_time, end_time).sum_single_timeseries()
    assert isinstance(result, float) and result == 41.0


if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
