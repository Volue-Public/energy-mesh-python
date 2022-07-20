"""
Tests for volue.mesh.AttributeBase and volue.mesh.TimeseriesAttribute
"""

import sys
import uuid
from datetime import datetime
from typing import Optional, Tuple, Union

import grpc
import pytest
from dateutil import tz

from volue.mesh import AttributeBase, Timeseries, TimeseriesAttribute

ATTRIBUTE_PATH_PREFIX = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1."


def verify_plant_base_attribute(
    attribute: AttributeBase, name: str, id: uuid.UUID, is_definition: bool
):
    path = ATTRIBUTE_PATH_PREFIX + name

    assert isinstance(attribute, AttributeBase)
    assert attribute.path == path
    assert attribute.name == name
    assert attribute.id == id

    if is_definition:
        assert (
            attribute.definition.path
            == "Repository/SimpleThermalTestRepository/PlantElementType/" + name
        )
        # attribute definition name is the same as attribute name
        assert attribute.definition.name == name
        assert len(attribute.definition.tags) == 0
        assert attribute.definition.namespace == "SimpleThermalTestRepository"
    else:
        assert attribute.definition is None


def verify_plant_raw_timeseries_attribute(
    attribute: Union[AttributeBase, TimeseriesAttribute], is_definition: bool
):
    attribute_name = "TsRawAtt"

    verify_plant_base_attribute(attribute, attribute_name, attribute.id, is_definition)

    assert attribute.time_series_resource.timeseries_key == 0
    assert attribute.time_series_resource.temporary == False
    assert attribute.time_series_resource.curve_type == Timeseries.Curve.PIECEWISELINEAR
    assert attribute.time_series_resource.resolution == Timeseries.Resolution.HOUR
    assert attribute.time_series_resource.unit_of_measurement == "Unit2"
    assert attribute.expression == ""
    assert attribute.is_local_expression == False

    if is_definition:
        assert attribute.definition.description == ""
        assert attribute.definition.value_type == "TimeseriesAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 1
        assert attribute.definition.maximum_cardinality == 1
        assert attribute.definition.template_expression == ""
    else:
        assert attribute.definition is None


def verify_plant_double_attribute(
    attribute: AttributeBase,
    name: str,
    id: uuid.UUID,
    is_definition: bool,
):
    verify_plant_base_attribute(attribute, name, id, is_definition)

    if is_definition:
        assert attribute.definition.description == ""
        assert attribute.definition.value_type == "DoubleAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 1
        assert attribute.definition.maximum_cardinality == 1
        assert attribute.definition.default_value == 1000
        assert attribute.definition.minimum_value == -sys.float_info.max
        assert attribute.definition.maximum_value == sys.float_info.max
        assert attribute.definition.unit_of_measurement is None
    else:
        assert attribute.definition is None

    assert attribute.value == 1000


def verify_time_series_attribute_with_calculation(
    attribute: TimeseriesAttribute,
    attribute_info: Tuple[bool, str, Optional[str]],
    attribute_name: str,
    attribute_id: uuid.UUID,
    is_definition: bool = True,
):
    is_local_expression = attribute_info[0]
    template_expression = attribute_info[1]
    local_expression = attribute_info[2]

    verify_plant_base_attribute(attribute, attribute_name, attribute_id, is_definition)

    assert (
        attribute.expression == local_expression
        if local_expression is not None
        else template_expression
    )
    assert attribute.is_local_expression == is_local_expression

    if is_definition:
        assert attribute.definition.description == ""
        assert attribute.definition.value_type == "TimeseriesAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 1
        assert attribute.definition.maximum_cardinality == 1
        assert attribute.definition.template_expression == template_expression
    else:
        assert attribute.definition is None


def get_targets(session, attribute_name):
    """
    Return all possible targets for attribute APIs, like: ID or path.
    ID is always the first element in the returned target list.
    """
    # ID is auto-generated when creating an attribute, so
    # first we need to read it.
    attribute_path = ATTRIBUTE_PATH_PREFIX + attribute_name
    attribute_id = session.get_attribute(attribute_path).id
    return [attribute_id, attribute_path]


