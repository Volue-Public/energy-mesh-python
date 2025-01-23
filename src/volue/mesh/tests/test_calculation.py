"""
Tests for volue.mesh.calc
"""

import math
import sys
import uuid
from datetime import datetime
from typing import List

import pytest
from dateutil import tz

from volue.mesh import Timeseries
from volue.mesh.calc import transform
from volue.mesh.calc.common import (
    Timezone,
    _convert_datetime_to_mesh_calc_format,
    _parse_single_float_response,
    _parse_single_timeseries_response,
)
from volue.mesh.proto.calc.v1alpha import calc_pb2

ATTRIBUTE_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.TsRawAtt"


def get_targets(session):
    """
    Return all possible targets for calculation APIs, like: ID or path.
    """
    # ID is auto-generated when creating an attribute, so
    # first we need to read it.
    attribute = session.get_attribute(ATTRIBUTE_PATH)
    return [attribute.id, ATTRIBUTE_PATH, attribute]


@pytest.mark.unittest
@pytest.mark.parametrize(
    "test_time, expected_result",
    [
        (datetime(2016, 1, 5, 17, 48, 11, 123456), "UTC20160105174811123"),
        (
            datetime(2017, 2, 15, 8, 48, 11, 123456, tzinfo=tz.UTC),
            "UTC20170215084811123",
        ),
        (
            datetime(2017, 9, 15, 8, 48, 11, 123456, tzinfo=tz.gettz("Europe/Warsaw")),
            "UTC20170915064811123",
        ),  # during daylight saving period (UTC+2)
        (
            datetime(2017, 2, 15, 8, 48, 11, 123456, tzinfo=tz.gettz("Europe/Warsaw")),
            "UTC20170215074811123",
        ),
    ],
)  # outside of daylight saving period (UTC+1)
def test_convert_local_datetime_to_mesh_calc_format_converts_datetime_to_correct_format(
    test_time: datetime, expected_result: str
):
    """
    Check that datetime parameter is correctly converted to format expected by Mesh calculator.
    If datetime is time zone naive it should be treated as UTC.
    If datetime is already expressed in UTC it should be taken as it is (no conversion needed).
    If datetime is expressed in some time zone it should converted to UTC and DST should be taken into account.
    E.g. for 2021.09.17 15:25:00
    Expected: UTC20210917152500000
    """
    converted_datetime = _convert_datetime_to_mesh_calc_format(test_time)
    assert expected_result == converted_datetime


@pytest.mark.unittest
def test_parsing_single_timeseries_response_with_invalid_calculation_result_should_throw():
    """
    Check that expected exception is thrown when calculation result is not
    a single time series.
    """
    response = calc_pb2.CalculationResponse()
    # no time series at all
    with pytest.raises(RuntimeError, match=".*invalid calculation result*"):
        _parse_single_timeseries_response(response)


@pytest.mark.unittest
def test_parsing_single_float_response_with_invalid_calculation_result_should_throw():
    """
    Check that expected exception is thrown when calculation result is not a single float.
    """
    response = calc_pb2.CalculationResponse()
    # no float values at all
    with pytest.raises(RuntimeError, match=".*invalid calculation result*"):
        _parse_single_float_response(response)


@pytest.mark.unittest
def test_preparing_transform_request_with_unsupported_resolution_should_throw():
    """
    Check that expected exception is thrown when trying to
    read transformed time series with unsupported resolution.
    """
    session_id = uuid.uuid4()  # generate random UUID

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    base = transform.TransformFunctions(
        session_id, ATTRIBUTE_PATH, start_time, end_time
    )

    unsupported_resolutions = [
        Timeseries.Resolution.BREAKPOINT,
        Timeseries.Resolution.UNDEFINED,
        Timeseries.Resolution.UNSPECIFIED,
    ]

    for resolution in unsupported_resolutions:
        with pytest.raises(
            ValueError, match=f".*'{resolution.name}' resolution is unsupported.*"
        ):
            base._transform_expression(resolution, transform.Method.SUM, None, None)


