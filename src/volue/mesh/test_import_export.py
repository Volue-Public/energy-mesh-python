import threading
import time
import subprocess
import uuid

from datetime import datetime

from google.protobuf import timestamp_pb2

from volue import mesh

from volue.mesh.proto import type
from volue.mesh.proto.model.v1alpha import model_pb2


class ValidityInfo:
    def __init__(self, valid_from: datetime.time, valid_until: datetime.time):
        self.valid_from = valid_from
        self.valid_until = valid_until


    def __str__(self):
        return f"valid_from: '{self.valid_from.isoformat}'; valid_until: '{self.valid_until.isoformat()}'"


    def __eq__(self, other):
        if isinstance(other, ValidityInfo):
            self.valid_from == other.valid_from
            self.valid_until == other.valid_until
        else:
            raise TypeError("'other' is not an instance of ValidityInfo")


def main():
    connection = mesh.Connection.insecure("localhost:50051")

    mesh_build_path = "C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug"
    mesh_exe = f"{mesh_build_path}/Powel.Mesh.Server.exe"
    imp_exp_exe = f"{mesh_build_path}/Powel.Mesh.Model.ImportExport.exe"
    dump_with_validity_path = "C:/Users/martin.galvan/with_validity.mdump"

    # This is the ID of Models->MeshTEK->Mesh->To_Areas->Finland
    object_id = uuid.UUID("{21893300-6482-4b09-b9ba-58b48740d0e7}")

    valid_from = datetime.fromisoformat("2024-12-04T00:00:00.000Z")
    valid_until = datetime.fromisoformat("2024-12-27T00:00:00.000Z")
    expected_validity_info = ValidityInfo(valid_from, valid_until)

    print("[MARTIN] Starting mesh...")

    mesh_proc = subprocess.Popen([mesh_exe])

    # We need to use try/finally instead of 'with subprocess.Popen(...)' since for some reason we
    # won't be able to catch any exceptions until we terminate the mesh process.
    try:
        # Give mesh some time to finish starting up
        time.sleep(10)


        generate_data_with_validity(
            connection, imp_exp_exe, dump_with_validity_path, object_id, expected_validity_info
        )

        print("[MARTIN] Terminating mesh...")
    finally:
        mesh_proc.terminate()

    print("[MARTIN] Starting mesh...")

    mesh_proc = subprocess.Popen(mesh_exe)

    try:
        # Give mesh some time to finish starting up
        time.sleep(10)

        validity_info = import_and_get_validity(
            connection, imp_exp_exe, dump_with_validity_path, object_id
        )

        check_validity(validity_info, expected_validity_info)
    finally:
        print("[MARTIN] Terminating mesh...")

        mesh_proc.terminate()


def generate_data_with_validity(
    connection: mesh.Connection,
    imp_exp_exe: str,
    dump_with_validity_path: str,
    object_id: str,
    validity_info: ValidityInfo
):
    imp_args = [imp_exp_exe, "-i", "C:/Users/martin.galvan/base_dump.mdump", "-S"]

    # Import the base data first
    print("[MARTIN] Importing base data...")

    subprocess.check_call(imp_args)

    # Set validity for an object
    with connection.create_session() as session:
        # First, verify that the object doesn't have any validity info set
        response = get_validity(session, object_id)

        print(f"[MARTIN] Validity of object before setting it: '{response}'")

        # Now, set the validity
        set_validity(session, object_id, validity_info)

        session.commit()

    exp_args = [imp_exp_exe, "-o", dump_with_validity_path, "-m", "MeshTEK"]

    # Export data with validity
    print("[MARTIN] Exporting data with validity...")

    subprocess.check_call(exp_args)


def import_and_get_validity(
    connection: mesh.Connection,
    imp_exp_exe: str,
    dump_with_validity_path: str,
    object_id: str,
):
    imp_args = [imp_exp_exe, "-i", dump_with_validity_path, "-S"]

    # Import the data with validity
    print("[MARTIN] Importing data with validity...")

    subprocess.check_call(imp_args)

    with connection.create_session() as session:
        response = get_validity(session, object_id)

    validity_info = ValidityInfo(response.valid_from.ToDatetime(), response.valid_until.ToDatetime())

    print(f"[MARTIN] Validity of object after importing it: '{validity_info}'")

    return validity_info


def set_validity(session, object_id: str, validity_info: ValidityInfo):
    print("[MARTIN] Setting validity for object...")

    valid_from = timestamp_pb2.Timestamp()
    valid_from.FromDatetime(validity_info.valid_from)

    valid_until = timestamp_pb2.Timestamp()
    valid_until.FromDatetime(validity_info.valid_until)

    request = model_pb2.UpdateValidityRequest(
        session_id=to_proto_guid(session.session_id),
        object_id=to_proto_mesh_id(object_id),
        valid_from=valid_from,
        valid_until=valid_until,
    )

    response = session.model_service.UpdateValidity(request)

    print(f"[MARTIN] Done! Response: '{response}'")


def get_validity(session, object_id: str):
    print("[MARTIN] Getting validity for object...")

    request = model_pb2.GetValidityRequest(
        session_id=to_proto_guid(session.session_id),
        object_id=to_proto_mesh_id(object_id),
    )

    response = session.model_service.GetValidity(request)

    print(f"[MARTIN] Done!")

    return response


def check_validity(validity_info: ValidityInfo, expected_validity_info: ValidityInfo)
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
