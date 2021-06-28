import uuid
from volue.mesh.proto import mesh_pb2

def uuid_to_guid(id: uuid.UUID) -> mesh_pb2.Guid:
    if (id is None):
        return None
    return mesh_pb2.Guid(bytes_le=id.bytes_le)


def guid_to_uuid(id: mesh_pb2.Guid) -> uuid.UUID:
    if (id is None):
        return None
    return uuid.UUID(bytes_le=id)