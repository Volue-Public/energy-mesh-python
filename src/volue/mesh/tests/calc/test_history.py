from datetime import datetime
import uuid
from matplotlib.style import available
from pandas import date_range
import pytest

from volue.mesh import Timeseries
from volue.mesh.calc import history as History
from volue.mesh.calc.common import Timezone
from volue.mesh.proto import mesh_pb2
from volue.mesh.tests.test_utilities.utilities import  get_timeseries_attribute_2


@pytest.mark.unittest
def test_parsing_invalid_history_result_should_throw():
    """
    Check that expected exception is thrown when history result is not a single timeseries.
    """
    response = mesh_pb2.CalculationResponse()
    # no timeseries at all
    with pytest.raises(RuntimeError, match=".*invalid history result*"):
        History.parse_response(response)


@pytest.mark.unittest
@pytest.mark.parametrize('timezone',
    [Timezone.LOCAL,
     Timezone.STANDARD,
     Timezone.UTC])
def test_preparing_history_request_with_timezone_should_add_this_parameter_to_calculation_expression(timezone):
    """
    Check that providing optional `timezone` parameter is
    reflected in generated calculation expression.
    """
    session_id = uuid.uuid4()  # generate random UUID

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    resolution = Timeseries.Resolution.MIN15
    available_at_timepoint = datetime.now()

    history_parameters_no_timezone = History.Parameters(
        resolution, available_at_timepoint)
    history_parameters_with_timezone = History.Parameters(
        resolution, available_at_timepoint, timezone)

    _, full_name = get_timeseries_attribute_2()

    relative_to = mesh_pb2.ObjectId()
    relative_to.full_name = full_name

    # first check that if `timezone` is not provided then
    # it is not present in generated calculation expression
    request = History.prepare_request(
        session_id, start_time, end_time, relative_to, history_parameters_no_timezone)
    assert f"'{timezone.name}" not in str(request.expression)

    # now it should be in generated calculation expression
    request = History.prepare_request(
        session_id, start_time, end_time, relative_to, history_parameters_with_timezone)
    assert f"'{timezone.name}" in str(request.expression)


@pytest.mark.unittest
def test_preparing_history_request_converts_datetime_to_correct_format_in_calculation_expression():
    """
    Check that 'available_at_timepoint' parameter is correctly converted to expected format.
    E.g. for 2021.09.17 15:25:00
    Expected: 20210917152500000
    """
    session_id = uuid.uuid4()  # generate random UUID

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    function = History.Function.AS_OF_TIME
    available_at_timepoint = datetime(2016, 1, 5, 17, 48, 11, 123456)
    expected_datetime_format = '20160105174811123'

    history_parameters_no_timezone = History.Parameters(
        function, available_at_timepoint)

    _, full_name = get_timeseries_attribute_2()

    relative_to = mesh_pb2.ObjectId()
    relative_to.full_name = full_name

    request = History.prepare_request(
        session_id, start_time, end_time, relative_to, history_parameters_no_timezone)
    assert f"'{expected_datetime_format}'" in str(request.expression)

if __name__ == '__main__':
    pytest.main()
