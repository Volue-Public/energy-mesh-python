from datetime import datetime
from dateutil import tz
import pytest

from volue.mesh.calc.common import Timezone, _convert_datetime_to_mesh_calc_format, _parse_single_float_response, _parse_single_timeseries_response
from volue.mesh.proto.core.v1alpha import core_pb2
from volue.mesh.tests.test_utilities.utilities import get_timeseries_attribute_2


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
@pytest.mark.parametrize('test_time, expected_result',
    [(datetime(2016, 1, 5, 17, 48, 11, 123456), 'UTC20160105174811123'),
     (datetime(2017, 2, 15, 8, 48, 11, 123456, tzinfo=tz.UTC), 'UTC20170215084811123'),
     (datetime(2017, 9, 15, 8, 48, 11, 123456, tzinfo=tz.gettz('Europe/Warsaw')), 'UTC20170915064811123'),  # during daylight saving period (UTC+2)
     (datetime(2017, 2, 15, 8, 48, 11, 123456, tzinfo=tz.gettz('Europe/Warsaw')), 'UTC20170215074811123')])  # outside of daylight saving period (UTC+1)
def test_convert_local_datetime_to_mesh_calc_format_converts_datetime_to_correct_format(
    test_time: datetime, expected_result: str):
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
