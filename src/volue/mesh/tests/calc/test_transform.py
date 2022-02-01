from datetime import datetime
import uuid
import pytest

from volue.mesh import Timeseries
from volue.mesh.calc import transform as Transform
from volue.mesh.calc.common import Timezone
from volue.mesh.proto import mesh_pb2
from volue.mesh.tests.test_utilities.utilities import  get_timeseries_attribute_2


@pytest.mark.unittest
def test_preparing_transform_request_with_breakpoint_resolution_should_throw():
    """
    Check that expected exception is thrown when trying to
    read transfromed timeseries with unsupported resolution.
    """
    session_id = uuid.uuid4()  # generate random UUID

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    transform_parameters = Transform.Parameters(
        Timeseries.Resolution.BREAKPOINT, Transform.Method.SUM)
    _, full_name = get_timeseries_attribute_2()

    timeseries_attribute = mesh_pb2.ObjectId()
    timeseries_attribute.full_name = full_name

    with pytest.raises(ValueError, match=".*'BREAKPOINT' resolution is unsupported.*"):
        Transform.prepare_request(
            session_id, start_time, end_time, timeseries_attribute, transform_parameters)


@pytest.mark.unittest
def test_parsing_invalid_transform_result_should_throw():
    """
    Check that expected exception is thrown when transformation result is not a single timeseries.
    """
    response = mesh_pb2.CalculationResponse()
    # no timeseries at all
    with pytest.raises(RuntimeError, match=".*invalid transformation result*"):
        Transform.parse_response(response)


@pytest.mark.unittest
@pytest.mark.parametrize('timezone',
    [Timezone.LOCAL,
     Timezone.STANDARD,
     Timezone.UTC])
def test_preparing_transform_request_with_timezone_should_add_this_parameter_to_calculation_expression(timezone):
    """
    Check that providing optional `timezone` parameter is
    reflected in generated calculation expression.
    """
    session_id = uuid.uuid4()  # generate random UUID

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    resolution = Timeseries.Resolution.MIN15
    method = Transform.Method.SUM

    transform_parameters_no_timezone = Transform.Parameters(
        resolution, method)
    transform_parameters_with_timezone = Transform.Parameters(
        resolution, method, timezone)

    _, full_name = get_timeseries_attribute_2()

    timeseries_attribute = mesh_pb2.ObjectId()
    timeseries_attribute.full_name = full_name

    # first check that if `timezone` is not provided then
    # it is not present in generated calculation expression
    request = Transform.prepare_request(
        session_id, start_time, end_time, timeseries_attribute, transform_parameters_no_timezone)
    assert f"'{timezone.name}'" not in str(request.expression)

    # now it should be in generated calculation expression
    request = Transform.prepare_request(
        session_id, start_time, end_time, timeseries_attribute, transform_parameters_with_timezone)
    assert f"'{timezone.name}'" in str(request.expression)


if __name__ == '__main__':
    pytest.main()
