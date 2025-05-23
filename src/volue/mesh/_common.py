"""
Common classes/enums/etc. for the Mesh API.
"""

from __future__ import annotations

import datetime
import logging
import uuid
from dataclasses import dataclass, fields
from typing import List, Optional, Tuple

import pyarrow as pa
from google.protobuf import field_mask_pb2, timestamp_pb2

from bidict import bidict

from volue.mesh import Timeseries
from volue.mesh.proto import type
from volue.mesh.proto.auth.v1alpha import auth_pb2
from volue.mesh.proto.config.v1alpha import config_pb2
from volue.mesh.proto.model.v1alpha import resources_pb2 as model_resources_pb2
from volue.mesh.proto.time_series.v1alpha import time_series_pb2


@dataclass
class AttributesFilter:
    """Defines what attributes need to be returned in response message.

    Attributes:
        Name mask:
            Attribute name uniquely identifies attribute within given object.
            If set then only attributes set in the name mask are read.
            If any other mask: tag or namespace or `return_no_attributes`
            flag is also set then an error will be returned.
            The attribute name provided in the mask must be equal to
            the actual attribute name in the model.
            Note: Regular expressions are not supported.
            See examples below for more details.

        Tag mask:
            Each attribute can have zero, one or more tags.
            If the tag mask is set then only attributes with
            at least one tag set in the field mask are read.
            If multiple tags are provided then all attributes having
            at least one of them are returned (logical OR).
            If name mask or `return_no_attributes` flag is also set
            then an error will be returned.
            It is allowed to have both: tag mask and namespace mask set.
            Note: Regular expressions are not supported.
            See examples below for more details.

        Namespace mask:
            Each attribute can have zero, one or more namespaces.
            If the namespace mask is set then only attributes with
            at least one namespace set in the field mask are read.
            If multiple namespaces are provided in the mask then all
            attributes having at least one of them are returned (logical OR).
            Namespace mask does not accept entries with namespaces
            concatenated with dots '.'. Each namespace mask entry must
            be a separate namespace.
            If name mask or `return_no_attributes` flag is also set
            then an error will be returned.
            It is allowed to have both: tag mask and namespace mask set.
            Note: Regular expressions are not supported.
            See examples below for more details.

        `return_no_attributes` flag:
            If set to True then no attributes will be returned.
            If any mask: name, tag or namespace is also set
            then an error will be returned.
            Default value is False.

    Multiple attributes may have the same tag or namespace.
    If both: `tag_mask` and `namespace_mask` are provided then only attributes
    that meet both criteria are returned (intersection/logical AND).

    Note: If no masks are provided then all attributes will be returned.

    Example 1:

        Arg:      `names` is set to "Price,Volume,Production"
        Response: All attributes with names "Price", "Volume" or "Production" will be returned.
        Note:     `tag_mask` or `namespace_mask` will be ignored even if set.

    Example 2:

        Arg:      `tag_mask` is set to "ProductionAttributes,LocationAttributes"
        Response: All attributes with tag name "ProductionAttributes" or "LocationAttributes" will be returned.
        Note:     If attributes A1, A2 have tag "ProductionAttributes" and A3
        has "LocationAttributes" then all three attributes (A1, A2 and A3) will be returned.
        Exactly the same rules apply to `namespace_mask`.

    Example 3:

        Arg:      `namespace_mask` is set to "Hydro,Wind".
        Response: All attributes with namespace "Hydro" or "Wind" will be returned.
        Note:     Suppose there are the following attributes:
        - A1 (namespace "EnergySystem.Hydro")
        - A2 (namespace "EnergySystem.Wind")
        - A3 (namespace "EnergySystem.Carbon")
        - A4 (namespace "EnergySystem.Hydro.Small")
        - A5 (namespace "Hydro.Normal")

            In this case attributes A1, A2, A4 and A5 will be returned.

    Example 4:

        Arg:      `tag_mask` is set to "ProductionAttributes", `namespace_mask` is set to "Hydro,Wind".
        Response: All attributes with tag name "ProductionAttributes" and namespace "Hydro" or "Wind" will be returned.
        Note:     Suppose there are the following attributes:
        - A1 (tag "ProductionAttributes", namespace "Hydro")
        - A2 (tag "ProductionAttributes", namespace "Wind")
        - A3 (tag "ProductionAttributes", namespace "Carbon")
        - A4 (tag "LocationAttributes", namespace "Hydro")
        - A5 (tag "LocationAttributes", namespace "Wind")

            In this case attributes A1 and A2 will be returned.
    """

    name_mask: Optional[List[str]] = None
    tag_mask: Optional[List[str]] = None
    namespace_mask: Optional[List[str]] = None
    return_no_attributes: bool = False


