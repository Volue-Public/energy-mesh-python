"""
Tests for volue.mesh.calc
"""

from datetime import datetime
import pytest

from volue.mesh.calc.common import Timezone, _convert_datetime_to_mesh_calc_format, _parse_single_float_response, _parse_single_timeseries_response
from volue.mesh.proto.core.v1alpha import core_pb2


@pytest.mark.unittest
def test_parsing_invalid_single_timeseries_response_should_throw():
    """
    Check that expected exception is thrown when calculation result is not a single timeseries.
    """
    response = core_pb2.CalculationResponse()
    # no timeseries at all
    with pytest.raises(RuntimeError, match=".*invalid calculation result*"):
        _parse_single_timeseries_response(response)


@pytest.mark.unittest
@pytest.mark.parametrize('timezone',
    [Timezone.LOCAL,
     Timezone.STANDARD,
     Timezone.UTC])
def test_convert_datetime_to_mesh_calc_format_with_timezone_should_add_this_parameter(timezone):
    """
    Check that providing optional `timezone` parameter is
    reflected in converted datetime string.
    """
    test_time = datetime(2016, 1, 1, 9, 0, 0)

    # first check that if `timezone` is not provided then
    # it is not present in generated calculation expression
    converted_datetime = _convert_datetime_to_mesh_calc_format(test_time)
    assert f"{timezone.name}" not in converted_datetime

    # now it should be in generated calculation expression
    converted_datetime = _convert_datetime_to_mesh_calc_format(test_time, timezone)
    print(converted_datetime)
    assert f"{timezone.name}" in converted_datetime


@pytest.mark.unittest
def test_convert_datetime_to_mesh_calc_format_converts_datetime_to_correct_format():
    """
    Check that datetime parameter is correctly converted to format expected by Mesh calculator.
    E.g. for 2021.09.17 15:25:00
    Expected: 20210917152500000
    """
    test_time = datetime(2016, 1, 5, 17, 48, 11, 123456)
    expected_datetime_format = '20160105174811123'

    converted_datetime = _convert_datetime_to_mesh_calc_format(test_time)
    assert f"{expected_datetime_format}" in converted_datetime


@pytest.mark.unittest
def test_parsing_single_timeseries_response_with_invalid_calculation_result_should_throw():
    """
    Check that expected exception is thrown when calculation result is not a single timeseries.
    """
    response = core_pb2.CalculationResponse()
    # no timeseries at all
    with pytest.raises(RuntimeError, match=".*invalid calculation result*"):
        _parse_single_timeseries_response(response)


@pytest.mark.unittest
def test_parsing_single_float_response_with_invalid_calculation_result_should_throw():
    """
    Check that expected exception is thrown when calculation result is not a single float.
    """
    response = core_pb2.CalculationResponse()
    # no float values at all
    with pytest.raises(RuntimeError, match=".*invalid calculation result*"):
        _parse_single_float_response(response)


if __name__ == '__main__':
    pytest.main()
