import threading
import time
import subprocess
import uuid

from google.protobuf import timestamp_pb2

from volue import mesh


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

    print("[MARTIN] Starting mesh...")

    with subprocess.Popen(mesh_exe) as mesh_proc:
        # Give mesh some time to finish starting up
        time.sleep(10)

        import_and_check_validity(connection, imp_exp_exe, dump_with_validity_path)

        print("[MARTIN] Terminating mesh...")

        mesh_proc.terminate()

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

    exp_args = [imp_exp_exe, "-o", dump_with_validity_path, "-m", "MeshTEK"]

    # Export data with validity
    print("[MARTIN] Exporting data with validity...")

    subprocess.check_call(exp_args)


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
    # Llamar a UpdateValidity de protobuf

    valid_from_datetime = datetime.fromisoformat("2024-12-04T00:00:00.000Z")
    valid_from = timestamp_pb2.Timestamp()
    valid_from.FromDatetime(valid_from_datetime)

    valid_until_datetime = datetime.fromisoformat("2024-12-27T00:00:00.000Z")
    valid_until = timestamp_pb2.Timestamp()
    valid_until.FromDatetime(valid_until_datetime)

    object_id = uuid.UUID("{21893300-6482-4b09-b9ba-58b48740d0e7}")

    request = time_series_pb2.UpdateValidityRequest(
        session_id=_to_proto_guid(session_id.session_id),
        object_id=_to_proto_guid(object_id),
        valid_from=valid_from,
        valid_until=valid_until,
    )

    response = session.model_service.UpdateValidity(request)

    print(response)

    # unit_of_measurement_id = self._get_unit_of_measurement_id_by_name(
    #     unit_of_measurement
    # )

    # request = time_series_pb2.CreatePhysicalTimeseriesRequest(
    #     session_id=_to_proto_guid(self.session_id),
    #     path=path,
    #     name=name,
    #     curve_type=_to_proto_curve_type(curve_type),
    #     resolution=_to_proto_resolution(resolution),
    #     unit_of_measurement_id=unit_of_measurement_id,
    # )

    # response = self.time_series_service.CreatePhysicalTimeseries(request)

    # return TimeseriesResource._from_proto_timeseries_resource(response)


if __name__ == "__main__":
    main()
