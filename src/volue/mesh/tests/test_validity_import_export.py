import pytest
import threading
import time
import subprocess
import uuid

from datetime import datetime

from google.protobuf import timestamp_pb2

from volue import mesh

from volue.mesh._common import _to_proto_guid
from volue.mesh._mesh_id import _to_proto_object_mesh_id
from volue.mesh.proto import type
from volue.mesh.proto.model.v1alpha import model_pb2

BASE_DUMP_PATH = "C:/Users/martin.galvan/base_dump.mdump"
DUMP_WITH_VALIDITY_PATH = "C:/Users/martin.galvan/with_validity.mdump"
MESH_BUILD_PATH = "C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug"
MESH_EXE = f"{MESH_BUILD_PATH}/Powel.Mesh.Server.exe"
IMP_EXP_EXE = f"{MESH_BUILD_PATH}/Powel.Mesh.Model.ImportExport.exe"

OBJECT_ID = "{21893300-6482-4b09-b9ba-58b48740d0e7}"

# FIXME: The checks seem to break if we use datetime.fromisoformat("2024-12-04T00:00:00.000Z") since
# the return value from GetValidity doesn't seem to include the fractionary part.
FROM_DATE = "2024-12-04T00:00:00"
UNTIL_DATE = "2024-12-27T00:00:00"


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


@pytest.mark.parametrize(
    ("validity_info"),
    [
        ValidityInfo(
            datetime.fromisoformat(FROM_DATE), datetime.fromisoformat(UNTIL_DATE)
        ),
        ValidityInfo(None, datetime.fromisoformat(UNTIL_DATE)),
        ValidityInfo(datetime.fromisoformat(FROM_DATE), None),
    ],
)
class TestValidityImportExport:
    def test_set_validity(
        connection: mesh.Connection,
        validity_info: ValidityInfo,
    ):
        print("[MARTIN] Starting mesh...")

        mesh_proc = subprocess.Popen([MESH_EXE])

        # We need to use try/finally instead of 'with subprocess.Popen(...)' since for some reason we
        # won't be able to catch any exceptions until we terminate the mesh process.
        try:
            # Give mesh some time to finish starting up
            time.sleep(10)

            _generate_data_with_validity(connection, validity_info)
        finally:
            print("[MARTIN] Terminating mesh...")

            mesh_proc.terminate()

        print("[MARTIN] Starting mesh...")

        mesh_proc = subprocess.Popen([MESH_EXE])

        try:
            # Give mesh some time to finish starting up
            time.sleep(10)

            validity_info = _import_and_get_validity(connection)

            _check_validity(validity_info, expected_validity_info)
        finally:
            print("[MARTIN] Terminating mesh...")

            mesh_proc.terminate()

    def _generate_data_with_validity(
        connection: mesh.Connection, validity_info: ValidityInfo
    ):
        imp_args = [IMP_EXP_EXE, "-i", BASE_DUMP_PATH, "-S"]

        # Import the base data first
        print("[MARTIN] Importing base data...")

        # subprocess.check_call(imp_args)

        # Set validity for an object
        with connection.create_session() as session:
            # First, verify that the object doesn't have any validity info set
            response = _get_validity(session)

            print(f"[MARTIN] Validity of object before setting it: '{response}'")

            # Now, set the validity
            _set_validity(session, validity_info)

            session.commit()

        exp_args = [IMP_EXP_EXE, "-o", DUMP_WITH_VALIDITY_PATH, "-m", "MeshTEK"]

        # Export data with validity
        print("[MARTIN] Exporting data with validity...")

        subprocess.check_call(exp_args)

    def _import_and_get_validity(
        connection: mesh.Connection,
    ):
        imp_args = [IMP_EXP_EXE, "-i", DUMP_WITH_VALIDITY_PATH, "-S"]

        # Import the data with validity
        print("[MARTIN] Importing data with validity...")

        subprocess.check_call(imp_args)

        with connection.create_session() as session:
            response = _get_validity(session)

        validity_info = ValidityInfo(
            response.valid_from.ToDatetime(), response.valid_until.ToDatetime()
        )

        print(f"[MARTIN] Validity of object after importing it: '{validity_info}'")

        return validity_info

    def _set_validity(session, validity_info: ValidityInfo):
        print("[MARTIN] Setting validity for object...")

        valid_from = timestamp_pb2.Timestamp()
        valid_from.FromDatetime(validity_info.valid_from)

        valid_until = timestamp_pb2.Timestamp()
        valid_until.FromDatetime(validity_info.valid_until)

        request = model_pb2.UpdateValidityRequest(
            session_id=_to_proto_guid(session.session_id),
            object_id=_to_proto_object_mesh_id(OBJECT_ID),
            valid_from=valid_from,
            valid_until=valid_until,
        )

        response = session.model_service.UpdateValidity(request)

        print(f"[MARTIN] Done! Response: '{response}'")

    def _get_validity(session):
        print("[MARTIN] Getting validity for object...")

        request = model_pb2.GetValidityRequest(
            session_id=_to_proto_guid(session.session_id),
            object_id=_to_proto_object_mesh_id(OBJECT_ID),
        )

        response = session.model_service.GetValidity(request)

        print(f"[MARTIN] Done!")

        return response

    def _check_validity(
        validity_info: ValidityInfo, expected_validity_info: ValidityInfo
    ):
        if validity_info == expected_validity_info:
            print(f"[MARTIN] OK: '{validity_info}' == '{expected_validity_info}'")
        else:
            print(f"[MARTIN] ERROR: '{validity_info}' != '{expected_validity_info}'")


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
