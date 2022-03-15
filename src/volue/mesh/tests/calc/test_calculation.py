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
def test_convert_datetime_to_mesh_calc_format_converts_datetime_to_correct_format():
    """
    Check that datetime parameter is correctly converted to format expected by Mesh calculator.
    If datetime is time zone naive it should be treated as UTC.
    E.g. for 2021.09.17 15:25:00
    Expected: UTC20210917152500000
    """
    test_time = datetime(2016, 1, 5, 17, 48, 11, 123456)
    expected_datetime_format = 'UTC20160105174811123'

    converted_datetime = _convert_datetime_to_mesh_calc_format(test_time)
    assert expected_datetime_format == converted_datetime


@pytest.mark.unittest
def test_convert_utc_datetime_to_mesh_calc_format_converts_datetime_to_correct_format():
    """
    Check that datetime parameter is correctly converted to format expected by Mesh calculator.
    If datetime is already expressed in UTC it should be taken as it is (no conversion needed).
    E.g. for 2021.09.17 15:25:00
    Expected: UTC20210917152500000
    """
    test_time = datetime(2017, 2, 15, 8, 48, 11, 123456, tzinfo=tz.UTC)
    expected_datetime_format = 'UTC20170215084811123'

    converted_datetime = _convert_datetime_to_mesh_calc_format(test_time)
    assert expected_datetime_format == converted_datetime


@pytest.mark.unittest
def test_convert_utc_datetime_to_mesh_calc_format_converts_datetime_to_correct_format():
    """
    Check that datetime parameter is correctly converted to format expected by Mesh calculator.
    If datetime is expressed in some time zone it should converted to UTC and DST should be taken into account.
    E.g. for 2021.09.17 15:25:00
    Expected: UTC20210917152500000
    """
    local_tzinfo = tz.gettz('Europe/Warsaw')

    # during daylight saving period (UTC+2)
    test_time = datetime(2017, 9, 15, 8, 48, 11, 123456, tzinfo=local_tzinfo)
    expected_datetime_format = 'UTC20170915064811123'

    converted_datetime = _convert_datetime_to_mesh_calc_format(test_time)
    assert expected_datetime_format == converted_datetime

    # outside of daylight saving period (UTC+1)
    test_time = datetime(2017, 2, 15, 8, 48, 11, 123456, tzinfo=local_tzinfo)
    expected_datetime_format = 'UTC20170215074811123'

    converted_datetime = _convert_datetime_to_mesh_calc_format(test_time)
    assert expected_datetime_format == converted_datetime


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