@dataclass
class UserIdentity:
    """Represents a Mesh server user identity.

    display_name - a human readable name identifying this user. This name
    should not be used as a unique identifier for the user as it may be
    identical  between users and change over time.

    source - security package name where the user identity came from.
    It is not a unique identifier of the security package instance.

    identifier - uniquely identifies the user within given `source` instance, but
    not necessarily globally. Combining `source` and `identifier` does not guarantee
    to get globally unique identifier for the user as there may be different
    Active Directories using the same security packages (`source`) with
    duplicated user identifiers. However such situation is rather unlikely.
    """

    display_name: str
    source: str
    identifier: str

    @classmethod
    def _from_proto(cls, proto_user_identity: auth_pb2.UserIdentity) -> UserIdentity:
        """Create a `UserIdentity` from protobuf UserIdentity.

        Args:
            proto_user_identity: Protobuf UserIdentity returned from the gRPC method.
        """
        return cls(
            display_name=proto_user_identity.display_name,
            source=proto_user_identity.source,
            identifier=proto_user_identity.identifier,
        )


@dataclass
class VersionInfo:
    """
    Represents a Mesh server version information.

    version - version number, e.g.: 2.5.2.32

    name - friendly name of the Mesh server, e.g.: Volue Mesh Server.
    """

    version: str
    name: str

    @classmethod
    def _from_proto(cls, proto_version_info: config_pb2.VersionInfo) -> VersionInfo:
        """Create a `VersionInfo` from protobuf VersionInfo.

        Args:
            proto_version_info: protobuf VersionInfo returned from the gRPC method.
        """
        return cls(version=proto_version_info.version, name=proto_version_info.name)


@dataclass
class XyCurve:
    """A list of (x, y) pairs, indexed by a reference/z value.

    See Also:
        :doc:`mesh_xy_sets`
    """

    z: float
    xy: List[Tuple[float, float]]

    def __iter__(self):
        return (getattr(self, field.name) for field in fields(self))


@dataclass
class XySet:
    """A set of XY-curves.

    If this set is part of a versioned XY-set attribute (:code:`XYZSeriesAttribute`)
    the :code:`valid_from_time` field contains a datetime with the start of the validity
    period for the XY-set. Otherwise it will be :code:`None`.

    See Also:
        :doc:`mesh_xy_sets`
    """

    valid_from_time: Optional[datetime.datetime]
    xy_curves: List[XyCurve]

    def __iter__(self):
        return (getattr(self, field.name) for field in fields(self))


@dataclass
class RatingCurveSegment:
    """Represents a rating curve segment.

    Contains `a`, `b` and `c` factors for the discharge formula.
    Additionally each segment `i` stores a 64 bit floating point
    `x_range_until` value and is valid for a range of `x` values
    `[x_range_until[i-1], x_range_until[i])`.

    See Also:
         :doc:`mesh_rating_curve`
    """

    x_range_until: float
    factor_a: float
    factor_b: float
    factor_c: float

    def __iter__(self):
        return (getattr(self, field.name) for field in fields(self))

    def __str__(self) -> str:
        return (
            f"x range until={self.x_range_until}, "
            f"a={self.factor_a}, "
            f"b={self.factor_b}, "
            f"c={self.factor_c}\n"
        )


