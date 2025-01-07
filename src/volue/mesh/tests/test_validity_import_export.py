import pytest
import threading
import time
import subprocess
import uuid

from datetime import datetime

from google.protobuf import timestamp_pb2

from volue import mesh

from volue.mesh import _common, _mesh_id
from volue.mesh.proto import type
from volue.mesh.proto.model.v1alpha import model_pb2

BASE_DUMP_PATH = "C:/Users/martin.galvan/base_dump.mdump"
DUMP_WITH_VALIDITY_PATH = "C:/Users/martin.galvan/with_validity.mdump"
MESH_BUILD_PATH = "C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug"
MESH_EXE = f"{MESH_BUILD_PATH}/Powel.Mesh.Server.exe"
IMP_EXP_EXE = f"{MESH_BUILD_PATH}/Powel.Mesh.Model.ImportExport.exe"

# FIXME: The checks seem to break if we use datetime.fromisoformat("2024-12-04T00:00:00.000Z") since
# the return value from GetValidity doesn't seem to include the fractionary part.
FROM_DATE = datetime.fromisoformat("2024-12-04T00:00:00")
UNTIL_DATE = datetime.fromisoformat("2024-12-27T00:00:00")

class ValidityInfo:
    def __init__(self, valid_from: datetime=None, valid_until: datetime=None):
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

    def to_proto_timestamps(self) -> tuple[timestamp_pb2.Timestamp, timestamp_pb2.Timestamp]:
        valid_from = None
        valid_until = None

        if self.valid_from != None:
            valid_from = timestamp_pb2.Timestamp()
            valid_from.FromDatetime(self.valid_from)

        if self.valid_until != None:
            valid_until = timestamp_pb2.Timestamp()
            valid_until.FromDatetime(self.valid_until)

        return (valid_from, valid_until)

    def from_proto_timestamps(self, valid_from: timestamp_pb2.Timestamp, valid_until: timestamp_pb2.Timestamp):
        self.valid_from = None
        self.valid_until = None

        if valid_from != None:
            self.valid_from.ToDatetime(valid_from)

        if valid_until != None:
            self.valid_until.ToDatetime(valid_until)


# We set various combinations of validity values for different objects at the same time on each test.
# This is more efficient than doing the entire export/import cycle on a single object for each
# combination of validity values.
VALIDITY_TEST_DATA = {
    # Models->MeshTEK->Mesh->To_Areas->Finland
    uuid.UUID("{21893300-6482-4b09-b9ba-58b48740d0e7}"): ValidityInfo(FROM_DATE, UNTIL_DATE),
    # Models->MeshTEK->Mesh->To_Areas->Norge
    uuid.UUID("{f06e67ed-61a6-4700-ac40-df80d752aeba}"): ValidityInfo(None, UNTIL_DATE),
    # Models->MeshTEK->Mesh->EnergySystemVersion->EnergySystemVersion
    uuid.UUID("{b292fde5-feb8-4bd2-95a4-d7b5022b9734}"): ValidityInfo(FROM_DATE, None),
}

# @pytest.mark.parametrize(
#     ("validity_info"),
#     [
#         ValidityInfo(FROM_DATE, UNTIL_DATE),
#         ValidityInfo(None, UNTIL_DATE),
#         ValidityInfo(FROM_DATE, None),
#     ],
# )
class TestValidityImportExport:
    def test_set_validity(self, connection: mesh.Connection)#, validity_info: ValidityInfo):
        print("[MARTIN] Starting mesh...")

        mesh_proc = subprocess.Popen([MESH_EXE])

        # We need to use try/finally instead of 'with subprocess.Popen(...)' since for some reason we
        # won't be able to catch any exceptions until we terminate the mesh process.
        try:
            # Give mesh some time to finish starting up
            time.sleep(10)

            self._generate_data_with_validity(connection)#, validity_info)
        finally:
            print("[MARTIN] Terminating mesh...")

            mesh_proc.terminate()

        print("[MARTIN] Starting mesh...")

        mesh_proc = subprocess.Popen([MESH_EXE])

        try:
            # Give mesh some time to finish starting up
            time.sleep(10)

            imported_validity_info = self._import_and_get_validity(connection)
        finally:
            print("[MARTIN] Terminating mesh...")

            mesh_proc.terminate()

        assert imported_validity_info == VALIDITY_TEST_DATA

    def _generate_data_with_validity(
        self, connection: mesh.Connection#, validity_info: ValidityInfo
    ):
        imp_args = [IMP_EXP_EXE, "-i", BASE_DUMP_PATH, "-S"]

        # Import the base data first
        print("[MARTIN] Importing base data...")

        subprocess.check_call(imp_args)

        # Set validity for an object
        with connection.create_session() as session:
            for object_id, validity_info in VALIDITY_TEST_DATA.items():
                # First, verify that the object doesn't have any validity info set
                response = self._get_validity(session)

                print(f"[MARTIN] Validity of object '{object_id}' before setting it: '{response}'")

                # Now, set the validity
                self._set_validity(session, object_id, validity_info)

            session.commit()

        exp_args = [IMP_EXP_EXE, "-o", DUMP_WITH_VALIDITY_PATH, "-m", "MeshTEK"]

        # Export data with validity
        print("[MARTIN] Exporting data with validity...")

        subprocess.check_call(exp_args)

    def _import_and_get_validity(self, connection: mesh.Connection) -> dict[uuid.UUID, ValidityInfo]:
        result = {}
        imp_args = [IMP_EXP_EXE, "-i", DUMP_WITH_VALIDITY_PATH, "-S"]

        # Import the data with validity
        print("[MARTIN] Importing data with validity...")

        subprocess.check_call(imp_args)

        with connection.create_session() as session:
            for object_id in VALIDITY_TEST_DATA:
                response = self._get_validity(session, object_id)
                validity_info = ValidityInfo().from_proto_timestamps(response.valid_from, response.valid_until)

            result[object_id] = validity_info

            print(f"[MARTIN] Validity of object '{object_id}' after importing it: '{validity_info}'")

        return result

    def _set_validity(self, session: mesh.Connection.Session, object_id: uuid.UUID, validity_info: ValidityInfo):
        print("[MARTIN] Setting validity for object...")

        valid_from, valid_until = validity_info.to_proto_timestamps()

        request = model_pb2.UpdateValidityRequest(
            session_id=_common._to_proto_guid(session.session_id),
            object_id=_mesh_id._to_proto_object_mesh_id(object_id),
            valid_from=valid_from,
            valid_until=valid_until,
        )

        response = session.model_service.UpdateValidity(request)

        print(f"[MARTIN] Done! Response: '{response}'")

    def _get_validity(self, session: mesh.Connection.Session, object_id: uuid.UUID) -> model_pb2.GetValidityResponse:
        print("[MARTIN] Getting validity for object...")

        request = model_pb2.GetValidityRequest(
            session_id=_common._to_proto_guid(session.session_id),
            object_id=_mesh_id._to_proto_object_mesh_id(object_id),
        )

        response = session.model_service.GetValidity(request)

        print(f"[MARTIN] Done!")

        return response


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
