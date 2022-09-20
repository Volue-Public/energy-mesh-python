"""
Functionality for working with Mesh attributes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional, Union

from dateutil import tz
from google.protobuf import timestamp_pb2

from volue.mesh import TimeseriesResource
from volue.mesh._common import LinkRelationVersion, _from_proto_guid
from volue.mesh.proto.core.v1alpha import core_pb2

SIMPLE_TYPE = Union[int, float, bool, str, datetime]
SIMPLE_TYPE_OR_COLLECTION = Union[
    SIMPLE_TYPE, List[int], List[float], List[bool], List[str], List[datetime]
]

PROTO_VALUE_ONE_OF_FIELD_NAME = "value_oneof"
PROTO_DEFINITION_ONE_OF_FIELD_NAME = "definition_type_oneof"


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

    proto_value = getattr(
        proto_attribute_value,
        proto_attribute_value.WhichOneof(PROTO_VALUE_ONE_OF_FIELD_NAME),
    )

    if type(proto_value) is timestamp_pb2.Timestamp:
        # time zone aware datetime as UTC
        proto_value = proto_value.ToDatetime(tz.UTC)

    return proto_value


def _from_proto_attribute(proto_attribute: core_pb2.Attribute):
    """Factory for creating attributes from protobuf Mesh Attribute.

    Args:
        proto_attribute: protobuf Attribute returned from the gRPC methods.
    """
    attribute_value_type = proto_attribute.value_type

    if attribute_value_type == core_pb2.ATTRIBUTE_VALUE_TYPE_TIMESERIES:
        attribute = TimeseriesAttribute(proto_attribute)
    elif attribute_value_type == core_pb2.ATTRIBUTE_VALUE_TYPE_OWNERSHIP_RELATION:
        attribute = OwnershipRelationAttribute(proto_attribute)
    elif attribute_value_type == core_pb2.ATTRIBUTE_VALUE_TYPE_LINK_RELATION:
        attribute = LinkRelationAttribute(proto_attribute)
    elif attribute_value_type == core_pb2.ATTRIBUTE_VALUE_TYPE_VERSIONED_LINK_RELATION:
        attribute = VersionedLinkRelationAttribute(proto_attribute)
    elif attribute_value_type in (
        core_pb2.ATTRIBUTE_VALUE_TYPE_INT,
        core_pb2.ATTRIBUTE_VALUE_TYPE_DOUBLE,
        core_pb2.ATTRIBUTE_VALUE_TYPE_BOOL,
        core_pb2.ATTRIBUTE_VALUE_TYPE_STRING,
        core_pb2.ATTRIBUTE_VALUE_TYPE_UTC_TIME,
    ):
        attribute = SimpleAttribute(proto_attribute)
    else:
        attribute = AttributeBase(proto_attribute, init_definition=True)

    return attribute


class AttributeBase:
    """Base class for Mesh Attribute.

    Represents common information for all kinds of attributes.
    Mesh Attribute is an instance of Attribute Definition in the
    Mesh Model and has always an owner of Object type.
    It has some type (e.g. DoubleAttribute or BoolCollectionAttribute).

    Refer to documentation for more details:
    :ref:`Mesh attribute <mesh_attribute>`.
    """

    class AttributeBaseDefinition:
        """Attribute definition common for all kinds of attributes."""

        def __init__(self, proto_definition: core_pb2.AttributeDefinition):
            self.id: uuid.UUID = _from_proto_guid(
                proto_definition.id
            )  # ID will always be present here
            self.path: str = proto_definition.path
            self.name: str = proto_definition.name
            self.description: str = proto_definition.description
            self.tags: List[str] = []
            for tag in proto_definition.tags:
                self.tags.append(tag)
            self.namespace: str = proto_definition.name_space
            self.type_name: str = proto_definition.type_name
            self.minimum_cardinality: int = proto_definition.minimum_cardinality
            self.maximum_cardinality: int = proto_definition.maximum_cardinality

    def __init__(
        self, proto_attribute: core_pb2.Attribute, init_definition: bool = False
    ):
        self.id: uuid.UUID = _from_proto_guid(proto_attribute.id)
        self.path: str = proto_attribute.path
        self.name: str = proto_attribute.name

        self.definition = None

        # in basic view the definition is not a part of response from Mesh server
        if init_definition and proto_attribute.HasField("definition"):
            self.definition: Optional[
                AttributeBase.AttributeBaseDefinition
            ] = self.AttributeBaseDefinition(proto_attribute.definition)

    def _get_string_representation(self) -> str:
        """Get string representation that could be used by subclasses `__str__` method calls."""
        message = f"name: {self.name}\n" f"\t id: {self.id}\n" f"\t path: {self.path}"

        if self.definition is not None:
            message = (
                f"{message}\n"
                f"\t definition name: {self.definition.name}\n"
                f"\t definition id: {self.definition.id}\n"
                f"\t definition path: {self.definition.path}\n"
                f"\t definition type name: {self.definition.type_name}\n"
                f"\t description: {self.definition.description}\n"
                f"\t tags: {self.definition.tags}\n"
                f"\t namespace: {self.definition.namespace}\n"
                f"\t minimum cardinality: {self.definition.minimum_cardinality}\n"
                f"\t maximum cardinality: {self.definition.maximum_cardinality}"
            )

        return message

    def __str__(self) -> str:
        return f"AttributeBase:\n" f"\t {self._get_string_representation()}"


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

    Refer to documentation for more details:
    :ref:`Mesh attribute <mesh_attribute>`.
    """

    class SimpleAttributeDefinition(AttributeBase.AttributeBaseDefinition):
        """Attribute definition for simple attributes."""

        def __init__(self, proto_definition: core_pb2.AttributeDefinition):
            super().__init__(proto_definition)
            definition_type_name = proto_definition.WhichOneof(
                PROTO_DEFINITION_ONE_OF_FIELD_NAME
            )
            # get the proto message
            definition_type = getattr(proto_definition, definition_type_name)
            # read all of the available proto fields
            field_names = set([field.name for field, _ in definition_type.ListFields()])

            # set all possible values
            # if a field does not exist for the given definition type then return `None`
            self.default_value = _get_field_value(
                "default_value", field_names, definition_type
            )
            self.minimum_value = _get_field_value(
                "minimum_value", field_names, definition_type
            )
            self.maximum_value = _get_field_value(
                "maximum_value", field_names, definition_type
            )
            self.unit_of_measurement: Union[str, None] = _get_field_value(
                "unit_of_measurement", field_names, definition_type
            )

    def __init__(self, proto_attribute: core_pb2.Attribute):
        super().__init__(proto_attribute)

        if proto_attribute.value_type_collection:
            self.value = []
            for proto_value in proto_attribute.values:
                value = _get_attribute_value(proto_value)
                if value is not None:
                    self.value.append(value)
        else:
            self.value = _get_attribute_value(proto_attribute.values[0])

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField("definition"):
            self.definition: Optional[
                SimpleAttribute.SimpleAttributeDefinition
            ] = self.SimpleAttributeDefinition(proto_attribute.definition)

    def __str__(self) -> str:
        base_message = super()._get_string_representation()
        message = f"SimpleAttribute:\n" f"\t {base_message}\n" f"\t value: {self.value}"

        if self.definition is not None:
            message = (
                f"{message}\n"
                f"\t default_value: {self.definition.default_value}\n"
                f"\t minimum_value: {self.definition.minimum_value}\n"
                f"\t maximum_value: {self.definition.maximum_value}\n"
                f"\t unit_of_measurement: {self.definition.unit_of_measurement}"
            )

        return message