@pytest.mark.database
def test_update_timeseries_attribute_with_expression(session):
    """Check that time series attribute data with an expression can be updated."""

    attribute_name = "TsCalcAtt2"
    new_local_expression = "something"

    # provide all possible attribute target types, like path or ID
    targets = get_targets(session, attribute_name)

    for target in targets:
        original_attribute = session.get_timeseries_attribute(target)
        assert original_attribute.expression != new_local_expression
        assert original_attribute.is_local_expression == False

        session.update_timeseries_attribute(
            target, new_local_expression=new_local_expression
        )

        updated_attribute = session.get_timeseries_attribute(
            target, full_attribute_info=True
        )
        assert updated_attribute.expression == new_local_expression
        assert updated_attribute.definition.template_expression != new_local_expression
        assert updated_attribute.is_local_expression == True

        session.rollback()


@pytest.mark.database
def test_update_timeseries_attribute_with_timeseries_resource(session):
    """
    Check that we can connect time series resource to an existing
    time series attribute.
    """

    attribute_name = "TsRawAtt"
    new_timeseries_resource_key = 2

    targets = get_targets(session, attribute_name)

    for target in targets:
        original_attribute = session.get_timeseries_attribute(target)
        assert original_attribute.time_series_resource is not None
        assert (
            original_attribute.time_series_resource.timeseries_key
            != new_timeseries_resource_key
        )

        session.update_timeseries_attribute(
            target, new_timeseries_resource_key=new_timeseries_resource_key
        )

        updated_attribute = session.get_timeseries_attribute(target)
        assert updated_attribute.time_series_resource is not None
        assert (
            updated_attribute.time_series_resource.timeseries_key
            == new_timeseries_resource_key
        )

        session.rollback()


@pytest.mark.database
def test_update_timeseries_attribute_with_disconnect_timeseries_resource(session):
    """
    Check that we can connect time series resource to an existing
    time series attribute.
    """

    attribute_name = "TsRawAtt"

    targets = get_targets(session, attribute_name)

    for target in targets:
        # first make sure it is connected to some physical time series
        original_attribute = session.get_timeseries_attribute(target)
        assert original_attribute.time_series_resource is not None

        # now let's disconnect it
        session.update_timeseries_attribute(target, new_timeseries_resource_key=0)

        updated_attribute = session.get_timeseries_attribute(target)
        assert updated_attribute.time_series_resource is None

        session.rollback()


@pytest.mark.database
def test_update_timeseries_attribute_with_non_existing_timeseries_key(session):
    """
    Check that 'update_timeseries_attribute' with non existing time series key
    will throw.
    """

    attribute_name = "TsRawAtt"
    non_existing_timeseries_key = 123456

    targets = get_targets(session, attribute_name)

    for target in targets:
        original_time_series_resource = session.get_timeseries_attribute(
            target
        ).time_series_resource

        with pytest.raises(grpc.RpcError):
            session.update_timeseries_attribute(
                target, new_timeseries_resource_key=non_existing_timeseries_key
            )

        attribute = session.get_timeseries_attribute(target)
        assert attribute.time_series_resource == original_time_series_resource


