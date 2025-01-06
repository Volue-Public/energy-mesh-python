import threading
import time
import subprocess
import uuid

from datetime import datetime

from google.protobuf import timestamp_pb2

from volue import mesh

from volue.mesh.proto import type
from volue.mesh.proto.model.v1alpha import model_pb2

BASE_DUMP_PATH = "C:/Users/martin.galvan/base_dump.mdump"
DUMP_WITH_VALIDITY_PATH = "C:/Users/martin.galvan/with_validity.mdump"
MESH_BUILD_PATH = "C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug"
MESH_EXE = f"{MESH_BUILD_PATH}/Powel.Mesh.Server.exe"
IMP_EXP_EXE = f"{MESH_BUILD_PATH}/Powel.Mesh.Model.ImportExport.exe"

# This is the ID of Models->MeshTEK->Mesh->To_Areas->Finland
OBJECT_ID = uuid.UUID("{21893300-6482-4b09-b9ba-58b48740d0e7}")


class ValidityInfo:
    def __init__(self, valid_from: datetime, valid_until: datetime):
        self.valid_from = valid_from
        self.valid_until = valid_until

    def __str__(self):
        return f"valid_from: '{self.valid_from}'; valid_until: '{self.valid_until}'"

    def __eq__(self, other):
        if isinstance(other, ValidityInfo):
            return (
                self.valid_from == other.valid_from
                and self.valid_until == other.valid_until
            )
        else:
            return NotImplemented


def main():
    connection = mesh.Connection.insecure("localhost:50051")

    # FIXME: The checks seem to break if I use datetime.fromisoformat("2024-12-04T00:00:00.000Z")
    # since the return value from GetValidity is different from what we have here.
    valid_from = datetime.fromisoformat("2024-12-04T00:00:00")
    valid_until = datetime.fromisoformat("2024-12-27T00:00:00")
    expected_validity_info = ValidityInfo(valid_from, valid_until)

    print("[MARTIN] Starting mesh...")

    # Set only 'from'
    test_set_validity(connection, ValidityInfo(valid_from, None))

    # Set only 'until'
    test_set_validity(connection, ValidityInfo(None, valid_until))

    # Set both 'from' and 'until'
    test_set_validity(connection, ValidityInfo(valid_from, valid_until))

    # test_update_from_until
    # test_update_from
    # test_update_until
    # test_remove_from
    # test_remove_until
    # test_remove_from_until


def test_set_validity(
    connection: mesh.Connection,
    expected_validity_info: ValidityInfo,
):
    mesh_proc = subprocess.Popen([MESH_EXE])

    # We need to use try/finally instead of 'with subprocess.Popen(...)' since for some reason we
    # won't be able to catch any exceptions until we terminate the mesh process.
    try:
        # Give mesh some time to finish starting up
        time.sleep(10)

        generate_data_with_validity(connection, expected_validity_info)
    finally:
        print("[MARTIN] Terminating mesh...")

        mesh_proc.terminate()

    print("[MARTIN] Starting mesh...")

    mesh_proc = subprocess.Popen([MESH_EXE])

    try:
        # Give mesh some time to finish starting up
        time.sleep(10)

        validity_info = import_and_get_validity(connection)

        check_validity(validity_info, expected_validity_info)
    finally:
        print("[MARTIN] Terminating mesh...")

        mesh_proc.terminate()


def generate_data_with_validity(
    connection: mesh.Connection, validity_info: ValidityInfo
):
    imp_args = [IMP_EXP_EXE, "-i", BASE_DUMP_PATH, "-S"]

    # Import the base data first
    print("[MARTIN] Importing base data...")

    subprocess.check_call(imp_args)

    # Set validity for an object
    with connection.create_session() as session:
        # First, verify that the object doesn't have any validity info set
        response = get_validity(session, OBJECT_ID)

        print(f"[MARTIN] Validity of object before setting it: '{response}'")

        # Now, set the validity
        set_validity(session, OBJECT_ID, validity_info)

        session.commit()

    exp_args = [IMP_EXP_EXE, "-o", DUMP_WITH_VALIDITY_PATH, "-m", "MeshTEK"]

    # Export data with validity
    print("[MARTIN] Exporting data with validity...")

    subprocess.check_call(exp_args)


def import_and_get_validity(
    connection: mesh.Connection,
):
    imp_args = [IMP_EXP_EXE, "-i", DUMP_WITH_VALIDITY_PATH, "-S"]

    # Import the data with validity
    print("[MARTIN] Importing data with validity...")

    subprocess.check_call(imp_args)

    with connection.create_session() as session:
        response = get_validity(session)

    validity_info = ValidityInfo(
        response.valid_from.ToDatetime(), response.valid_until.ToDatetime()
    )

    print(f"[MARTIN] Validity of object after importing it: '{validity_info}'")

    return validity_info


def set_validity(session, validity_info: ValidityInfo):
    print("[MARTIN] Setting validity for object...")

    valid_from = timestamp_pb2.Timestamp()
    valid_from.FromDatetime(validity_info.valid_from)

    valid_until = timestamp_pb2.Timestamp()
    valid_until.FromDatetime(validity_info.valid_until)

    request = model_pb2.UpdateValidityRequest(
        session_id=to_proto_guid(session.session_id),
        object_id=to_proto_mesh_id(OBJECT_ID),
        valid_from=valid_from,
        valid_until=valid_until,
    )

    response = session.model_service.UpdateValidity(request)

    print(f"[MARTIN] Done! Response: '{response}'")


def get_validity(session):
    print("[MARTIN] Getting validity for object...")

    request = model_pb2.GetValidityRequest(
        session_id=to_proto_guid(session.session_id),
        object_id=to_proto_mesh_id(OBJECT_ID),
    )

    response = session.model_service.GetValidity(request)

    print(f"[MARTIN] Done!")

    return response


def check_validity(validity_info: ValidityInfo, expected_validity_info: ValidityInfo):
    if validity_info == expected_validity_info:
        print(f"[MARTIN] OK: '{validity_info}' == '{expected_validity_info}'")
    else:
        print(f"[MARTIN] ERROR: '{validity_info}' != '{expected_validity_info}'")


def to_proto_mesh_id(uuid: uuid.UUID):
    proto_mesh_id = type.resources_pb2.MeshId()

    proto_mesh_id.id.CopyFrom(to_proto_guid(uuid))

    return proto_mesh_id


def to_proto_guid(uuid: uuid.UUID):
    return type.resources_pb2.Guid(bytes_le=uuid.bytes_le)


if __name__ == "__main__":
    main()
