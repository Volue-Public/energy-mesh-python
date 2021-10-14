import uuid
import datetime
from volue.mesh.proto.mesh_pb2 import Guid as ProtoGuid
from google.protobuf.timestamp_pb2 import Timestamp
from volue.mesh.proto.mesh_pb2 import UtcInterval


def uuid_to_guid(uuid: uuid.UUID) -> ProtoGuid:
    """Convert from UUID format to Microsoft's GUID format.

    :param uuid: UUID
    :return: GUID
    """
    if (uuid is None):
        return None
    return ProtoGuid(bytes_le=uuid.bytes_le)


def guid_to_uuid(guid: ProtoGuid) -> uuid.UUID:
    """Convert from Microsoft's GUID format to UUID format.

    :param guid: GUID to be converted
    :return: UUID
    """
    if (guid is None):
        return None
    return uuid.UUID(bytes_le=guid)


def datetime_to_protobuf_utcinterval(start_time: datetime, end_time: datetime) -> UtcInterval:
    """Convert to protobuf UtcInterval."""
    start = Timestamp()
    start.FromDatetime(start_time)
    end = Timestamp()
    end.FromDatetime(end_time)
    interval = UtcInterval(
        start_time=start,
        end_time=end
    )
    return interval


def dot_net_ticks_to_protobuf_timestamp(ticks: int) -> Timestamp:
    """Convert .NET ticks to protobuf timestamp.
    Note: A .NET tick is 100 nanoseconds which started at 0001-01-01T00:00:00Z
    Note: https://docs.microsoft.com/en-us/dotnet/api/system.datetime.ticks?view=net-5.0#remarks

    :param ticks: windows ticks
    :return: Timestamp
    """
    if (ticks is None):
        return None
    date = datetime.datetime(1, 1, 1) + \
           datetime.timedelta(microseconds=ticks // 10)
    if date.year < 1900:  # strftime() requires year >= 1900
        date = date.replace(year=date.year + 1900)
    ts = Timestamp()
    ts.FromJsonString(date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    return ts


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