@pytest.mark.database
def test_update_timeseries_attribute_without_parameters_to_update(session):
    """
    Check that 'update_timeseries_attribute' without parameters to update will
    throw.
    """

    attribute_name = "TsRawAtt"

    targets = get_targets(session, attribute_name)

    for target in targets:
        with pytest.raises(grpc.RpcError):
            session.update_timeseries_attribute(target)


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_search_timeseries_attribute(session, full_attribute_info):
    """Check that time series attribute data can be searched for."""

    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    start_object_id = uuid.UUID("0000000B-0001-0000-0000-000000000000")
    query = "{*}.TsRawAtt"

    targets = [start_object_path, start_object_id]

    for target in targets:
        timeseries_attributes = session.search_for_timeseries_attributes(
            target, query, full_attribute_info
        )

        assert len(timeseries_attributes) == 3
        assert all(
            isinstance(attr, TimeseriesAttribute) for attr in timeseries_attributes
        )

        # take one and verify
        some_power_plant_ts_attr_path = ATTRIBUTE_PATH_PREFIX + "TsRawAtt"
        some_power_plant_ts_attr = next(
            attr
            for attr in timeseries_attributes
            if attr.path == some_power_plant_ts_attr_path
        )
        verify_plant_raw_timeseries_attribute(
            some_power_plant_ts_attr, full_attribute_info
        )


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_bool_array_attribute(session, full_attribute_info):
    """
    Check that 'get_attribute' with full attribute view retrieves a boolean array attribute and its definition.
    """
    attribute_name = "BoolArrayAtt"
    bool_array_values = [False, True, False, True, False]

    targets = get_targets(session, attribute_name)
    attribute_id = targets[0]

    for target in targets:
        attribute = session.get_attribute(target, full_attribute_info)
        verify_plant_base_attribute(
            attribute, attribute_name, attribute_id, full_attribute_info
        )

        if full_attribute_info:
            assert attribute.definition.description == "Array of bools"
            assert attribute.definition.value_type == "BooleanArrayAttributeDefinition"
            assert attribute.definition.minimum_cardinality == 0
            assert attribute.definition.maximum_cardinality == 10
        else:
            assert attribute.definition is None

        for values in zip(attribute.value, bool_array_values):
            assert values[0] == values[1]


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_xy_set_attribute(session, full_attribute_info):
    """
    Check that 'get_attribute' with full attribute view retrieves a XY set attribute and its definition.
    """
    attribute_name = "XYSetAtt"

    targets = get_targets(session, attribute_name)
    attribute_id = targets[0]

    for target in targets:
        attribute = session.get_attribute(target, full_attribute_info)
        verify_plant_base_attribute(
            attribute, attribute_name, attribute_id, full_attribute_info
        )

        if full_attribute_info:
            assert attribute.definition.description == ""
            assert attribute.definition.value_type == "XYSetAttributeDefinition"
            assert attribute.definition.minimum_cardinality == 1
            assert attribute.definition.maximum_cardinality == 1
        else:
            assert attribute.definition is None

        # XY set attribute does not have a value read via get_attribute


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_utc_time_attribute(session, full_attribute_info):
    """
    Check that 'get_attribute' with full attribute view retrieves a UtcDateTime attribute and its definition.
    """
    attribute_name = "UtcDateTimeAtt"
    # your UtcDateTimeAtt in SimpleThermalModel should be populated with this value
    utc_time_value = datetime(2022, 5, 10, 7, 24, 15, tzinfo=tz.UTC)

    targets = get_targets(session, attribute_name)
    attribute_id = targets[0]

    for target in targets:
        attribute = session.get_attribute(target, full_attribute_info)
        verify_plant_base_attribute(
            attribute, attribute_name, attribute_id, full_attribute_info
        )

        if full_attribute_info:
            assert attribute.definition.description == ""
            assert attribute.definition.value_type == "UtcDateTimeAttributeDefinition"
            assert attribute.definition.minimum_cardinality == 1
            assert attribute.definition.maximum_cardinality == 1
            assert attribute.definition.default_value == "UTC20220510072415"
            assert attribute.definition.minimum_value == None
            assert attribute.definition.maximum_value == None
        else:
            assert attribute.definition is None

        assert attribute.value == utc_time_value


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_boolean_attribute(session, full_attribute_info):
    """
    Check that 'get_attribute' with full attribute view retrieves a boolean attribute and its definition.
    """
    attribute_name = "BoolAtt"

    targets = get_targets(session, attribute_name)
    attribute_id = targets[0]

    for target in targets:
        attribute = session.get_attribute(target, full_attribute_info)
        verify_plant_base_attribute(
            attribute, attribute_name, attribute_id, full_attribute_info
        )

        if full_attribute_info:
            assert attribute.definition.description == ""
            assert attribute.definition.value_type == "BooleanAttributeDefinition"
            assert attribute.definition.minimum_cardinality == 1
            assert attribute.definition.maximum_cardinality == 1
            assert attribute.definition.default_value == True
        else:
            assert attribute.definition is None

        assert attribute.value == True


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_string_attribute(session, full_attribute_info):
    """
    Check that 'get_attribute' with full attribute view retrieves a string attribute and its definition.
    """
    attribute_name = "StringAtt"
    default_string_value = "Default string value"

    targets = get_targets(session, attribute_name)
    attribute_id = targets[0]

    for target in targets:
        attribute = session.get_attribute(target, full_attribute_info)
        verify_plant_base_attribute(
            attribute, attribute_name, attribute_id, full_attribute_info
        )

        if full_attribute_info:
            assert attribute.definition.description == ""
            assert attribute.definition.value_type == "StringAttributeDefinition"
            assert attribute.definition.minimum_cardinality == 1
            assert attribute.definition.maximum_cardinality == 1
            assert attribute.definition.default_value == default_string_value
        else:
            assert attribute.definition is None

        assert attribute.value == default_string_value


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_double_attribute(session, full_attribute_info):
    """
    Check that 'get_attribute' with full attribute view retrieves a double attribute and its definition.
    """
    attribute_name = "DblAtt"

    targets = get_targets(session, attribute_name)
    attribute_id = targets[0]

    for target in targets:
        attribute = session.get_attribute(target, full_attribute_info)
        verify_plant_double_attribute(
            attribute, attribute_name, attribute_id, full_attribute_info
        )


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_rating_curve_attribute(session, full_attribute_info):
    """
    Check that 'get_attribute' with full attribute view retrieves a rating curve attribute.
    """
    attribute_name = "RatingCurveAtt"

    # provide attribute by path and ID
    targets = get_targets(session, attribute_name)
    attribute_id = targets[0]

    for target in targets:
        attribute = session.get_attribute(target, full_attribute_info)
        verify_plant_base_attribute(
            attribute, attribute_name, attribute_id, full_attribute_info
        )

        if full_attribute_info:
            assert attribute.definition.description == ""
            assert attribute.definition.value_type == "RatingCurveAttributeDefinition"
            assert attribute.definition.minimum_cardinality == 1
            assert attribute.definition.maximum_cardinality == 1
        else:
            assert attribute.definition is None

        # rating curve attribute does not have a value read via get_attribute


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_time_series_attribute_with_calculation(session, full_attribute_info):
    """
    Check that 'get_attribute' with full attribute view retrieves a time series
    attribute with a calculation and its definition.
    """
    attribute_name = "TsCalcAtt2"
    template_expression = "##= @SUM(@T('ReferenceSeriesCollectionAtt.TsRawAtt'))\n\n"
    is_local_expression = False

    targets = get_targets(session, attribute_name)
    attribute_id = targets[0]

    for target in targets:
        base_attribute = session.get_attribute(target, full_attribute_info)
        timeseries_attribute = session.get_timeseries_attribute(
            target, full_attribute_info
        )

        assert isinstance(base_attribute, AttributeBase)
        assert isinstance(timeseries_attribute, TimeseriesAttribute)

        for attribute in [base_attribute, timeseries_attribute]:
            verify_time_series_attribute_with_calculation(
                attribute,
                (is_local_expression, template_expression, None),
                attribute_name,
                attribute_id,
                full_attribute_info,
            )


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_get_time_series_attribute_with_time_series_resource(
    session, full_attribute_info
):
    """
    Check that 'get_attribute' with full attribute view retrieves a time series
    attribute with a connected time series resource and its definition.
    """
    attribute_name = "TsRawAtt"

    targets = get_targets(session, attribute_name)

    for target in targets:
        base_attribute = session.get_attribute(target, full_attribute_info)
        timeseries_attribute = session.get_timeseries_attribute(
            target, full_attribute_info
        )

        assert isinstance(base_attribute, AttributeBase)
        assert isinstance(timeseries_attribute, TimeseriesAttribute)

        for attribute in [base_attribute, timeseries_attribute]:
            verify_plant_raw_timeseries_attribute(attribute, full_attribute_info)


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_search_multiple_attributes(session, full_attribute_info):
    """
    Check that 'search_for_attributes' with full attribute view retrieves
    requested attributes and their definitions.
    """
    start_object_path = "Model/SimpleThermalTestModel"

    # requested attributes
    attributes_names = ["TsCalcAtt", "TsCalcAtt2", "TsCalcAtt4", "TsCalcAtt7"]
    # holds an expression and information about its expression locality
    # [is_local, template_expression, local_expression]
    attributes_info = {
        # TsCalcAtt has local expression which is the same as its template expression
        attributes_names[0]: (
            True,
            "@PDLOG(12004, 'TEST') \n##= @d('.DblAtt') + @t('.TsRawAtt') + @SUM(@D('PlantToPlantRef.DblAtt'))\n\n",
            "@PDLOG(12004, 'TEST') \n##= @d('.DblAtt') + @t('.TsRawAtt') + @SUM(@D('PlantToPlantRef.DblAtt'))\n\n",
        ),
        attributes_names[1]: (
            False,
            "##= @SUM(@T('ReferenceSeriesCollectionAtt.TsRawAtt'))\n\n",
            None,
        ),
        attributes_names[2]: (
            False,
            "temp=@t('.TsRawAtt')\ngt2 = @ABS(temp) > 2\n## = temp - 1000\nIF (gt2) THEN\n## = temp + 1000\nENDIF\n",
            None,
        ),
        attributes_names[3]: (
            False,
            "##=@Restriction('ProductionMin[MW]', 'Proposed|Recommended', @t('.TsRawAtt'), 'Minimum')\n",
            None,
        ),
    }

    query = "*[.Name=SomePowerPlant1]." + ",".join(attributes_names)
    attributes = session.search_for_attributes(
        start_object_path, query, full_attribute_info
    )

    assert len(attributes) == len(attributes_names)

    for attribute in attributes:
        assert attribute.name in attributes_names
        assert isinstance(attribute, AttributeBase)

        attribute_id = session.get_attribute(attribute.path).id

        verify_time_series_attribute_with_calculation(
            attribute,
            attributes_info[attribute.name],
            attribute.name,
            attribute_id,
            full_attribute_info,
        )


