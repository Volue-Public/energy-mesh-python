"""
Common classes/enums/etc. for the Mesh API.
"""

import uuid
from dataclasses import dataclass
import datetime
from typing import List, Optional
from google.protobuf import timestamp_pb2
import pyarrow as pa

from volue.mesh import Timeseries
from volue.mesh.proto.core.v1alpha import core_pb2
from volue.mesh.proto.type import resources_pb2


@dataclass
class MeshObjectId:
    """`MeshObjectId` represents a unique way of identifying a Mesh object.

    Args:
        timskey (int):  integer that only applies to a specific raw time series
        uuid_id (uuid.UUID):   Universal Unique Identifier for Mesh objects
        full_name (str): path in the :ref:`Mesh object model <mesh object model>`
    """
    timskey: int = None
    uuid_id: uuid.UUID = None
    full_name: str = None

    @classmethod
    def with_timskey(cls, timskey: int):
        """Create a `MeshObjectId` using a timskey of a Mesh object

        Args:
            timskey (int):  integer that only applies to a specific raw time series
        """
        mesh_object_id = cls()
        mesh_object_id.timskey = timskey
        return mesh_object_id

    @classmethod
    def with_uuid_id(cls, uuid_id: uuid.UUID):
        """Create a `MeshObjectId` using an uuid of a Mesh object

        Args:
            uuid_id (uuid.UUID):  Universal Unique Identifier for Mesh objects
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
