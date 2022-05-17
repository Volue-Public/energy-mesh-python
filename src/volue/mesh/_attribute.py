"""
Functionality for working with Mesh attributes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Type, TypeVar
import uuid

from google.protobuf import timestamp_pb2

from volue.mesh._common import _from_proto_guid
from volue.mesh.proto.core.v1alpha import core_pb2

S = TypeVar('S', int, float, bool, str, datetime)

PROTO_VALUE_ONE_OF_FIELD_NAME = 'value_oneof'
PROTO_DEFINITION_ONE_OF_FIELD_NAME = 'definition_type_oneof'

def _get_field_value(field_name: str, field_names: set[str], proto_message: Any):
    """
    Check if a field exists in a given proto message.
    If it exists then read its value. Return `None` otherwise.
    """
    if field_name in field_names:
        return getattr(proto_message, field_name)
    else:
        return None

def _get_attribute_value(proto_attribute_value: core_pb2.AttributeValue):
    """Reads attribute value from proto message and coverts to Python type."""

    proto_value = getattr(proto_attribute_value, proto_attribute_value.WhichOneof(
        PROTO_VALUE_ONE_OF_FIELD_NAME))

    if type(proto_value) is timestamp_pb2.Timestamp:
        proto_value = proto_value.ToDatetime()

    return proto_value


def _from_proto_attribute(proto_attribute: core_pb2.Attribute) -> Type[AttributeBase]:
    """Factory for creating attributes from protobuf Mesh Attribute.

    Args:
        proto_attribute (core_pb2.Attribute): protobuf Attribute returned from the gRPC methods.
    """
    attribute_value_type = None
    attribute_definition_type = None

    # check if this is a singular attribute or a collection
    if proto_attribute.HasField('singular_value'):
        attribute_value_type = proto_attribute.singular_value.WhichOneof(
            PROTO_VALUE_ONE_OF_FIELD_NAME)
    elif len(proto_attribute.collection_values) > 0:
        for collection_value in proto_attribute.collection_values:
            attribute_value_type = collection_value.WhichOneof(
                PROTO_VALUE_ONE_OF_FIELD_NAME)
            break

    if proto_attribute.HasField('definition'):
        attribute_definition_type = proto_attribute.definition.WhichOneof(
            PROTO_DEFINITION_ONE_OF_FIELD_NAME)

    if attribute_value_type == 'timeseries_value':
        attribute = TimeseriesAttribute._from_proto_attribute(proto_attribute)
    # Relationship attribute is a bit special.
    # It does not have a value, only definition.
    # It will be treated as generic AttributeBase if
    # definition is not a part of the proto message.
    elif attribute_value_type is None and attribute_definition_type == "relationship_definition":
        attribute = RelationshipAttribute._from_proto_attribute(proto_attribute)
    elif attribute_value_type is None:
        attribute = AttributeBase._from_proto_attribute(proto_attribute)
    else:
        attribute = SimpleAttribute._from_proto_attribute(proto_attribute)

    return attribute


@dataclass
class AttributeBase:
    """Base class for Mesh Attribute.

    Represents common information for all kinds of attributes.
    Mesh Attribute is an instance of Attribute Definition in the
    Mesh Model and has always an owner of Object type.
    It has some type (e.g. DoubleAttribute or BoolCollectionAttribute).
    """

    id: uuid = None
    path: str = None
    name: str = None
    definition_id: uuid = None
    definition_path: str = None
    definition_name: str = None
    description: str = None
    tags: List[str] = field(default_factory=list)
    namespace: str = None
    value_type: str = None
    minimum_cardinality: int = None
    maximum_cardinality: int = None

    @classmethod
    def _from_proto_attribute(cls, proto_attribute: core_pb2.Attribute):
        """Create an `AttributeBase` from protobuf Mesh Attribute.

        Args:
            proto_attribute (core_pb2.Attribute): protobuf Attribute returned from the gRPC methods.
        """
        attribute = cls()
        attribute._init_from_proto_attribute(proto_attribute)
        return attribute


    def _init_from_proto_attribute(self, proto_attribute: core_pb2.Attribute):
        """Initialize an `Attribute` from protobuf Mesh Attribute.

        Args:
            proto_attribute (core_pb2.Attribute): protobuf Attribute returned from the gRPC methods.
        """
        attribute = self
        attribute.id = _from_proto_guid(proto_attribute.id)
        attribute.path = proto_attribute.path
        attribute.name = proto_attribute.name

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField('definition'):
            attribute.definition_id = _from_proto_guid(proto_attribute.definition.id)
            attribute.definition_path = proto_attribute.definition.path
            attribute.definition_name = proto_attribute.definition.name
            attribute.description = proto_attribute.definition.description
            for tag in proto_attribute.definition.tags:
                attribute.tags.append(tag)
            attribute.namespace = proto_attribute.definition.name_space
            attribute.value_type = proto_attribute.definition.value_type
            attribute.minimum_cardinality = proto_attribute.definition.minimum_cardinality
            attribute.maximum_cardinality = proto_attribute.definition.maximum_cardinality

        return attribute

    def _get_string_representation(self) -> str:
        """Get string representation that could be used by subclasses `_str__` method calls."""
        return (
            f"name: {self.name}\n"
            f"\t id: {self.id}\n"
            f"\t path: {self.id}\n"
            f"\t id: {self.definition_id}\n"
            f"\t path: {self.definition_path}\n"
            f"\t name: {self.definition_name}\n"
            f"\t description: {self.description}\n"
            f"\t tags: {self.tags}\n"
            f"\t namespace: {self.namespace}\n"
            f"\t value_type: {self.value_type}\n"
            f"\t minimum_cardinality: {self.minimum_cardinality}\n"
            f"\t maximum_cardinality: {self.maximum_cardinality}"
        )

    def __str__(self) -> str:
        return (
            f"AttributeBase:\n"
            f"\t {self._get_string_representation()}"
        )


@dataclass
class SimpleAttribute(AttributeBase):
    """Represents simple Mesh Attributes.

    A simple attribute means an attribute that is defined by a single value
    or a collection of single values.

    The value can be of the following type (`value_type` is provided in the parenthesis):
    - integer (Int64AttributeDefinition)
    - collection of integers (Int64ArrayAttributeDefinition)
    - double (DoubleAttributeDefinition)
    - collection of doubles (DoubleArrayAttributeDefinition)
    - boolean (BooleanAttributeDefinition)
    - collection of booleans (BooleanArrayAttributeDefinition)
    - string (StringAttributeDefinition) or collection of strings (StringArrayAttributeDefinition)
    - datetime (UtcDateTimeAttributeDefinition) or collection of datetimes (UtcDateTimeArrayAttributeDefinition)

    Types: integer (single or collection) and double (single or collection)
    may have additionally the following fields defined:
    - minimum_value
    - maximum_value
    - unit_of_measurement
    """

    value: S = None
 
    default_value: S = None
    minimum_value: S = None
    maximum_value: S = None
    unit_of_measurement: str = None

    @classmethod
    def _from_proto_attribute(cls, proto_attribute: core_pb2.Attribute):
        """Create a `SimpleAttribute` from protobuf Mesh Attribute.

        Args:
            proto_attribute (core_pb2.Attribute): protobuf Attribute returned from the gRPC methods.
        """
        attribute = cls()
        super()._init_from_proto_attribute(attribute, proto_attribute)

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField('definition'):
            # get field name of specific definition type from oneof
            definition_type_name = proto_attribute.definition.WhichOneof(
                PROTO_DEFINITION_ONE_OF_FIELD_NAME)
            # get the proto message
            definition_type = getattr(proto_attribute.definition, definition_type_name)
            # read all of the available proto fields
            field_names = set([field.name for field, _ in definition_type.ListFields()])

            # set all possible values
            # if a field does not exist for the given definition type then return `None`
            attribute.default_value = _get_field_value(
                'default_value', field_names, definition_type)
            attribute.minimum_value = _get_field_value(
                'minimum_value', field_names, definition_type)
            attribute.maximum_value = _get_field_value(
                'maximum_value', field_names, definition_type)
            attribute.unit_of_measurement = _get_field_value(
                'unit_of_measurement', field_names, definition_type)

        if proto_attribute.HasField('singular_value'):
            attribute.value = _get_attribute_value(proto_attribute.singular_value)
        elif len(proto_attribute.collection_values) > 0:
            attribute.value = []
            for value in proto_attribute.collection_values:
                attribute.value.append(_get_attribute_value(value))

        return attribute

    def __str__(self) -> str:
        base_message = super()._get_string_representation()
        return (
            f"SimpleAttribute:\n"
            f"\t {base_message}\n"
            f"\t value: {self.value}\n"
            f"\t default_value: {self.default_value}\n"
            f"\t minimum_value: {self.minimum_value}\n"
            f"\t maximum_value: {self.maximum_value}\n"
            f"\t unit_of_measurement: {self.unit_of_measurement}"
        )


@dataclass
class RelationshipAttribute(AttributeBase):
    """Represents relationship Mesh Attribute.

    Relationship attributes connects two objects.
    The owned object's owner is always a relationship attribute that
    belongs to some other object.

    There are two types of relationship attributes (`value_type` is provided in the parenthesis):
    - one-to-one (ElementAttributeDefinition)
    - one-to-many (ElementCollectionAttributeDefinition)

    When creating a new object the owner must be a relationship attribute
    of one-to-many type (ElementCollectionAttributeDefinition).
    """
    object_type: str = None

    @classmethod
    def _from_proto_attribute(cls, proto_attribute: core_pb2.Attribute):
        """Create a `RelationshipAttribute` from protobuf Mesh Attribute.

        Args:
            proto_attribute (core_pb2.Attribute): protobuf Attribute returned from the gRPC methods.
        """
        attribute = cls()
        super()._init_from_proto_attribute(attribute, proto_attribute)

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField('definition'):
            attribute.object_type = proto_attribute.definition.relationship_definition.object_type

        return attribute

    def __str__(self) -> str:
        base_message = super()._get_string_representation()
        return (
            f"RelationshipAttribute:\n"
            f"\t {base_message}\n"
            f"\t object_type: {self.object_type}"
        )


@dataclass
class TimeseriesAttribute(AttributeBase):
    """Represents time series Mesh Attribute.

    Time series attribute can be a:
    - reference to a physical time series: it has actual data (timestamps, values and flags)
        and meta data (e.g.: curve type, resolution, etc.).
    - reference to a virtual time series: it has defined an expression to calculate
        time series data (similar to calculation time series).
    - calculation time series: it has defined an expression to calculate
        time series data. The calculation expression can be defined on Attribute Definition
        level (`template_expression`) or overwritten for the given attribute (if it is then
        `is_local_expression` is set to True).

    Note: physical and virtual time series are both called resource time series.
    """
    resource_time_series_id: uuid = None
    resource_time_series_path: str = None
    resource_time_series_timeseries_key: int = None
    is_local_expression: bool = None
    expression: str = None

    template_expression: str = None


    @classmethod
    def _from_proto_attribute(cls, proto_attribute: core_pb2.Attribute):
        """Create a `TimeseriesAttribute` from protobuf Mesh Attribute.

        Args:
            proto_attribute (core_pb2.Attribute): protobuf Attribute returned from the gRPC methods.

        Raises:
            TypeError: Error message raised if collection of time series
                attributes is passed as input.
        """
        attribute = cls()
        super()._init_from_proto_attribute(attribute, proto_attribute)

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField('definition'):
            attribute.template_expression = proto_attribute.definition.timeseries_definition.template_expression

        if proto_attribute.HasField('singular_value'):
            proto_value = proto_attribute.singular_value.timeseries_value

            if proto_value.HasField('resource_time_series_id'):
                attribute.resource_time_series_path = proto_value.resource_time_series_id.path
                attribute.resource_time_series_timeseries_key = proto_value.resource_time_series_id.timeseries_key
                attribute.resource_time_series_id = _from_proto_guid(proto_value.resource_time_series_id.id)

            attribute.is_local_expression = proto_value.is_local_expression
            attribute.expression = proto_value.expression
        elif len(proto_attribute.collection_values) > 0:
            raise TypeError('time series collection attribute is not supported')

        return attribute

    def __str__(self) -> str:
        base_message = super()._get_string_representation()
        return (
            f"TimeseriesAttribute:\n"
            f"\t {base_message}\n"
            f"\t resource_time_series_id: {self.resource_time_series_id}\n"
            f"\t resource_time_series_path: {self.resource_time_series_path}\n"
            f"\t resource_time_series_timeseries_key: {self.resource_time_series_timeseries_key}\n"
            f"\t is_local_expression: {self.is_local_expression}\n"
            f"\t expression: {self.expression}\n"
            f"\t template_expression: {self.template_expression}"
        )