@pytest.mark.database
@pytest.mark.parametrize("full_attribute_info", [False, True])
def test_search_with_absent_attribute(session, full_attribute_info):
    """
    Check that 'search_for_attributes' with query containing absent attribute will return all of the existing attributes.
    """
    start_object_path = "Model/SimpleThermalTestModel"

    # requested attributes, one doesn't exist
    attributes_names = ["DblAtt", "ABSENT_ATTRIBUTE_NAME"]
    query = "*[.Name=SomePowerPlant1]." + ",".join(attributes_names)

    attributes = session.search_for_attributes(
        start_object_path, query, full_attribute_info
    )

    assert len(attributes) == 1
    # ID is checked in other tests provide here ID from the attribute itself
    verify_plant_double_attribute(
        attributes[0], attributes_names[0], attributes[0].id, full_attribute_info
    )


@pytest.mark.database
@pytest.mark.parametrize(
    "attribute_name, new_value",
    [
        ("DblAtt", 5.0),
        ("DblAtt", 13),
        ("Int64Att", 70),
        ("BoolAtt", False),
        ("StringAtt", "my test string attribute value"),
        ("UtcDateTimeAtt", datetime(2022, 5, 14, 13, 44, 45, 0, tzinfo=tz.UTC)),
        ("BoolArrayAtt", [False, False, True, False, False]),
    ],
)
def test_update_simple_attribute(session, attribute_name, new_value):
    targets = get_targets(session, attribute_name)

    for target in targets:
        original_attribute = session.get_attribute(target)
        assert original_attribute.value != new_value

        session.update_simple_attribute(target, new_value)

        updated_attribute = session.get_attribute(target)
        assert updated_attribute.value == new_value

        session.rollback()