@dataclass
class RatingCurveVersion:
    """Represents a rating curve version.

    Contains rating curve segments, timestamp with the time at which the
    version becomes active and a threshold indicating the minimal `x` value
    for the curve. For `x < x_range_from` for the given version the
    `f(x) = nan`.

    See Also:
         :doc:`mesh_rating_curve`
    """

    x_range_from: float
    valid_from_time: datetime.datetime
    x_value_segments: List[RatingCurveSegment]

    def __iter__(self):
        return (getattr(self, field.name) for field in fields(self))

    def __str__(self) -> str:
        message = (
            f"Valid from: {self.valid_from_time}\n"
            f"x range from: {self.x_range_from}\n"
        )
        for i, segment in enumerate(self.x_value_segments):
            message = f"{message}" f"\tSegment {i+1}: {segment}"
        return message


@dataclass
class LinkRelationVersion:
    """Represents a link relation version.

    Contains target object ID and timestamp with the time at which the
    version becomes active. If target object ID is None, then it means
    the target object is "empty".

    See Also:
         :doc:`mesh_relations`
    """

    target_object_id: Optional[uuid.UUID]
    valid_from_time: datetime.datetime

    def __iter__(self):
        return (getattr(self, field.name) for field in fields(self))


@dataclass
class LogMessage:
    """Represents a log message from the Mesh server.

    These are returned as a response from hydro simulations and inflow
    calculations.
    """

    level: int
    message: str

    @classmethod
    def _from_proto(cls, proto):
        levels = {
            type.resources_pb2.LogLevel.TRACE: logging.DEBUG,
            type.resources_pb2.LogLevel.DEBUG: logging.DEBUG,
            type.resources_pb2.LogLevel.INFO: logging.INFO,
            type.resources_pb2.LogLevel.WARN: logging.WARNING,
            type.resources_pb2.LogLevel.ERR: logging.ERROR,
        }

        level = levels[proto.level]

        return cls(level, proto.message)


@dataclass
class HydSimDataset:
    """A representation of data used in a hydro simulation or inflow calculation.

    The HydSim team may use a dataset to diagnose issues. When Volue requests a
    dataset we recommend storing datasets with filename `name` and contents
    from `data` and then sending those files to Volue.
    """

    name: str
    data: bytes

    @classmethod
    def _from_proto(cls, proto):
        return cls(proto.name, proto.data)


def _to_proto_guid(uuid: Optional[uuid.UUID]) -> Optional[type.resources_pb2.Guid]:
    """Converts from Python UUID format to Microsoft's GUID format.

    Args:
        uuid: Identifier in Python's UUID format.
    """
    if uuid is None:
        return None
    return type.resources_pb2.Guid(bytes_le=uuid.bytes_le)


def _from_proto_guid(guid: Optional[type.resources_pb2.Guid]) -> Optional[uuid.UUID]:
    """Converts from Microsoft's GUID format to UUID format.

    Args:
        guid: GUID to be converted.
    """
    if guid is None:
        return None
    return uuid.UUID(bytes_le=guid.bytes_le)


CURVE_TYPES = bidict(
    {
        Timeseries.Curve.UNKNOWN: type.resources_pb2.Curve.UNKNOWN,
        Timeseries.Curve.PIECEWISELINEAR: type.resources_pb2.Curve.PIECEWISELINEAR,
        Timeseries.Curve.STAIRCASE: type.resources_pb2.Curve.STAIRCASE,
        Timeseries.Curve.STAIRCASESTARTOFSTEP: type.resources_pb2.Curve.STAIRCASESTARTOFSTEP,
    }
)


def _to_proto_curve_type(curve: Timeseries.Curve) -> type.resources_pb2.Curve:
    """
    Converts from Timeseries.Curve type to protobuf curve type.

    Args:
        curve: The curve to convert.
    """
    proto_curve = type.resources_pb2.Curve()

    proto_curve.type = CURVE_TYPES[curve]

    return proto_curve


