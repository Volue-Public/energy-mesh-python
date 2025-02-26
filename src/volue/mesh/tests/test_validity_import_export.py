import time
import subprocess
import sys
import tempfile
import uuid

from collections.abc import Callable
from datetime import datetime, timedelta

import pytest

from google.protobuf import timestamp_pb2

from volue import mesh

from volue.mesh import _common, _mesh_id
from volue.mesh.proto.model.v1alpha import model_pb2

BASE_DUMPS_PATH = "C:/Users/martin.galvan"
BASE_DUMP_OLD_MESH = f"{BASE_DUMPS_PATH}/base_dump_old_mesh.mdump"
BASE_DUMP_NEW_MESH = f"{BASE_DUMPS_PATH}/base_dump_new_mesh.mdump"
MESH_BUILD_PATH = "C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Debug"

# FIXME: The checks seem to break if we use datetime.fromisoformat("1990-08-21T00:00:00.000Z") since
# the return value from GetValidity doesn't seem to include the fractionary part.
FROM_DATE = datetime.fromisoformat("1990-08-21T00:00:00")
UNTIL_DATE = FROM_DATE + timedelta(days=1)

# We set various combinations of validity values for different objects at the same time on each test.
# This is more efficient than doing the entire export/import cycle on a single object for each
# combination of validity values.
# Note that the target objects must be of type AttributeElement or Component.

# Models->MeshTEK->Mesh->To_Areas->Finland
MESH_TO_AREAS_FINLAND_ID = uuid.UUID("{21893300-6482-4b09-b9ba-58b48740d0e7}")

# Models->MeshTEK->Mesh->To_Areas->Norge
MESH_TO_AREAS_NORGE_ID = uuid.UUID("{f06e67ed-61a6-4700-ac40-df80d752aeba}")

# Models->MeshTEK->Mesh->has_Market->Market->has_EnergyMarketFlows->NO1
MESH_MARKET_ENERGY_MARKET_FLOWS_NO1_ID = uuid.UUID("{478f13d3-6e40-4db7-ae5b-3544ce04c546}")

# Models->MeshTEK->Mesh->has_Market->Market->has_EnergyMarketFlows->NO3
MESH_MARKET_ENERGY_MARKET_FLOWS_NO3_ID = uuid.UUID("{f00dcb8c-3dfd-4f6d-9f46-052d0843886b}")


@pytest.fixture
def dumps_path():
    return tempfile.TemporaryDirectory()


class ValidityInterval:
    def __init__(self, valid_from: datetime = None, valid_until: datetime = None):
        self.valid_from = valid_from
        self.valid_until = valid_until

    def __str__(self):
        return f"valid_from: '{self.valid_from}'; valid_until: '{self.valid_until}'"

    def __eq__(self, other):
        if isinstance(other, ValidityInterval):
            return (self.valid_from == other.valid_from and
                    self.valid_until == other.valid_until)
        else:
            return NotImplemented


    def to_proto_timestamps(
        self,
    ) -> tuple[timestamp_pb2.Timestamp, timestamp_pb2.Timestamp]:
        valid_from = None
        valid_until = None

        if self.valid_from is not None:
            valid_from = timestamp_pb2.Timestamp()
            valid_from.FromDatetime(self.valid_from)

        if self.valid_until is not None:
            valid_until = timestamp_pb2.Timestamp()
            valid_until.FromDatetime(self.valid_until)

        return (valid_from, valid_until)


    def from_proto_timestamps(
        self, valid_from: timestamp_pb2.Timestamp, valid_until: timestamp_pb2.Timestamp
    ):
        self.valid_from = None
        self.valid_until = None

        if valid_from is not None:
            self.valid_from = valid_from.ToDatetime()

        if valid_until is not None:
            self.valid_until = valid_until.ToDatetime()

        return self


