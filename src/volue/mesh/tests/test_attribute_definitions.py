"""
Tests for attribute definition operations.
"""

import grpc
import pytest

ATTRIBUTE_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.TsCalcAtt2"


@pytest.mark.database
def test_update_timeseries_attribute_definition_with_template_expression_by_id(session):
    """Check that time series attribute definition template expression can be updated using ID."""

    new_template_expression = "##= @t('ReferenceSeriesAtt.TsRawAtt') + 100\n\n"

    # Get the attribute to access its definition
    attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    original_template_expression = attribute.definition.template_expression

    # Update the template expression using definition ID
    session.update_timeseries_attribute_definition(
        attribute.definition.id, new_template_expression=new_template_expression
    )

    # Verify the template expression was updated
    updated_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert updated_attribute.definition.template_expression == new_template_expression

    # Rollback to restore the original state
    session.rollback()

    # Verify rollback restored the original expression
    restored_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert (
        restored_attribute.definition.template_expression
        == original_template_expression
    )


@pytest.mark.database
def test_update_timeseries_attribute_definition_with_template_expression_by_path(
    session,
):
    """Check that time series attribute definition template expression can be updated using path."""

    new_template_expression = "##= @t('ReferenceSeriesAtt.TsRawAtt') + 200\n\n"

    # Get the attribute to access its definition
    attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )

    # Update the template expression using definition path
    session.update_timeseries_attribute_definition(
        attribute.definition.path, new_template_expression=new_template_expression
    )

    # Verify the template expression was updated
    updated_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert updated_attribute.definition.template_expression == new_template_expression


@pytest.mark.database
def test_update_timeseries_attribute_definition_with_template_expression_by_object(
    session,
):
    """Check that time series attribute definition template expression can be updated using definition object."""

    new_template_expression = "##= @t('ReferenceSeriesAtt.TsRawAtt') + 300\n\n"

    # Get the attribute to access its definition
    attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )

    # Update the template expression using definition object
    session.update_timeseries_attribute_definition(
        attribute.definition, new_template_expression=new_template_expression
    )

    # Verify the template expression was updated
    updated_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert updated_attribute.definition.template_expression == new_template_expression


@pytest.mark.database
def test_update_timeseries_attribute_definition_with_description(session):
    """Check that time series attribute definition description can be updated."""

    new_description = "Updated description for testing"

    # Get the attribute to access its definition
    attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    original_description = attribute.definition.description

    # Update the description
    session.update_timeseries_attribute_definition(
        attribute.definition, new_description=new_description
    )

    # Verify the description was updated
    updated_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert updated_attribute.definition.description == new_description

    session.rollback()

    # Verify rollback restored the original description
    restored_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert restored_attribute.definition.description == original_description


@pytest.mark.database
def test_update_timeseries_attribute_definition_both_fields(session):
    """Check that both template expression and description can be updated together."""

    new_template_expression = "##= @t('ReferenceSeriesAtt.TsRawAtt')) + 777\n\n"
    new_description = "Updated description and expression"

    # Get the attribute to access its definition
    attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )

    # Update both fields
    session.update_timeseries_attribute_definition(
        attribute.definition,
        new_template_expression=new_template_expression,
        new_description=new_description,
    )

    # Verify both fields were updated
    updated_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )

    assert updated_attribute.definition.template_expression == new_template_expression
    assert updated_attribute.definition.description == new_description


@pytest.mark.database
def test_update_timeseries_attribute_definition_without_parameters_to_update(session):
    """Check that updating without parameters raises an error."""

    attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )

    with pytest.raises(grpc.RpcError, match="nothing is set to be updated"):
        session.update_timeseries_attribute_definition(attribute.definition)


@pytest.mark.database
def test_local_expression_takes_precedence_over_template_expression(session):
    """Check that a local expression on an attribute takes precedence over the template expression."""

    template_expression = "##= @t('ReferenceSeriesAtt.TsRawAtt') + 1000\n\n"
    local_expression = "##= @t('ReferenceSeriesAtt.TsRawAtt') + 2000\n\n"

    # Get the attribute to access its definition
    attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    original_template_expression = attribute.definition.template_expression
    original_local_expression = (
        attribute.expression if attribute.is_local_expression else None
    )

    # First, update the template expression
    session.update_timeseries_attribute_definition(
        attribute.definition, new_template_expression=template_expression
    )

    # Verify the template expression is set and being used (no local expression yet)
    updated_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert updated_attribute.definition.template_expression == template_expression
    assert updated_attribute.expression == template_expression
    assert not updated_attribute.is_local_expression

    # Now set a local expression on the same attribute
    session.update_timeseries_attribute(
        ATTRIBUTE_PATH, new_local_expression=local_expression
    )

    # Verify the local expression takes precedence over the template expression
    final_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert final_attribute.definition.template_expression == template_expression
    assert final_attribute.expression == local_expression
    assert final_attribute.is_local_expression
    # The expression being used should be the local one, not the template
    assert final_attribute.expression != final_attribute.definition.template_expression

    # Rollback to restore the original state
    session.rollback()

    # Verify rollback restored the original expressions
    restored_attribute = session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert (
        restored_attribute.definition.template_expression
        == original_template_expression
    )
    if original_local_expression:
        assert restored_attribute.expression == original_local_expression
        assert restored_attribute.is_local_expression
    else:
        assert not restored_attribute.is_local_expression


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_timeseries_attribute_definition_with_template_expression_async(
    async_session,
):
    """Check that time series attribute definition template expression can be updated using async session."""

    new_template_expression = "##= @t('ReferenceSeriesAtt.TsRawAtt') + 500\n\n"

    # Get the attribute to access its definition
    attribute = await async_session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    original_template_expression = attribute.definition.template_expression

    # Update the template expression using definition object
    await async_session.update_timeseries_attribute_definition(
        attribute.definition, new_template_expression=new_template_expression
    )

    # Verify the template expression was updated
    updated_attribute = await async_session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert updated_attribute.definition.template_expression == new_template_expression

    # Rollback to restore the original state
    await async_session.rollback()

    # Verify rollback restored the original expression
    restored_attribute = await async_session.get_timeseries_attribute(
        ATTRIBUTE_PATH, full_attribute_info=True
    )
    assert (
        restored_attribute.definition.template_expression
        == original_template_expression
    )