def _from_proto_curve_type(proto_curve: type.resources_pb2.Curve) -> Timeseries.Curve:
    """
    Converts from protobuf curve type to Timeseries.Curve type.

    Args:
        proto_curve: The protobuf curve to convert.
    """
    return CURVE_TYPES.inverse[proto_curve.type]


RESOLUTIONS = bidict(
    {
        Timeseries.Resolution.UNDEFINED: type.resources_pb2.Resolution.UNDEFINED,
        Timeseries.Resolution.BREAKPOINT: type.resources_pb2.Resolution.BREAKPOINT,
        Timeseries.Resolution.MIN15: type.resources_pb2.Resolution.MIN15,
        Timeseries.Resolution.MIN30: type.resources_pb2.Resolution.MIN30,
        Timeseries.Resolution.HOUR: type.resources_pb2.Resolution.HOUR,
        Timeseries.Resolution.DAY: type.resources_pb2.Resolution.DAY,
        Timeseries.Resolution.WEEK: type.resources_pb2.Resolution.WEEK,
        Timeseries.Resolution.MONTH: type.resources_pb2.Resolution.MONTH,
        Timeseries.Resolution.YEAR: type.resources_pb2.Resolution.YEAR,
    }
)


def _to_proto_resolution(
    resolution: Timeseries.Resolution,
) -> type.resources_pb2.Resolution:
    """
    Converts from Timeseries.Resolution type to protobuf resolution type.

    Args:
        resolution: The resolution to convert.
    """
    proto_resolution = type.resources_pb2.Resolution()

    proto_resolution.type = RESOLUTIONS[resolution]

    return proto_resolution


def _from_proto_resolution(
    proto_resolution: type.resources_pb2.Resolution,
) -> Timeseries.Resolution:
    """
    Converts from protobuf resolution type to Timeseries.Resolution type.

    Args:
        proto_resolution: The protobuf resolution to convert.
    """
    return RESOLUTIONS.inverse[proto_resolution.type]


def _to_proto_utcinterval(
    start_time: datetime.datetime, end_time: datetime.datetime
) -> type.resources_pb2.UtcInterval:
    """
    Converts to protobuf UtcInterval.

    Args:
        start_time: Start of the interval.
        end_time: End of the interval.

    Returns:
        Protobuf UtcInterval.
    """
    start = timestamp_pb2.Timestamp()
    start.FromDatetime(start_time)
    end = timestamp_pb2.Timestamp()
    end.FromDatetime(end_time)
    interval = type.resources_pb2.UtcInterval(start_time=start, end_time=end)
    return interval


def _to_proto_timeseries(
    timeseries: Timeseries,
) -> time_series_pb2.Timeseries:
    """
    Converts a Timeseries to corresponding protobuf Timeseries.

    Args:
        timeseries: The time series to convert.

    Returns:
        Protobuf Timeseries.
    """
    stream = pa.BufferOutputStream()
    writer = pa.ipc.RecordBatchStreamWriter(
        sink=stream, schema=timeseries.arrow_table.schema
    )

    writer.write_table(timeseries.arrow_table)
    buffer = stream.getvalue()

    proto_timeseries = time_series_pb2.Timeseries(
        id=_to_proto_mesh_id_from_timeseries(timeseries),
        resolution=timeseries.resolution,
        interval=_to_proto_utcinterval(
            start_time=timeseries.start_time, end_time=timeseries.end_time
        ),
        data=buffer.to_pybytes(),
    )
    return proto_timeseries


def _to_proto_mesh_id_from_timeseries(
    timeseries: Timeseries,
) -> type.resources_pb2.MeshId:
    proto_mesh_id = type.resources_pb2.MeshId()

    if timeseries.uuid is not None:
        proto_mesh_id.id.CopyFrom(_to_proto_guid(timeseries.uuid))
    if timeseries.full_name is not None:
        proto_mesh_id.path = timeseries.full_name
    if timeseries.timskey is not None:
        proto_mesh_id.timeseries_key = timeseries.timskey

    if (
        timeseries.uuid is None
        and timeseries.full_name is None
        and timeseries.timskey is None
    ):
        raise TypeError("need to specify either path, id or time series key")

    return proto_mesh_id


