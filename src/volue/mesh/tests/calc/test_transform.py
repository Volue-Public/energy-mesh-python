"""
Tests for volue.mesh.calc.transform
"""

from datetime import datetime
import sys
import uuid

import pytest

from volue.mesh import Timeseries
from volue.mesh.calc.common import Timezone
from volue.mesh.calc import transform
from volue.mesh.calc.transform import TransformFunctions
from volue.mesh.tests.test_utilities.utilities import get_timeseries_attribute_2


@pytest.mark.unittest
def test_preparing_transform_request_with_breakpoint_resolution_should_throw():
    """
    Check that expected exception is thrown when trying to
    read transfromed timeseries with unsupported resolution.
    """
    session_id = uuid.uuid4()  # generate random UUID

    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)

    _, full_name = get_timeseries_attribute_2()

    base = TransformFunctions(session_id, full_name, start_time, end_time)

    with pytest.raises(ValueError, match=".*'BREAKPOINT' resolution is unsupported.*"):
        base._transform_expression(Timeseries.Resolution.BREAKPOINT, transform.Method.SUM, None, None)


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
    method = transform.Method.SUM

    _, full_name = get_timeseries_attribute_2()
    base = TransformFunctions(session_id, full_name, start_time, end_time)

    # first check that if `timezone` is not provided then
    # it is not present in generated calculation expression
    expression = base._transform_expression(resolution, method, None, None)
    assert f"'{timezone.name}'" not in str(expression)

    # now it should be in generated calculation expression
    expression = base._transform_expression(resolution, method, timezone, None)
    assert f"'{timezone.name}'" in str(expression)


if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv))