@pytest.mark.unittest
@pytest.mark.parametrize("timezone", [Timezone.LOCAL, Timezone.STANDARD, Timezone.UTC])
def test_preparing_transform_request_with_timezone_should_add_this_parameter_to_calculation_expression(
    timezone,
):
    """
    Check that providing optional `timezone` parameter is
    reflected in generated calculation expression.
    """
    session_id = uuid.uuid4()  # generate random UUID
    target = "some_path"
    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    resolution = Timeseries.Resolution.MIN15
    method = transform.Method.SUM
    base = transform.TransformFunctions(session_id, target, start_time, end_time)

    # first check that if `timezone` is not provided then
    # it is not present in generated calculation expression
    expression = base._transform_expression(resolution, method, None, None)
    assert f"'{timezone.name}'" not in str(expression)

    # now it should be in generated calculation expression
    expression = base._transform_expression(resolution, method, timezone, None)
    assert f"'{timezone.name}'" in str(expression)


@pytest.mark.database
@pytest.mark.parametrize(
    "resolution, expected_number_of_points",
    [
        (Timeseries.Resolution.MIN15, 33),
        (Timeseries.Resolution.MIN30, 17),
        (Timeseries.Resolution.HOUR, 9),
        (Timeseries.Resolution.DAY, 1),
        (Timeseries.Resolution.WEEK, 1),
        (Timeseries.Resolution.MONTH, 2),
        (Timeseries.Resolution.YEAR, 2),
    ],
)
@pytest.mark.parametrize(
    "method",
    [
        transform.Method.SUM,
        transform.Method.SUMI,
        transform.Method.AVG,
        transform.Method.AVGI,
        transform.Method.FIRST,
        transform.Method.LAST,
        transform.Method.MIN,
        transform.Method.MAX,
    ],
)
@pytest.mark.parametrize(
    "timezone", [None, Timezone.LOCAL, Timezone.STANDARD, Timezone.UTC]
)
def test_read_transformed_timeseries_points(
    session, resolution, method, timezone, expected_number_of_points: int
):
    """Check that transformed time series points can be read."""

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    # provide all possible and applicable target types, like path or ID
    targets = get_targets(session)

    for target in targets:
        reply_timeseries = session.transform_functions(
            target, start_time, end_time
        ).transform(resolution, method, timezone)

        assert reply_timeseries.is_calculation_expression_result

        # To avoid bloating this test too much check extensively one resolution
        # i.e. MIN15. For others just make sure the result has at least 1 point
        # and no error is thrown.
        if resolution in [
            Timeseries.Resolution.HOUR,
            Timeseries.Resolution.DAY,
            Timeseries.Resolution.WEEK,
            Timeseries.Resolution.MONTH,
            Timeseries.Resolution.YEAR,
        ]:
            assert reply_timeseries.number_of_points >= 1
            return

        assert reply_timeseries.number_of_points == expected_number_of_points

        expected_date = start_time
        delta = (
            1
            if expected_number_of_points == 1
            else (end_time - start_time) / (expected_number_of_points - 1)
        )
        index = 0
        d = reply_timeseries.arrow_table.to_pydict()

        for utc_time, flags, value in zip(d["utc_time"], d["flags"], d["value"]):
            # check timestamps
            assert utc_time == expected_date

            # check flags and values
            # hours, flags
            # <1, 3> - OK
            # (3, 4) - MISSING
            # <4, 5) - NOT_OK | MISSING
            # <5, 10) - OK
            if expected_date > datetime(2016, 1, 1, 3) and expected_date < datetime(
                2016, 1, 1, 4
            ):
                assert flags == Timeseries.PointFlags.MISSING.value
                assert math.isnan(value)
            elif expected_date >= datetime(2016, 1, 1, 4) and expected_date < datetime(
                2016, 1, 1, 5
            ):
                expected_flags = (
                    Timeseries.PointFlags.NOT_OK.value
                    | Timeseries.PointFlags.MISSING.value
                )
                assert flags == expected_flags
                assert math.isnan(value)
            else:
                assert flags == Timeseries.PointFlags.OK.value
                # check values for one some combinations (method AVG and resolution MIN15)
                if (
                    method is transform.Method.AVG
                    and resolution is Timeseries.Resolution.MIN15
                ):
                    # the original timeseries data is in hourly resolution,
                    # starts with 1 and the value is incremented with each hour up to 9
                    # here we are using 15 min resolution, so the delta between each 15 min point is 0.25
                    assert value == 1 + index * 0.25

            expected_date += delta
            index += 1