def _to_proto_attribute_masks(
    attributes_filter: Optional[AttributesFilter],
) -> model_resources_pb2.AttributesMasks:
    attributes_masks = model_resources_pb2.AttributesMasks()

    if attributes_filter is not None:
        if attributes_filter.name_mask is not None:
            attributes_masks.name_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=attributes_filter.name_mask)
            )
        if attributes_filter.tag_mask is not None:
            attributes_masks.tag_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=attributes_filter.tag_mask)
            )
        if attributes_filter.namespace_mask is not None:
            attributes_masks.namespace_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=attributes_filter.namespace_mask)
            )

    return attributes_masks


def _object_to_proto_field_mask(
    attributes_filter: Optional[AttributesFilter],
) -> Optional[field_mask_pb2.FieldMask]:
    if attributes_filter is None or not attributes_filter.return_no_attributes:
        return None
    fields = [field.name for field in model_resources_pb2.Object.DESCRIPTOR.fields]
    fields.remove("attributes")
    return field_mask_pb2.FieldMask(paths=fields)


def _to_proto_attribute_field_mask(
    full_attribute_info: bool, attributes_filter: Optional[AttributesFilter] = None
) -> Optional[field_mask_pb2.FieldMask]:
    # If attributes_filter.return_no_attributes is set to True we must not provide attribute field mask,
    # at the same time we can't expect user to provide full_attribute_info set to True. It would be very counter intuitive
    # to request no attributes and have to explicitly request full attributes info.
    if attributes_filter is not None and attributes_filter.return_no_attributes:
        return None

    if full_attribute_info:
        return None

    return field_mask_pb2.FieldMask(
        paths=[
            "id",
            "path",
            "name",
            "values",
            "value_type",
            "value_type_collection",
            "owner_id",
        ]
    )


def _read_proto_reply(
    reply: time_series_pb2.ReadTimeseriesResponse,
) -> List[Timeseries]:
    """
    Converts a protobuf time series reply from Mesh server into Timeseries.

    Args:
        reply: The reply from a time series read operation.

    Returns:
        An array of time series extracted from the reply.

    Raises:
        ValueError: no time series data.
    """
    timeseries = []
    for proto_timeseries in reply.timeseries:
        resolution = proto_timeseries.resolution

        # Since Mesh 2.17 in case of an empty time series an empty Arrow table is returned.
        # As a result, the below ValueError is deprecated and will be removed in future releases.
        if not proto_timeseries.data:
            raise ValueError("No data in time series reply for the given interval")

        if proto_timeseries.HasField("interval"):
            start_time = proto_timeseries.interval.start_time
            end_time = proto_timeseries.interval.end_time
        else:
            start_time = None
            end_time = None

        reader = pa.ipc.open_stream(proto_timeseries.data)
        table = reader.read_all()

        if proto_timeseries.HasField("id"):
            timeseries_id = proto_timeseries.id
            ts = Timeseries(
                table,
                _from_proto_resolution(resolution),
                start_time,
                end_time,
                timeseries_id.timeseries_key,
                _from_proto_guid(timeseries_id.id),
                timeseries_id.path,
            )
        else:
            ts = Timeseries(table, resolution, start_time, end_time)

        timeseries.append(ts)
    return timeseries


def _read_proto_numeric_reply(
    reply: time_series_pb2.ReadTimeseriesResponse,
) -> List[float]:
    """
    Converts a protobuf numeric calculation reply from Mesh server into an array of floating points values.

    Args:
        reply: The reply from a time series read operation.

    Returns:
        An array of floating point values extracted from the reply.
    """
    results = []
    for value in reply.value:
        results.append(value)
    return results


def _datetime_to_timestamp_pb2(datetime: datetime.datetime):
    """Converts datetime type to protobuf Timestamp type."""
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(datetime)
    return timestamp
