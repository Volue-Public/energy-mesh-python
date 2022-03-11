import uuid
from dataclasses import dataclass
import datetime
from typing import List

import pyarrow as pa

from volue.mesh import Timeseries
from volue.mesh.proto.core.v1alpha import core_pb2
from volue.mesh.proto.type import resources_pb2
from google.protobuf import timestamp_pb2


@dataclass
class MeshObjectId:
    """Mesh object id represents a unique way of identifying a Mesh object.

    - timskey only apply to specific raw time series.
    - uuid_id applies to all Mesh objects
    - full_name applies to all Mesh objects that are in the Mesh model structure
    """
    timskey: int = None
    uuid_id: uuid.UUID = None
    full_name: str = None


def to_proto_guid(uuid: uuid.UUID) -> resources_pb2.Guid:
    """Convert from UUID format to Microsoft's GUID format.

    :param uuid: UUID
    :return: GUID
    """
    if uuid is None:
        return None
    return resources_pb2.Guid(bytes_le=uuid.bytes_le)


def from_proto_guid(guid: resources_pb2.Guid) -> uuid.UUID:
    """Convert from Microsoft's GUID format to UUID format.

    :param guid: GUID to be converted
    :return: UUID
    """
    if guid is None:
        return None
    return uuid.UUID(bytes_le=guid.bytes_le)


def to_proto_curve_type(curve: Timeseries.Curve) -> resources_pb2.Curve:
    """Converts from Timeseries Curve type to protobuf curve type."""
    proto_curve = resources_pb2.Curve()
    proto_curve.type = resources_pb2.Curve.UNKNOWN
    if curve == Timeseries.Curve.PIECEWISELINEAR:
        proto_curve.type = resources_pb2.Curve.PIECEWISELINEAR
    elif curve == Timeseries.Curve.STAIRCASE:
        proto_curve.type = resources_pb2.Curve.STAIRCASE
    elif curve == Timeseries.Curve.STAIRCASESTARTOFSTEP:
        proto_curve.type = resources_pb2.Curve.STAIRCASESTARTOFSTEP

    return proto_curve


def to_protobuf_utcinterval(start_time: datetime, end_time: datetime) -> resources_pb2.UtcInterval:
    """Convert to protobuf UtcInterval."""
    start = timestamp_pb2.Timestamp()
    start.FromDatetime(start_time)
    end = timestamp_pb2.Timestamp()
    end.FromDatetime(end_time)
    interval = resources_pb2.UtcInterval(
        start_time=start,
        end_time=end
    )
    return interval


def to_proto_object_id(timeseries: Timeseries) -> core_pb2.ObjectId:
    """Convert a Timeseries to corresponding protobuf ObjectId"""
    return core_pb2.ObjectId(
        timskey=timeseries.timskey,
        guid=to_proto_guid(timeseries.uuid),
        full_name=timeseries.full_name
    )


def to_proto_timeseries(timeseries: Timeseries) -> core_pb2.Timeseries:
    """Converts a protobuf timeseries reply from Mesh server into Timeseries"""
    stream = pa.BufferOutputStream()
    writer = pa.ipc.RecordBatchStreamWriter(
        sink=stream,
        schema=timeseries.arrow_table.schema
    )

    writer.write_table(timeseries.arrow_table)
    buffer = stream.getvalue()

    proto_timeserie = core_pb2.Timeseries(
        object_id=to_proto_object_id(timeseries),
        resolution=timeseries.resolution,
        interval=to_protobuf_utcinterval(start_time=timeseries.start_time, end_time=timeseries.end_time),
        data=buffer.to_pybytes()
    )
    return proto_timeserie


def read_proto_reply(reply: core_pb2.ReadTimeseriesResponse) -> List[Timeseries]:
    """
    Converts a protobuf time series reply from Mesh server into Timeseries

    Raises:
        ValueError: no time series data
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
                            object_id.timskey, from_proto_guid(object_id.guid), object_id.full_name)
        else:
            ts = Timeseries(table, resolution,
                            interval.start_time, interval.end_time)

        timeseries.append(ts)
    return timeseries


def read_proto_numeric_reply(reply: core_pb2.ReadTimeseriesResponse) -> List[float]:
    """
    Converts a protobuf numeric calculation reply from Mesh server into a list of floats
    """
    results = []
    for v in reply.value:
        results.append(v)
    return results