# -k TestValidityImportExport
class TestValidityImportExport:
    def test_set_validity(self, connection: mesh.Connection, dumps_path: tempfile.TemporaryDirectory):
        dump_with_validity_path = f"{dumps_path.name}/with_validity.mdump"

        validity_test_data = {
            MESH_TO_AREAS_FINLAND_ID: ValidityInterval(FROM_DATE, UNTIL_DATE),
            MESH_TO_AREAS_NORGE_ID: ValidityInterval(FROM_DATE, None),
            MESH_MARKET_ENERGY_MARKET_FLOWS_NO1_ID: ValidityInterval(None, UNTIL_DATE),
        }

        self._generate_and_export_data_with_validity(connection, validity_test_data, dump_with_validity_path)

        imported_validity_data = dict.fromkeys(validity_test_data, None)

        def import_data_with_validity(connection: mesh.Connection, imported_validity_data: dict[uuid.UUID, ValidityInterval]):
            self._do_import(dump_with_validity_path)
            self._get_validity_data(connection, imported_validity_data)

        self._run_mesh_and_do(import_data_with_validity, connection, imported_validity_data)

        assert imported_validity_data == validity_test_data


    def test_change_existing_validity(self, connection: mesh.Connection, dumps_path: tempfile.TemporaryDirectory):
        dump_with_new_validity_path = f"{dumps_path.name}/new_validity.mdump"

        old_validity_data = {
            MESH_TO_AREAS_FINLAND_ID: ValidityInterval(FROM_DATE, UNTIL_DATE),
            MESH_TO_AREAS_NORGE_ID: ValidityInterval(FROM_DATE, None),
            MESH_MARKET_ENERGY_MARKET_FLOWS_NO1_ID: ValidityInterval(None, UNTIL_DATE),
            MESH_MARKET_ENERGY_MARKET_FLOWS_NO3_ID: ValidityInterval(FROM_DATE, UNTIL_DATE),
        }

        new_validity_data = {
            MESH_TO_AREAS_FINLAND_ID: ValidityInterval(FROM_DATE + timedelta(days=1), UNTIL_DATE + timedelta(days=1)),
            MESH_TO_AREAS_NORGE_ID: ValidityInterval(None, UNTIL_DATE),
            MESH_MARKET_ENERGY_MARKET_FLOWS_NO1_ID: ValidityInterval(FROM_DATE, None),
            MESH_MARKET_ENERGY_MARKET_FLOWS_NO3_ID: ValidityInterval(None, None),
        }

        # Create a dump file with the "new" validity data.
        self._generate_and_export_data_with_validity(connection, new_validity_data, dump_with_new_validity_path)

        # Set the "old" validity data first, then import the "new" validity data.
        imported_validity_data = dict.fromkeys(new_validity_data, None)

        def callback(connection: mesh.Connection, imported_validity_data: dict[uuid.UUID, ValidityInterval]):
            self._do_import(BASE_DUMP_NEW_MESH)
            self._set_validity_data(connection, old_validity_data)
            self._do_import(dump_with_new_validity_path)
            self._get_validity_data(connection, imported_validity_data)

        self._run_mesh_and_do(callback, connection, imported_validity_data)

        # Check that the resulting validity data is the "new" one.
        print("[MARTIN] Validity data after import:")

        for guid, interval in imported_validity_data.items():
            print(f"[MARTIN] {guid}: {interval}")

        assert imported_validity_data == new_validity_data


    def test_can_import_old_dump_without_validity(self, connection: mesh.Connection):
        def callback(connection: mesh.Connection):
            self._do_import(BASE_DUMP_OLD_MESH)

        self._run_mesh_and_do(callback, connection)


    def _generate_and_export_data_with_validity(self,
                                                connection: mesh.Connection,
                                                validity_data: dict[uuid.UUID, ValidityInterval],
                                                dump_with_validity_path: str):
        def callback(connection: mesh.Connection):
            self._do_import(BASE_DUMP_NEW_MESH)
            self._set_validity_data(connection, validity_data)
            self._do_export(dump_with_validity_path)

        self._run_mesh_and_do(callback, connection)


    def _run_mesh_and_do(self, callback: Callable, *args):
        mesh_exe = f"{MESH_BUILD_PATH}/Powel.Mesh.Server.exe"

        print("[MARTIN] Starting mesh...")

        # We need to use try/finally instead of 'with subprocess.Popen(...)' since we can't wait on
        # the mesh process (because it won't finish on its own). In addition, for some reason we
        # won't be able to catch any exceptions until we terminate the mesh process.
        mesh_proc = subprocess.Popen([mesh_exe])

        try:
            # Give mesh some time to finish starting up.
            time.sleep(10)

            # Check if mesh has terminated due to some error (e.g. missing mesh.json).
            # FIXME: The above waiting time may not've been enough for Mesh to reach a point where
            # it would normally fail, in which case we may end up waiting forever since the
            # ImportExport program doesn't finish on its own when Mesh isn't running. We should have
            # a more sure-fire way of catching such situations.
            if not mesh_proc.poll():
                callback(*args)
            else:
                raise RuntimeError(f"Mesh error: {mesh_proc.returncode}")
        finally:
            print("[MARTIN] Terminating mesh...")

            mesh_proc.terminate()


    def _set_validity_data(self, connection: mesh.Connection, validity_data: dict[uuid.UUID, ValidityInterval]):
        # Set validity for our target objects.
        with connection.create_session() as session:
            for object_id, validity_interval in validity_data.items():
                # First, verify that the object doesn't have any validity info set.
                response = self._get_validity(session, object_id)

                assert response.valid_from is None and response.valid_until is None

                # Now, set the validity.
                self._set_validity(session, object_id, validity_interval)

            session.commit()


    def _get_validity_data(self, connection: mesh.Connection, validity_data: dict[uuid.UUID, ValidityInterval]):
        with connection.create_session() as session:
            for object_id in validity_data:
                validity_data[object_id] = self._get_validity(session, object_id)

                print(f"[MARTIN] Validity of object '{object_id}': '{validity_data[object_id]}'")


    def _set_validity(self, session: mesh.Connection.Session, object_id: uuid.UUID, validity_interval: ValidityInterval):
        print(f"[MARTIN] Setting validity for object {object_id}...")

        valid_from, valid_until = validity_interval.to_proto_timestamps()

        request = model_pb2.UpdateValidityRequest(
            session_id=_common._to_proto_guid(session.session_id),
            object_id=_mesh_id._to_proto_object_mesh_id(object_id),
            valid_from=valid_from,
            valid_until=valid_until,
        )

        response = session.model_service.UpdateValidity(request)

        print(f"[MARTIN] Done! Response: '{response}'")


    def _get_validity(self, session: mesh.Connection.Session, object_id: uuid.UUID) -> ValidityInterval:
        print(f"[MARTIN] Getting validity for object {object_id}...")

        request = model_pb2.GetValidityRequest(
            session_id=_common._to_proto_guid(session.session_id),
            object_id=_mesh_id._to_proto_object_mesh_id(object_id),
        )

        response = session.model_service.GetValidity(request)

        print(f"[MARTIN] Done! Response: '{response}'")

        # We need these explicit checks here since otherwise the pb response will return default
        # values for the fields instead of None. In the case of timestamp_pb2, this is the Unix
        # epoch. See also https://protobuf.dev/reference/python/python-generated/#embedded_message
        valid_from = response.valid_from if response.HasField("valid_from") else None
        valid_until = response.valid_until if response.HasField("valid_until") else None

        validity_interval = ValidityInterval()
        validity_interval.from_proto_timestamps(valid_from, valid_until)

        return validity_interval


    def _do_import(self, dump_path: str):
        print("[MARTIN] Importing data...")

        self._call_import_export(["-i", dump_path, "-S"])


    def _do_export(self, dump_path: str):
        print("[MARTIN] Exporting data...")

        self._call_import_export(["-o", dump_path, "-m", "MeshTEK"])


    def _call_import_export(self, args: list[str]):
        imp_exp_exe = f"{MESH_BUILD_PATH}/Powel.Mesh.Model.ImportExport.exe"

        # Use serialization version 27, which introduces Validity support.
        subprocess.check_call([imp_exp_exe, '-v', '27'] + args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))