class OwnershipRelationAttribute(AttributeBase):
    """Represents an ownership relation Mesh Attribute.

    Ownership relation attributes connect two objects.
    The owned object's owner is always an ownership relation attribute that
    belongs to some other object.

    There are two types of ownership relation attributes
    (`value_type` is provided in the parenthesis):
    - one-to-one (ElementAttributeDefinition)
    - one-to-many (ElementCollectionAttributeDefinition)

    When creating a new object the owner must be an ownership relation
    attribute of one-to-many type (ElementCollectionAttributeDefinition).

    Refer to documentation for more details:
    :ref:`Mesh attribute <mesh_attribute>` and :doc:`mesh_relations`.
    """

    class OwnershipRelationAttributeDefinition(AttributeBase.AttributeBaseDefinition):
        """Attribute definition for ownership relation attribute."""

        def __init__(self, proto_definition: core_pb2.AttributeDefinition):
            super().__init__(proto_definition)
            self.target_object_type_name: str = (
                proto_definition.ownership_relation_definition.target_object_type_name
            )

    def __init__(self, proto_attribute: core_pb2.Attribute):
        super().__init__(proto_attribute)

        self.target_object_ids: List[uuid.UUID] = []

        for value in proto_attribute.values:
            self.target_object_ids.append(
                _from_proto_guid(value.ownership_relation_value.target_object_id)
            )

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField("definition"):
            self.definition: Optional[
                OwnershipRelationAttribute.OwnershipRelationAttributeDefinition
            ] = self.OwnershipRelationAttributeDefinition(proto_attribute.definition)

    def __str__(self) -> str:
        base_message = super()._get_string_representation()
        message = (
            f"OwnershipRelationAttribute:\n"
            f"\t {base_message}\n"
            f"\t target_object_ids: {self.target_object_ids}"
        )

        if self.definition is not None:
            message = (
                f"{message}\n"
                f"\t target_object_type_name: {self.definition.target_object_type_name}"
            )

        return message


