"""
Common classes/enums/etc. for the Mesh API.
"""

import uuid
from dataclasses import dataclass
import datetime
from typing import List, Optional
import uuid

from google.protobuf import field_mask_pb2, timestamp_pb2
import pyarrow as pa

from volue.mesh import Timeseries
from volue.mesh.proto.core.v1alpha import core_pb2
from volue.mesh.proto.type import resources_pb2


@dataclass
class AttributesFilter:
    """Defines what attributes need to be returned in response message.

    Name mask:

    Attribute name uniquely identifies attribute within given object.
    If set then only attributes set in the field mask are read.
    See examples below for more details.
    Note: The attribute name provided in the mask must be equal to
    the actual attribute name in the model.
    Regular expressions are not supported.

    Tag mask:

    If multiple tags are provided then all attributes having
    at least one of them are returned (logical OR).
    See examples below for more details.
    Note: Regular expressions are not supported.

    Namespace mask:

    If multiple namespaces are provided then all attributes having
    at least one of them are returned (logical OR).
    See examples below for more details.
    Note: Regular expressions are not supported.
    If an attribute has more than one namespace, they are
    concatentad with dots '.', e.g.: namespace1.namespace2
    In such case the namespace mask must provide also
    "namespace1.namespace2" as one entry in the namespace mask.

    `return_no_attributes` flag:

    If set to True then no attributes will be returned.
    All above masks will be ignored.
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

    name_mask: List[str] = None
    tag_mask: List[str] = None
    namespace_mask: List[str] = None
    return_no_attributes: bool = False


@dataclass
class MeshObjectId:
    """`MeshObjectId` represents a unique way of identifying a Mesh object.

    Args:
        timskey (int): integer that only applies to a specific physical or virtual time series
        uuid_id (uuid.UUID): Universal Unique Identifier for Mesh objects
        full_name (str): path in the :ref:`Mesh object model <mesh object model>`
    """
    timskey: int = None
    uuid_id: uuid.UUID = None
    full_name: str = None

    @classmethod
    def with_timskey(cls, timskey: int):
        """Create a `MeshObjectId` using a timskey of a Mesh object

        Args:
            timskey (int): integer that only applies to a specific raw time series
        """
        mesh_object_id = cls()
        mesh_object_id.timskey = timskey
        return mesh_object_id

    @classmethod
    def with_uuid_id(cls, uuid_id: uuid.UUID):
        """Create a `MeshObjectId` using an uuid of a Mesh object

        Args:
            uuid_id (uuid.UUID): Universal Unique Identifier for Mesh objects
        """
        mesh_object_id = cls()
        mesh_object_id.uuid_id = uuid_id
        return mesh_object_id

    @classmethod
    def with_full_name(cls, full_name: str):
        """Create a `MeshObjectId` using full_name of a Mesh object

        Args:
            full_name (str): path in the :ref:`Mesh object model <mesh object model>`
        """
        mesh_object_id = cls()
        mesh_object_id.full_name = full_name
        return mesh_object_id


def _to_proto_guid(uuid: uuid.UUID) -> Optional[resources_pb2.Guid]:
    """Convert from Python UUID format to Microsoft's GUID format.

    Args:
        uuid (uuid.UUID): identifier in Python's UUID format

    Returns:
        resources_pb2.Guid
    """
    if uuid is None:
        return None
    return resources_pb2.Guid(bytes_le=uuid.bytes_le)


def _from_proto_guid(guid: resources_pb2.Guid) -> uuid.UUID:
    """Convert from Microsoft's GUID format to UUID format.

    Args:
        guid (resources_pb2.Guid): GUID to be converted

    Returns:
        uuid.UUID
    """
    if guid is None:
        return None
    return uuid.UUID(bytes_le=guid.bytes_le)


def _to_proto_curve_type(curve: Timeseries.Curve) -> resources_pb2.Curve:
    """
    Converts from Timeseries Curve type to protobuf curve type.

    Args:
        curve (Timeseries.Curve): the curve to convert

    Returns:
        resources_pb2.Curve
    """
    proto_curve = resources_pb2.Curve()
    proto_curve.type = resources_pb2.Curve.UNKNOWN
    if curve == Timeseries.Curve.PIECEWISELINEAR:
        proto_curve.type = resources_pb2.Curve.PIECEWISELINEAR
    elif curve == Timeseries.Curve.STAIRCASE:
        proto_curve.type = resources_pb2.Curve.STAIRCASE
    elif curve == Timeseries.Curve.STAIRCASESTARTOFSTEP:
        proto_curve.type = resources_pb2.Curve.STAIRCASESTARTOFSTEP

    return proto_curve


def _to_protobuf_utcinterval(start_time: datetime, end_time: datetime) -> resources_pb2.UtcInterval:
    """
    Convert to protobuf UtcInterval.

    Args:
        start_time (datetime): start of the interval
        end_time (datetime): end of the interval

    Returns:
        resources_pb2.UtcInterval
    """
    start = timestamp_pb2.Timestamp()
    start.FromDatetime(start_time)
    end = timestamp_pb2.Timestamp()
    end.FromDatetime(end_time)
    interval = resources_pb2.UtcInterval(
        start_time=start,
        end_time=end
    )
    return interval


def _to_proto_object_id(timeseries: Timeseries) -> core_pb2.ObjectId:
    """
    Convert a Timeseries to corresponding protobuf ObjectId

    Args:
        timeseries (Timeseries): the time series to convert

    Returns:
        core_pb2.ObjectId
    """
    return core_pb2.ObjectId(
        timskey=timeseries.timskey,
        guid=_to_proto_guid(timeseries.uuid),
        full_name=timeseries.full_name
    )


def _to_proto_timeseries(timeseries: Timeseries) -> core_pb2.Timeseries:
    """
    Converts a protobuf timeseries reply from Mesh server into Timeseries

    Args:
        timeseries (Timeseries):t the timeseries to convert

    Returns:
        core_pb2.Timeseries
    """
    stream = pa.BufferOutputStream()
    writer = pa.ipc.RecordBatchStreamWriter(
        sink=stream,
        schema=timeseries.arrow_table.schema
    )

    writer.write_table(timeseries.arrow_table)
    buffer = stream.getvalue()

    proto_timeserie = core_pb2.Timeseries(
        object_id=_to_proto_object_id(timeseries),
        resolution=timeseries.resolution,
        interval=_to_protobuf_utcinterval(start_time=timeseries.start_time, end_time=timeseries.end_time),
        data=buffer.to_pybytes()
    )
    return proto_timeserie



def _to_proto_mesh_id(id: uuid.UUID, path: str) -> core_pb2.MeshId:
    proto_mesh_id = core_pb2.MeshId()

    if id is not None:
        if isinstance(id, str):
            id = uuid.UUID(id)
        proto_mesh_id.id.CopyFrom(_to_proto_guid(id))
    if path is not None:
        proto_mesh_id.path = path

    if id is None and path is None:
        raise ValueError("need to specify either path or id")

    return proto_mesh_id


def _to_proto_attribute_masks(attributes_filter: Optional[AttributesFilter]) -> core_pb2.AttributesMasks:
    attributes_masks = core_pb2.AttributesMasks()

    if attributes_filter is not None:
        if attributes_filter.name_mask is not None:
            attributes_masks.name_mask.CopyFrom(field_mask_pb2.FieldMask(paths=attributes_filter.name_mask))
        if attributes_filter.tag_mask is not None:
            attributes_masks.tag_mask.CopyFrom(field_mask_pb2.FieldMask(paths=attributes_filter.tag_mask))
        if attributes_filter.namespace_mask is not None:
            attributes_masks.namespace_mask.CopyFrom(field_mask_pb2.FieldMask(paths=attributes_filter.namespace_mask))
        attributes_masks.return_no_attributes = attributes_filter.return_no_attributes

    return attributes_masks

def _read_proto_reply(reply: core_pb2.ReadTimeseriesResponse) -> List[Timeseries]:
    """
    Converts a protobuf time series reply from Mesh server into Timeseries

    Args:
        reply (core_pb2.ReadTimeseriesResponse): the reply from a time series read operation

    Raises:
        ValueError: no time series data

    Returns:
        List[Timeseries]: list of time series extracted from the reply
    """
    timeseries = []
    for timeserie in reply.timeseries:
        resolution = timeserie.resolution
        interval = timeserie.interval

        if not timeserie.data:
            raise ValueError('No data in time series reply for the given interval')

        reader = pa.ipc.open_stream(timeserie.data)
        table = reader.read_all()

        if timeserie.HasField("object_id"):
            object_id = timeserie.object_id
            ts = Timeseries(table, resolution,
                            interval.start_time, interval.end_time,
                            object_id.timskey, _from_proto_guid(object_id.guid), object_id.full_name)
        else:
            ts = Timeseries(table, resolution,
                            interval.start_time, interval.end_time)

        timeseries.append(ts)
    return timeseries


def _read_proto_numeric_reply(reply: core_pb2.ReadTimeseriesResponse) -> List[float]:
    """
    Converts a protobuf numeric calculation reply from Mesh server into a list of floats

    Args:
        reply (core_pb2.ReadTimeseriesResponse): the reply from a time series read operation

    Returns:
        List[float]: list of floats extracted from the reply
    """
    results = []
    for value in reply.value:
        results.append(value)
    return results