@pytest.mark.database
def test_forecast_get_all_forecasts(session):
    """
    Check that running forecast `get_all_forecasts`
    does not throw exception for any combination of parameters.
    """

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    targets = get_targets(session)

    for target in targets:
        reply_timeseries = session.forecast_functions(
            target, start_time, end_time
        ).get_all_forecasts()
        assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0


@pytest.mark.database
@pytest.mark.parametrize(
    "forecast_start", [(None, None), (datetime(2016, 1, 2), datetime(2016, 1, 8))]
)
@pytest.mark.parametrize(
    "available_at_timepoint", [None, datetime(2016, 1, 5, 17, 48, 11, 123456)]
)
def test_forecast_get_forecast(session, forecast_start, available_at_timepoint):
    """
    Check that running forecast `get_forecast`
    does not throw exception for any combination of parameters.
    """

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    forecast_start_min, forecast_start_max = forecast_start

    targets = get_targets(session)

    for target in targets:
        reply_timeseries = session.forecast_functions(
            target, start_time, end_time
        ).get_forecast(forecast_start_min, forecast_start_max, available_at_timepoint)
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

    targets = get_targets(session)

    for target in targets:
        reply_timeseries = session.history_functions(
            target, start_time, end_time
        ).get_ts_as_of_time(available_at_timepoint)
        assert reply_timeseries.is_calculation_expression_result


@pytest.mark.database
@pytest.mark.parametrize("max_number_of_versions_to_get", [1, 2, 5])
def test_history_get_ts_historical_versions(session, max_number_of_versions_to_get):
    """
    Check that running history `get_ts_historical_versions`
    does not throw exception for any combination of parameters.
    """

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    targets = get_targets(session)

    for target in targets:
        reply_timeseries = session.history_functions(
            target, start_time, end_time
        ).get_ts_historical_versions(max_number_of_versions_to_get)
        assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0


@pytest.mark.database
def test_statistical_sum(session):
    """
    Check that running statistical `sum`
    does not throw exception for any combination of parameters.
    """
    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    targets = get_targets(session)

    for target in targets:
        reply_timeseries = session.statistical_functions(
            target, start_time, end_time
        ).sum(search_query="some_query")
        assert reply_timeseries.is_calculation_expression_result


@pytest.mark.database
def test_statistical_sum_single_timeseries(session):
    """
    Check that running statistical `sum_single_timeseries` works correctly.
    """
    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    targets = get_targets(session)

    for target in targets:
        result = session.statistical_functions(
            target, start_time, end_time
        ).sum_single_timeseries()
        assert isinstance(result, float) and result == 41.0


@pytest.mark.asyncio
@pytest.mark.database
async def test_calculation_functions_async(async_session):
    """For async run the simplest test, implementation is the same."""

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    target = ATTRIBUTE_PATH

    reply_timeseries = await async_session.transform_functions(
        target, start_time, end_time
    ).transform(Timeseries.Resolution.HOUR, transform.Method.SUM, Timezone.STANDARD)
    assert (
        reply_timeseries.is_calculation_expression_result
        and reply_timeseries.number_of_points == 8
    )

    reply_timeseries = await async_session.forecast_functions(
        target, start_time, end_time
    ).get_all_forecasts()
    assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0

    reply_timeseries = await async_session.forecast_functions(
        target, start_time, end_time
    ).get_forecast(datetime(2016, 1, 1, 2), datetime(2016, 1, 1, 8))
    assert reply_timeseries.is_calculation_expression_result

    reply_timeseries = await async_session.history_functions(
        target, start_time, end_time
    ).get_ts_as_of_time(datetime(2016, 1, 1, 5))
    assert reply_timeseries.is_calculation_expression_result

    reply_timeseries = await async_session.history_functions(
        target, start_time, end_time
    ).get_ts_historical_versions(1)
    assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0

    reply_timeseries = await async_session.statistical_functions(
        target, start_time, end_time
    ).sum(search_query="some_query")
    assert reply_timeseries.is_calculation_expression_result

    result = await async_session.statistical_functions(
        target, start_time, end_time
    ).sum_single_timeseries()
    assert isinstance(result, float) and result == 41.0


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
