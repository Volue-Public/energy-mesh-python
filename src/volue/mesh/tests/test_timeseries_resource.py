"""
Tests for volue.mesh.TimeseriesResource
"""

import sys

import grpc
import pytest

from volue.mesh import Timeseries, TimeseriesResource


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
    non_existing_unit_of_measurement = "no_such_unit"

    original_unit_of_measurement = session.get_timeseries_resource_info(
        timeseries_key
    ).unit_of_measurement

    with pytest.raises(ValueError, match="invalid unit of measurement provided"):
        session.update_timeseries_resource_info(
            timeseries_key, new_unit_of_measurement=non_existing_unit_of_measurement
        )

    timeseries_resource = session.get_timeseries_resource_info(timeseries_key)
    assert timeseries_resource.unit_of_measurement == original_unit_of_measurement


def test_create_physical_timeseries(session):
    """Check that we can create a new physical timeseries."""
    PATH = '/Path/To/Test/Timeseries/',
    NAME = 'Test_Timeseries',
    CURVE_TYPE = Timeseries.Curve.PIECEWISELINEAR,
    RESOLUTION = Timeseries.Resolution.HOUR,
    UNIT_OF_MEASUREMENT = 'Unit1'

    timeseries_resource = session.create_physical_timeseries(
        path=PATH,
        name=NAME,
        curve_type=CURVE_TYPE,
        resolution=RESOLUTION,
        unit_of_measurement=UNIT_OF_MEASUREMENT
    )

    assert timeseries.resource.path == PATH
    assert timeseries.resource.name == NAME
    assert timeseries.resource.curve_type == CURVE_TYPE
    assert timeseries.resource.resolution == RESOLUTION
    assert timeseries.resource.unit_of_measurement == UNIT_OF_MEASUREMENT

    # """Check that time series resource can be updated."""
    # session.update_timeseries_resource_info(
    #     timeseries_key, new_curve_type, new_unit_of_measurement
    # )
    # timeseries_info = session.get_timeseries_resource_info(timeseries_key)

    # if new_curve_type is not None:
    #     assert timeseries_info.curve_type == new_curve_type
    # if new_unit_of_measurement is not None:
    #     assert timeseries_info.unit_of_measurement == new_unit_of_measurement


# //  --gtest_filter=CreatePhysicalTimeseriesTests.SendRequestAndCommitShouldPass
# TEST_F(CreatePhysicalTimeseriesTests, SendRequestAndCommitShouldPass) {
#     const auto& create_ts_request = CreateRequest();
#     const auto& create_ts_response = Api::CreatePhysicalTimeseries(context_, create_ts_request);
#     Api::Commit(context_, proto_session_id_);

#     VerifyResponse(create_ts_response);
# }

# //  --gtest_filter=CreatePhysicalTimeseriesTests.CreateExistingTimeseriesShouldThrow
# TEST_F(CreatePhysicalTimeseriesTests, CreateExistingTimeseriesShouldThrow) {
#     const auto& create_ts_request = CreateRequest();

#     const auto& send_request = [&]() -> TimeseriesResource {
#         return Api::CreatePhysicalTimeseries(context_, create_ts_request);
#     };

#     // Create the timeseries.
#     const auto& create_ts_response = send_request();

#     Api::Commit(context_, proto_session_id_);

#     VerifyResponse(create_ts_response);

#     const auto& msg =
#         fmt::format("An element named {} already exists in the Timeseries resource catalog\n", name_);

#     // Now try to create it again.
#     EXPECT_THAT(send_request, ThrowsMessage<std::exception>(StrEq(msg)));
# }

# //  --gtest_filter=CreatePhysicalTimeseriesTests.InvalidPathShouldThrow
# TEST_F(CreatePhysicalTimeseriesTests, InvalidPathShouldThrow) {
#     // The path string must begin and end with slashes.
#     TestInvalidPath("Path/To/Test/Timeseries");
#     TestInvalidPath("Path/To/Test/Timeseries/");
#     TestInvalidPath("/Path/To/Test/Timeseries");
# }

# //  --gtest_filter=CreatePhysicalTimeseriesTests.MissingFieldsShouldThrow
# TEST_F(CreatePhysicalTimeseriesTests, MissingFieldsShouldThrow) {
#     // Can't use auto here since it's deduced to different lambda types.
#     std::function clear_field = [&](CreatePhysicalTimeseriesRequest& create_ts_request) {
#         create_ts_request.clear_curve_type();
#     };

#     TestMissingField(clear_field);

#     clear_field = [&](CreatePhysicalTimeseriesRequest& create_ts_request) {
#         create_ts_request.clear_resolution();
#     };

#     TestMissingField(clear_field);

#     clear_field = [&](CreatePhysicalTimeseriesRequest& create_ts_request) {
#         create_ts_request.clear_unit_of_measurement_id();
#     };

#     TestMissingField(clear_field);
# }

# //  --gtest_filter=CreatePhysicalTimeseriesTests.InvalidUnitOfMeasurementIdShouldThrow
# TEST_F(CreatePhysicalTimeseriesTests, InvalidUnitOfMeasurementIdShouldThrow) {
#     unit_of_measurement_id_ = Common::Guid::Empty();

#     const auto& create_ts_request = CreateRequest();

#     EXPECT_THROW(Api::CreatePhysicalTimeseries(context_, create_ts_request), std::invalid_argument);
# }


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