@pytest.mark.database
def test_update_simple_attribute_invalid_request(session):
    """
    Check that 'update_simple_attribute' with invalid request
    (e.g.: wrong value type and dimension) will throw.
    """

    # boolean array attribute, wrong value type and dimension
    targets = get_targets(session, "BoolArrayAtt")

    for target in targets:
        original_values = session.get_attribute(target).value

        with pytest.raises(grpc.RpcError):
            session.update_simple_attribute(target, value=7)

        attribute = session.get_attribute(target)
        assert attribute.value == original_values


@pytest.mark.database
@pytest.mark.parametrize(
    "invalid_target",
    [
        "Model/SimpleThermalTestModel/ThermalComponent/SomePowerPlant1",
        uuid.UUID("0000000A-0001-0000-0000-000000000000"),
        "Model/SimpleThermalTestModel/ThermalComponent",
        uuid.UUID("0000000B-0001-0000-0000-000000000000"),
        "non_existing_path",
        uuid.uuid4(),
    ],
)
def test_get_update_attribute_with_invalid_target(session, invalid_target):
    """
    Check that 'get_timeseries_attribute', 'update_timeseries_attribute',
    'get_attribute' and 'update_simple_attribute' with invalid target
    (meaning incorrect attribute path or ID) will throw.
    """
    with pytest.raises(grpc.RpcError):
        session.get_timeseries_attribute(invalid_target)
    with pytest.raises(grpc.RpcError):
        session.update_timeseries_attribute(invalid_target, new_local_expression="test")
    with pytest.raises(grpc.RpcError):
        session.get_attribute(invalid_target)
    with pytest.raises(grpc.RpcError):
        session.update_simple_attribute(invalid_target, value="test")