class LinkRelationAttribute(AttributeBase):
    """Represents a link relation Mesh Attribute.

    Link relation attributes connect two objects, but object pointing to
    another object does not own it like in `OwnershipRelationAttribute`.

    There are two types of link relation attributes
    (`value_type` is provided in the parenthesis):
    - one-to-one (ReferenceAttributeDefinition)
    - one-to-many (ReferenceCollectionAttributeDefinition)

    There is also a versioned link relation, where the target object can change
    over time. See `VersionedLinkRelationAttribute`.

    Refer to documentation for more details:
    :ref:`Mesh attribute <mesh_attribute>` and :doc:`mesh_relations`.
    """

    class LinkRelationAttributeDefinition(AttributeBase.AttributeBaseDefinition):
        """Attribute definition for link relation attribute."""

        def __init__(self, proto_definition: core_pb2.AttributeDefinition):
            super().__init__(proto_definition)
            self.target_object_type_name: str = (
                proto_definition.link_relation_definition.target_object_type_name
            )

    def __init__(self, proto_attribute: core_pb2.Attribute):
        super().__init__(proto_attribute)

        self.target_object_ids: List[uuid.UUID] = []

        for proto_value in proto_attribute.values:
            self.target_object_ids.append(
                _from_proto_guid(proto_value.link_relation_value.target_object_id)
            )

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField("definition"):
            self.definition: Optional[
                LinkRelationAttribute.LinkRelationAttributeDefinition
            ] = self.LinkRelationAttributeDefinition(proto_attribute.definition)

    def __str__(self) -> str:
        base_message = super()._get_string_representation()
        message = (
            f"LinkRelationAttribute:\n"
            f"\t {base_message}\n"
            f"\t target_object_ids: {self.target_object_ids}"
        )

        if self.definition is not None:
            message = (
                f"{message}\n"
                f"\t target_object_type_name: {self.definition.target_object_type_name}"
            )

        return message


