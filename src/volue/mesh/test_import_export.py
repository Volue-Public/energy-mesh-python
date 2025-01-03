import threading
import time
import subprocess
import uuid

from datetime import datetime

from google.protobuf import timestamp_pb2

from volue import mesh

from volue.mesh.proto import type
from volue.mesh.proto.model.v1alpha import model_pb2


def main():
    connection = mesh.Connection.insecure("localhost:50051")

    mesh_build_path = "C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug"
    mesh_exe = f"{mesh_build_path}/Powel.Mesh.Server.exe"
    imp_exp_exe = f"{mesh_build_path}/Powel.Mesh.Model.ImportExport.exe"
    dump_with_validity_path = "C:/Users/martin.galvan/with_validity.mdump"

    print("[MARTIN] Starting mesh...")

    with subprocess.Popen([mesh_exe]) as mesh_proc:
        # Give mesh some time to finish starting up
        time.sleep(10)

        generate_data_with_validity(connection, imp_exp_exe, dump_with_validity_path)

        print("[MARTIN] Terminating mesh...")

        mesh_proc.terminate()

    # print("[MARTIN] Starting mesh...")

    # with subprocess.Popen(mesh_exe) as mesh_proc:
    #     # Give mesh some time to finish starting up
    #     time.sleep(10)

    #     import_and_check_validity(connection, imp_exp_exe, dump_with_validity_path)

    #     print("[MARTIN] Terminating mesh...")

    #     mesh_proc.terminate()

    # check_validity()


def generate_data_with_validity(
    connection: mesh.Connection, imp_exp_exe: str, dump_with_validity_path: str
):
    imp_args = [imp_exp_exe, "-i", "C:/Users/martin.galvan/base_dump.mdump", "-S"]

    # Import the base data first
    print("[MARTIN] Importing base data...")

    subprocess.check_call(imp_args)

    # Set validity for an object (Models->MeshTEK->Mesh->To_Areas->Finland)
    with connection.create_session() as session:
        set_validity(session)

        session.commit()

    # exp_args = [imp_exp_exe, "-o", dump_with_validity_path, "-m", "MeshTEK"]

    # # Export data with validity
    # print("[MARTIN] Exporting data with validity...")

    # subprocess.check_call(exp_args)


def import_and_check_validity(
    connection: mesh.Connection, imp_exp_exe: str, dump_with_validity_path: str
):
    imp_args = [imp_exp_exe, "-i", dump_with_validity_path, "-S"]

    # Import the data with validity
    print("[MARTIN] Importing data with validity...")

    subprocess.check_call(imp_args)

    with connection.create_session() as session:
        pass
        # get_validity()


def set_validity(session):
    print("[MARTIN] Setting validity for object...")

    valid_from_datetime = datetime.fromisoformat("2024-12-04T00:00:00.000Z")
    valid_from = timestamp_pb2.Timestamp()
    valid_from.FromDatetime(valid_from_datetime)

    valid_until_datetime = datetime.fromisoformat("2024-12-27T00:00:00.000Z")
    valid_until = timestamp_pb2.Timestamp()
    valid_until.FromDatetime(valid_until_datetime)

    object_id = uuid.UUID("{21893300-6482-4b09-b9ba-58b48740d0e7}")

    request = model_pb2.UpdateValidityRequest(
        session_id=to_proto_guid(session.session_id),
        object_id=to_proto_guid(object_id),
        valid_from=valid_from,
        valid_until=valid_until,
    )

    response = session.model_service.UpdateValidity(request)

    print(f"[MARTIN] Done! Response: '{response}'")


def to_proto_guid(uuid: uuid.UUID):
    return type.resources_pb2.Guid(bytes_le=uuid.bytes_le)


if __name__ == "__main__":
    main()
