"""
Tests for volue.mesh.TimeseriesResource
"""

import random
import string
import sys

import grpc
import pytest

from volue.mesh import Timeseries, TimeseriesResource


INVALID_UNIT_OF_MEASUREMENT_NAME = "no_such_unit"


def get_physical_timeseries():
    """
    Physical time series from SimpleThermalModel test model.
    """
    ts_name = "chimney2TimeSeriesRaw"
    test_timeseries = TimeseriesResource(
        timeseries_key=3,
        temporary=False,
        curve_type=Timeseries.Curve.PIECEWISELINEAR,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement="Unit2",
        path=f"Resource/SimpleThermalTestResourceCatalog/{ts_name}",
        name=ts_name,
    )
    return test_timeseries


def get_virtual_timeseries():
    """
    Virtual time series from SimpleThermalModel test model.
    """
    ts_name = "simpleVtsTimeseries"
    test_timeseries = TimeseriesResource(
        timeseries_key=4,
        temporary=False,
        curve_type=Timeseries.Curve.PIECEWISELINEAR,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement=None,
        path=f"Resource/SimpleThermalTestResourceCatalog/{ts_name}",
        name=ts_name,
        virtual_timeseries_expression="##= %'/SimpleThermalTestResourceCatalog/plantTimeSeriesRaw' + 3\n",
    )
    return test_timeseries


@pytest.mark.database
@pytest.mark.parametrize(
    "timeseries", [get_virtual_timeseries(), get_physical_timeseries()]
)
def test_get_timeseries_resource(session, timeseries):
    """Check that time series resource can be retrieved."""

    timeseries_info = session.get_timeseries_resource_info(
        timeseries_key=timeseries.timeseries_key
    )
    assert isinstance(timeseries_info, TimeseriesResource)
    assert timeseries_info.timeseries_key == timeseries.timeseries_key
    assert timeseries_info.path == timeseries.path
    assert timeseries_info.name == timeseries.name
    assert timeseries_info.temporary == timeseries.temporary
    assert timeseries_info.curve_type == timeseries.curve_type
    assert timeseries_info.resolution == timeseries.resolution
    assert timeseries_info.unit_of_measurement == timeseries.unit_of_measurement

    if timeseries.virtual_timeseries_expression is None:
        assert timeseries_info.virtual_timeseries_expression == ""
    else:
        assert (
            timeseries_info.virtual_timeseries_expression
            == timeseries.virtual_timeseries_expression
        )


@pytest.mark.database
@pytest.mark.parametrize(
    "timeseries_key",
    [get_virtual_timeseries().timeseries_key, get_physical_timeseries().timeseries_key],
)
@pytest.mark.parametrize(
    "new_curve_type, new_unit_of_measurement",
    [
        (Timeseries.Curve.STAIRCASESTARTOFSTEP, None),
        (None, "Unit1"),
        (Timeseries.Curve.PIECEWISELINEAR, "Unit2"),
    ],
)
def test_update_timeseries_resource(
    session, timeseries_key, new_curve_type, new_unit_of_measurement
):
    """Check that time series resource can be updated."""
    session.update_timeseries_resource_info(
        timeseries_key, new_curve_type, new_unit_of_measurement
    )
    timeseries_info = session.get_timeseries_resource_info(timeseries_key)

    if new_curve_type is not None:
        assert timeseries_info.curve_type == new_curve_type
    if new_unit_of_measurement is not None:
        assert timeseries_info.unit_of_measurement == new_unit_of_measurement


@pytest.mark.database
def test_update_timeseries_resource_with_non_existing_unit_of_measurement(session):
    """
    Check that 'update_timeseries_resource_info' with non existing unit of
    measurement will throw.
    """

    timeseries_key = get_physical_timeseries().timeseries_key
    non_existing_unit_of_measurement = INVALID_UNIT_OF_MEASUREMENT_NAME

    original_unit_of_measurement = session.get_timeseries_resource_info(
        timeseries_key
    ).unit_of_measurement

    with pytest.raises(ValueError, match="invalid unit of measurement provided"):
        session.update_timeseries_resource_info(
            timeseries_key, new_unit_of_measurement=non_existing_unit_of_measurement
        )

    timeseries_resource = session.get_timeseries_resource_info(timeseries_key)
    assert timeseries_resource.unit_of_measurement == original_unit_of_measurement


