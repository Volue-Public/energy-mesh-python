import uuid
import datetime
from volue.mesh.proto import mesh_pb2

from google.protobuf.timestamp_pb2 import Timestamp

def uuid_to_guid(uuid: uuid.UUID) -> mesh_pb2.Guid:
    """Convert from UUID format to Microsofts GUID format.

    :param uuid: UUID
    :return: GUID
    """
    if (uuid is None):
        return None
    return mesh_pb2.Guid(bytes_le=uuid.bytes_le)


def guid_to_uuid(guid: mesh_pb2.Guid) -> uuid.UUID:
    """Convert from Microsofts GUID format to UUID format.

    :param guid: GUID to be converted
    :return: UUID
    """
    if (guid is None):
        return None
    return uuid.UUID(bytes_le=guid)


def windows_ticks_to_protobuf_timestamp(ticks: int) -> Timestamp:
    """Convert Windows ticks to protobuf timestamp.
    Note: A Windows tick is 100 nanoseconds. Windows epoch 1601-01-01T00:00:00Z

    :param ticks: windows ticks
    :return: Timestamp
    """
    if(ticks is None):
        return None
    date = datetime.datetime(1, 1, 1) + \
        datetime.timedelta(microseconds=ticks // 10)
    if date.year < 1900:  # strftime() requires year >= 1900
        date = date.replace(year=date.year + 1900)
    ts = Timestamp()
    ts.FromJsonString(date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    return ts