@pytest.mark.database
@pytest.mark.parametrize(
    "invalid_target",
    [
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef",
        "non_existing_path",
        uuid.uuid4(),
    ],
)
def test_search_for_attributes_with_invalid_target(session, invalid_target):
    """
    Check that 'search_for_timeseries_attributes' and 'search_for_attributes'
    with invalid target (meaning incorrect start object path or ID) will throw.
    """
    query = "{*}.TsCalcAtt"

    with pytest.raises(grpc.RpcError):
        session.search_for_timeseries_attributes(invalid_target, query)
    with pytest.raises(grpc.RpcError):
        session.search_for_attributes(invalid_target, query)


@pytest.mark.asyncio
@pytest.mark.database
async def test_timeseries_attributes_async(async_session):
    """
    For TimeseriesAttribute async run the simplest test, implementation is
    the same.
    """

    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    query = "{*}.TsCalcAtt"
    new_local_expression = "some expression"

    timeseries_attributes = await async_session.search_for_timeseries_attributes(
        start_object_path, query
    )
    assert len(timeseries_attributes) == 3
    assert all(isinstance(attr, TimeseriesAttribute) for attr in timeseries_attributes)

    await async_session.update_timeseries_attribute(
        timeseries_attributes[0].path, new_local_expression=new_local_expression
    )
    updated_timeseries_attribute = await async_session.get_attribute(
        timeseries_attributes[0].path
    )
    assert isinstance(updated_timeseries_attribute, TimeseriesAttribute)
    assert updated_timeseries_attribute.expression == new_local_expression


@pytest.mark.asyncio
@pytest.mark.database
async def test_attributes_async(async_session):
    """
    For AttributeBase async run the simplest test, implementation is
    the same.
    """

    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
    query = "{*}.DblAtt"
    new_value = 3

    attributes = await async_session.search_for_attributes(start_object_path, query)
    assert len(attributes) == 3
    assert all(isinstance(attr, AttributeBase) for attr in attributes)

    await async_session.update_simple_attribute(attributes[0].path, new_value)
    updated_attribute = await async_session.get_attribute(attributes[0].path)

    assert isinstance(updated_attribute, AttributeBase)
    assert updated_attribute.value == new_value


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
