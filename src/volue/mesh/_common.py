import uuid
import datetime

import pyarrow as pa

from volue.mesh import Timeseries
from volue.mesh.proto import mesh_pb2
from google.protobuf import timestamp_pb2


# ------------------------------------------------------------------------------

class TimeseriesTestdata:
    """Tests data structure."""

    def __init__(self, full_name, guid, timskey, start_time, end_time, database):
        self.full_name = full_name
        self.guid = guid
        self.timskey = timskey
        self.start_time = start_time
        self.end_time = end_time
        self.database = database


eagle_wind = TimeseriesTestdata(
    "Resource/Wind Power/WindPower/WPModel/WindProdForec(0)",
    "3f1afdd7-5f7e-45f9-824f-a7adc09cff8e",
    201503,
    datetime.datetime(year=2016, month=5, day=1, hour=0, minute=0),
    datetime.datetime(year=2016, month=5, day=14, hour=0, minute=0),
    "eagle"
)


# ------------------------------------------------------------------------------

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


def read_proto_reply(reply: mesh_pb2.ReadTimeseriesResponse) -> [Timeseries]:
    """Converts a timeseries reply into a Timeseries """
    timeseries = []
    for timeserie in reply.timeseries:
        resolution = timeserie.resolution
        object_id = timeserie.object_id
        interval = timeserie.interval
        reader = pa.ipc.open_stream(timeserie.data)
        table = reader.read_all()
        ts = Timeseries(table, resolution,
                        interval.start_time, interval.end_time,
                        object_id.timskey, from_proto_guid(object_id.guid), object_id.full_name)
        timeseries.append(ts)
    return timeseries