# pytest -k TestCreatePhysicalTimeseries
@pytest.mark.database
class TestCreatePhysicalTimeseries:
    class TSInitData:
        def __init__(self):
            random_chars = 10

            # Mesh will throw an exception if we try to create a timeseries with an existing path
            # and name. Add a random suffix to the timeseries name to avoid this.
            name_suffix = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=random_chars)
            )

            self.path = "/Path/To/Test/Timeseries/"
            self.name = "Test_Timeseries_" + name_suffix
            self.curve_type = Timeseries.Curve.PIECEWISELINEAR
            self.resolution = Timeseries.Resolution.HOUR
            self.unit_of_measurement = "Unit1"

    @pytest.fixture
    def ts_init_data(self):
        return TestCreatePhysicalTimeseries.TSInitData()

    @staticmethod
    def _verify_timeseries(timeseries: TimeseriesResource, expected_ts_data):
        # Newly created timeseries have "Resource" prepended to their paths, and the timeseries name
        # appended to it.
        expected_path = "Resource" + expected_ts_data.path + expected_ts_data.name

        assert timeseries.path == expected_path
        assert timeseries.name == expected_ts_data.name
        assert timeseries.curve_type == expected_ts_data.curve_type
        assert timeseries.resolution == expected_ts_data.resolution
        assert timeseries.unit_of_measurement == expected_ts_data.unit_of_measurement

    def test_create_physical_timeseries(self, session, ts_init_data):
        """Check that we can create a new physical timeseries."""
        timeseries = session.create_physical_timeseries(
            path=ts_init_data.path,
            name=ts_init_data.name,
            curve_type=ts_init_data.curve_type,
            resolution=ts_init_data.resolution,
            unit_of_measurement=ts_init_data.unit_of_measurement,
        )

        session.commit()

        self._verify_timeseries(timeseries, ts_init_data)

        # TODO: We should also check that the timeseries actually exists in the database. Normally
        # we'd be able to do this by using GetTimeseriesResource; however, that function currently
        # requires us to know the timeseries' key, which CreatePhysicalTimeseries cannot return
        # since it's generated at the commit stage.

    @pytest.mark.asyncio
    async def test_create_physical_timeseries_async(self, async_session, ts_init_data):
        """Check that we can create a new physical timeseries."""
        timeseries = await async_session.create_physical_timeseries(
            path=ts_init_data.path,
            name=ts_init_data.name,
            curve_type=ts_init_data.curve_type,
            resolution=ts_init_data.resolution,
            unit_of_measurement=ts_init_data.unit_of_measurement,
        )

        await async_session.commit()

        self._verify_timeseries(timeseries, ts_init_data)

        # TODO: We should also check that the timeseries actually exists in the database. Normally
        # we'd be able to do this by using GetTimeseriesResource; however, that function currently
        # requires us to know the timeseries' key, which CreatePhysicalTimeseries cannot return
        # since it's generated at the commit stage.

    def test_create_timeseries_with_non_existing_unit_of_measurement(
        self, session, ts_init_data
    ):
        with pytest.raises(ValueError, match="invalid unit of measurement provided"):
            timeseries = session.create_physical_timeseries(
                path=ts_init_data.path,
                name=ts_init_data.name,
                curve_type=ts_init_data.curve_type,
                resolution=ts_init_data.resolution,
                unit_of_measurement=INVALID_UNIT_OF_MEASUREMENT_NAME,
            )


@pytest.mark.asyncio
@pytest.mark.database
async def test_timeseries_resource_async(async_session):
    """For async run the simplest test, implementation is the same."""

    timeseries_key = get_physical_timeseries().timeseries_key
    new_curve_type = Timeseries.Curve.STAIRCASE
    new_unit_of_measurement = "Unit1"

    await async_session.update_timeseries_resource_info(
        timeseries_key, new_curve_type, new_unit_of_measurement
    )
    timeseries_info = await async_session.get_timeseries_resource_info(timeseries_key)
    assert timeseries_info.curve_type == new_curve_type
    assert timeseries_info.unit_of_measurement == new_unit_of_measurement


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
