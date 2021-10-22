import uuid
import datetime

import pyarrow as pa

from volue.mesh import Timeseries
from volue.mesh.proto import mesh_pb2
from google.protobuf import timestamp_pb2


# ------------------------------------------------------------------------------

class TimeseriesTestdata:
    """Tests data structure."""

    def __init__(self, full_name, guid, timskey, start_time_ticks, start_time_json, end_time_ticks, end_time_json,
                 database):
        self.full_name = full_name
        self.guid = guid
        self.timskey = timskey
        self.start_time_ticks = start_time_ticks
        self.start_time_json = start_time_json
        self.end_time_ticks = end_time_ticks
        self.end_time_json = end_time_json
        self.database = database


# A smaller segment
# 01.05.2016 : 635976576000000000
# 14.05.2016 : 635987808000000000

eagle_wind = TimeseriesTestdata(
    "Resource/Wind Power/WindPower/WPModel/WindProdForec(0)",
    "3f1afdd7-5f7e-45f9-824f-a7adc09cff8e",
    201503,
    635103072000000000,  # 25/07/2013 00:00:00
    "2013-07-25T00:00:00Z",
    636182208000000000,  # 25/12/2016 00:00:00
    "2016-12-25T00:00:00Z",
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


def to_protobuf_timestamp(dot_net_ticks: int) -> timestamp_pb2.Timestamp:
    """Convert .NET ticks to protobuf timestamp.
    Note: A .NET tick is 100 nanoseconds which started at 0001-01-01T00:00:00Z
    Note: https://docs.microsoft.com/en-us/dotnet/api/system.datetime.ticks?view=net-5.0#remarks

    :param dot_net_ticks: windows ticks
    :return: Timestamp
    """
    if dot_net_ticks is None:
        return None
    date = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=dot_net_ticks // 10)
    if date.year < 1900:  # strftime() requires year >= 1900
        date = date.replace(year=date.year + 1900)
    ts = timestamp_pb2.Timestamp()
    ts.FromJsonString(date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    return ts


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