class VersionedLinkRelationAttribute(AttributeBase):
    """Represents a versioned link relation Mesh Attribute.

    Versioned link relation, which is a link relation where the target object
    can change over time. It consists of a list of pairs:
    - Target object identifier.
    - Timestamp which indicates start of the period where the target object is
    active (linked to), the target object is active until the next target
    object in the list, if any, becomes active.

    There are two types of versioned link relation attributes
    (`value_type` is provided in the parenthesis):
    - one-to-one (ReferenceSeriesAttributeDefinition)
    - one-to-many (ReferenceSeriesCollectionAttributeDefinition)

    Refer to documentation for more details:
    :ref:`Mesh attribute <mesh_attribute>` and :doc:`mesh_relations`.
    """

    @dataclass
    class VersionedLinkRelationEntry:
        """Represents a versioned link relation entry."""

        versions: List[LinkRelationVersion]

    def __init__(self, proto_attribute: core_pb2.Attribute):
        super().__init__(proto_attribute)

        self.entries: List[
            VersionedLinkRelationAttribute.VersionedLinkRelationEntry
        ] = []

        for proto_value in proto_attribute.values:
            versions: List[LinkRelationVersion] = []

            for proto_version in proto_value.versioned_link_relation_value.versions:
                target_object_id = _from_proto_guid(proto_version.target_object_id)
                valid_from_time = proto_version.valid_from_time.ToDatetime(tz.UTC)
                versions.append(LinkRelationVersion(target_object_id, valid_from_time))

            self.entries.append(self.VersionedLinkRelationEntry(versions))

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField("definition"):
            self.definition: Optional[
                LinkRelationAttribute.LinkRelationAttributeDefinition
            ] = LinkRelationAttribute.LinkRelationAttributeDefinition(
                proto_attribute.definition
            )

    def __str__(self) -> str:
        base_message = super()._get_string_representation()
        message = (
            f"VersionedLinkRelationAttribute:\n"
            f"\t {base_message}\n"
            f"\t entries: {self.entries}"
        )

        if self.definition is not None:
            message = (
                f"{message}\n"
                f"\t target_object_type_name: {self.definition.target_object_type_name}"
            )

        return message


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

    Refer to documentation for more details:
    :ref:`Mesh attribute <mesh_attribute>`.
    """

    class TimeseriesAttributeDefinition(AttributeBase.AttributeBaseDefinition):
        """Attribute definition for time series attribute."""

        def __init__(self, proto_definition: core_pb2.AttributeDefinition):
            super().__init__(proto_definition)
            self.template_expression: str = (
                proto_definition.timeseries_definition.template_expression
            )
            self.unit_of_measurement: str = (
                proto_definition.timeseries_definition.unit_of_measurement
            )

    def __init__(self, proto_attribute: core_pb2.Attribute):
        super().__init__(proto_attribute)

        if len(proto_attribute.values) > 1:
            raise TypeError("time series collection attribute is not supported")

        proto_value = proto_attribute.values[0].timeseries_value

        if proto_value.HasField("time_series_resource"):
            self.time_series_resource = (
                TimeseriesResource._from_proto_timeseries_resource(
                    proto_value.time_series_resource
                )
            )
        else:
            self.time_series_resource = (
                None  # for typing hints: "TimeseriesResource | None"
            )

        self.is_local_expression: bool = proto_value.is_local_expression
        self.expression: str = proto_value.expression

        # in basic view the definition is not a part of response from Mesh server
        if proto_attribute.HasField("definition"):
            self.definition: Optional[
                TimeseriesAttribute.TimeseriesAttributeDefinition
            ] = self.TimeseriesAttributeDefinition(proto_attribute.definition)

    def __str__(self: TimeseriesAttribute) -> str:
        base_message = super()._get_string_representation()
        message = (
            f"TimeseriesAttribute:\n"
            f"\t {base_message}\n"
            f"\t time_series_resource: {self.time_series_resource}\n"
            f"\t is_local_expression: {self.is_local_expression}\n"
            f"\t expression: {self.expression}"
        )

        if self.definition is not None:
            message = (
                f"{message}\n"
                f"\t template_expression: {self.definition.template_expression}\n"
                f"\t unit_of_measurement: {self.definition.unit_of_measurement}"
            )

        return message
