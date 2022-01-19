import uuid
import datetime
from enum import Enum
from typing import List

import pyarrow as pa

from volue.mesh import Timeseries
from volue.mesh.proto import mesh_pb2
from google.protobuf import timestamp_pb2

class CalendarType(Enum):
    LOCAL    = 0
    DATABASE = 1
    UTC      = 2
    UNKNOWN  = 3  # TODO: should we expose it? Is it used in some scenario?


# TODO: there is already a Resolution enum in Timeseries, but it contains 'BREAKPOINT' and is missing 'MIN', 'MIN5' and 'MIN10'
class TransformationResolution(Enum):
    MIN   = 0
    MIN5  = 1
    MIN10 = 2
    MIN15 = 3
    HOUR  = 4
    DAY   = 5
    WEEK  = 6
    MONTH = 7
    YEAR  = 8

class TransformationMethod(Enum):
    SUM   = 0
    SUMI  = 1
    AVG   = 2  # equivalent to MEAN
    AVGI  = 3
    FIRST = 5
    LAST  = 6
    MIN   = 7
    MAX   = 8

def to_proto_guid(uuid: uuid.UUID) -> mesh_pb2.Guid:
    """Convert from UUID format to Microsoft's GUID format.

    :param uuid: UUID
    :return: GUID
    """
    if uuid is None:
        return None
    return mesh_pb2.Guid(bytes_le=uuid.bytes_le)


def from_proto_guid(guid: mesh_pb2.Guid) -> uuid.UUID:
    """Convert from Microsoft's GUID format to UUID format.

    :param guid: GUID to be converted
    :return: UUID
    """
    if guid is None:
        return None
    return uuid.UUID(bytes_le=guid.bytes_le)


def to_proto_curve_type(curve: Timeseries.Curve) -> mesh_pb2.Curve:
    proto_curve = mesh_pb2.Curve()
    proto_curve.type = mesh_pb2.Curve.UNKNOWN
    if curve == Timeseries.Curve.PIECEWISELINEAR:
        proto_curve.type = mesh_pb2.Curve.PIECEWISELINEAR
    elif curve == Timeseries.Curve.STAIRCASE:
        proto_curve.type = mesh_pb2.Curve.STAIRCASE
    elif curve == Timeseries.Curve.STAIRCASESTARTOFSTEP:
        proto_curve.type = mesh_pb2.Curve.STAIRCASESTARTOFSTEP

    return proto_curve



def to_protobuf_utcinterval(start_time: datetime, end_time: datetime) -> mesh_pb2.UtcInterval:
    """Convert to protobuf UtcInterval."""
    start = timestamp_pb2.Timestamp()
    start.FromDatetime(start_time)
    end = timestamp_pb2.Timestamp()
    end.FromDatetime(end_time)
    interval = mesh_pb2.UtcInterval(
        start_time=start,
        end_time=end
    )
    return interval


def to_proto_object_id(timeseries: Timeseries) -> mesh_pb2.ObjectId:
    """Convert a Timeseries to corresponding protobuf ObjectId"""
    return mesh_pb2.ObjectId(
        timskey=timeseries.timskey,
        guid=to_proto_guid(timeseries.uuid),
        full_name=timeseries.full_name
    )


def to_proto_timeseries(timeseries: Timeseries) -> mesh_pb2.Timeseries:
    """Convert a Timeseries to corresponding protobuf Timeseries"""
    stream = pa.BufferOutputStream()
    writer = pa.ipc.RecordBatchStreamWriter(
        sink=stream,
        schema=timeseries.arrow_table.schema
    )

    writer.write_table(timeseries.arrow_table)
    buffer = stream.getvalue()

    proto_timeserie = mesh_pb2.Timeseries(
        object_id=to_proto_object_id(timeseries),
        resolution=timeseries.resolution,
        interval=to_protobuf_utcinterval(start_time=timeseries.start_time, end_time=timeseries.end_time),
        data=buffer.to_pybytes()
    )
    return proto_timeserie


def read_proto_reply(reply: mesh_pb2.ReadTimeseriesResponse) -> List[Timeseries]:
    """Converts a timeseries reply into a Timeseries

    Returns:
        object:
    """
    timeseries = []
    for timeserie in reply.timeseries:
        resolution = timeserie.resolution
        interval = timeserie.interval
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
