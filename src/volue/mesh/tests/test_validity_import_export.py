import os
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

# Use serialization version 27, which introduces Validity support.
# TODO: Remove this once the default is version 27 or greater.
SERIALIZATION_VERSION = 27

# BASE_DUMPS_PATH = "C:/Users/martin.galvan"
# BASE_DUMP_OLD_MESH = f"{BASE_DUMPS_PATH}/base_dump_old_mesh.mdump"
# BASE_DUMP_NEW_MESH = f"{BASE_DUMPS_PATH}/base_dump_new_mesh.mdump"
MESH_BUILD_PATH = "C:/Users/martin.galvan/Documents/energy-mesh/Mesh/build/Release"

# FIXME: The checks seem to break if we use datetime.fromisoformat("1990-08-21T00:00:00.000Z") since
# the return value from GetValidity doesn't seem to include the fractionary part.
FROM_DATE = datetime.fromisoformat("1990-08-21T00:00:00")
UNTIL_DATE = FROM_DATE + timedelta(days=1)

# We set various combinations of validity values for different objects at the same time on each test.
# This is more efficient than doing the entire export/import cycle on a single object for each
# combination of validity values.
# Note that the target objects must be of kind AttributeElement or Component.
# Models->SimpleThermalTestModel->ThermalComponent
THERMAL_COMPONENT_ID = uuid.UUID("{0000000b-0001-0000-0000-000000000000}")

# Models->SimpleThermalTestModel->ThermalComponent->ThermalPowerToPlantRef->SomePowerPlant1
POWER_PLANT_1_ID = uuid.UUID("{0000000a-0001-0000-0000-000000000000}")

# Models->SimpleThermalTestModel->ThermalComponent->ThermalPowerToPlantRef->SomePowerPlant1->PlantToChimneyRef->SomePowerPlantChimney1
CHIMNEY_1_ID = uuid.UUID("{0000000a-0004-0000-0000-000000000000}")

# Models->SimpleThermalTestModel->ThermalComponent->ThermalPowerToPlantRef->SomePowerPlant1->PlantToChimneyRef->SomePowerPlantChimney1
CHIMNEY_2_ID = uuid.UUID("{0000000a-0005-0000-0000-000000000000}")


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
    @pytest.fixture(scope="class")
    def dumps_dir(self, tmp_path_factory: pytest.TempPathFactory) -> str:
        return str(tmp_path_factory.mktemp(self.__class__.__name__))

    # This fixture creates an .mdump file containing the 'SimpleThermalTestModel' which can be later
    # imported and used as a base for further testing.
    # Note that we could replace this fixture by just calling _populate_with_simple_thermal_model
    # on each test instead of importing the .mdump; however, if we later do an import of e.g. a
    # modified SimpleThermalModel, we'll get an error of the following form:
    #
    # "The member container at PlantElementType already contains an attribute definition..."
    #
    # The error doesn't appear if we first populate Mesh through importing this .mdump instead of
    # using CommandLineRequests as in _populate_with_simple_thermal_model.
    @pytest.fixture(scope="class")
    def base_dump_new_mesh_path(self, dumps_dir: str) -> str:
        dump_path = os.path.join(dumps_dir, "base_dump_new_mesh.mdump")

        def callback():
            self._populate_with_simple_thermal_model()
            self._do_export(dump_path)

        self._run_mesh_and_do(callback)

        return dump_path


    def test_import_validity(self,
                             connection: mesh.Connection,
                             base_dump_new_mesh_path: str,
                             dumps_dir: str):
        dump_with_validity_path = os.path.join(dumps_dir, "with_validity.mdump")

        validity_test_data = {
            THERMAL_COMPONENT_ID: ValidityInterval(FROM_DATE, UNTIL_DATE),
            POWER_PLANT_1_ID: ValidityInterval(FROM_DATE, None),
            CHIMNEY_1_ID: ValidityInterval(None, UNTIL_DATE),
        }

        self._generate_and_export_data_with_validity(connection,
                                                     validity_test_data,
                                                     base_dump_new_mesh_path,
                                                     dump_with_validity_path)

        imported_validity_data = dict.fromkeys(validity_test_data, None)

        def import_data_with_validity(connection: mesh.Connection,
                                      imported_validity_data: dict[uuid.UUID, ValidityInterval]):
            self._do_import(dump_with_validity_path)
            self._get_validity_data(connection, imported_validity_data)

        self._run_mesh_and_do(import_data_with_validity, connection, imported_validity_data)

        assert imported_validity_data == validity_test_data


    def test_import_over_existing_validity(self,
                                           connection: mesh.Connection,
                                           base_dump_new_mesh_path: str,
                                           dumps_dir: str):
        dump_with_new_validity_path = os.path.join(dumps_dir, "new_validity.mdump")

        old_validity_data = {
            THERMAL_COMPONENT_ID: ValidityInterval(FROM_DATE, UNTIL_DATE),
            POWER_PLANT_1_ID: ValidityInterval(FROM_DATE, None),
            CHIMNEY_1_ID: ValidityInterval(None, UNTIL_DATE),
            CHIMNEY_2_ID: ValidityInterval(FROM_DATE, UNTIL_DATE),
        }

        new_validity_data = {
            THERMAL_COMPONENT_ID: ValidityInterval(FROM_DATE + timedelta(days=1),
                                                   UNTIL_DATE + timedelta(days=1)),
            POWER_PLANT_1_ID: ValidityInterval(None, UNTIL_DATE),
            CHIMNEY_1_ID: ValidityInterval(FROM_DATE, None),
            CHIMNEY_2_ID: ValidityInterval(None, None),
        }

        # Create a dump file with the "new" validity data.
        self._generate_and_export_data_with_validity(connection,
                                                     new_validity_data,
                                                     base_dump_new_mesh_path,
                                                     dump_with_new_validity_path)

        imported_validity_data = dict.fromkeys(new_validity_data, None)

        # Set the "old" validity data first, then import the "new" validity data.
        def callback(connection: mesh.Connection,
                     base_dump_new_mesh_path: str,
                     imported_validity_data: dict[uuid.UUID, ValidityInterval]):
            self._do_import(base_dump_new_mesh_path)
            self._set_validity_data(connection, old_validity_data)

            # We need a 1-second delay between two imports because each one creates an entry in the
            # ObjectModelUpdates catalog with a name including a timestamp with a resolution in
            # seconds. If two updates happen too close to each other, the names of the entries will
            # collide and we'll get an error.
            time.sleep(1)

            self._do_import(dump_with_new_validity_path)
            self._get_validity_data(connection, imported_validity_data)

        self._run_mesh_and_do(callback, connection, base_dump_new_mesh_path, imported_validity_data)

        # Check that the resulting validity data is the "new" one.
        print("[MARTIN] Validity data after import:")

        for guid, interval in imported_validity_data.items():
            print(f"[MARTIN] {guid}: {interval}")

        assert imported_validity_data == new_validity_data


    # def test_can_import_old_dump_without_validity(self, connection: mesh.Connection):
    #     def callback(connection: mesh.Connection):
    #         self._do_import(BASE_DUMP_OLD_MESH)

    #     self._run_mesh_and_do(callback, connection)


    def _populate_with_simple_thermal_model(self):
        cli_requests_exe = os.path.join(MESH_BUILD_PATH, "Powel.Mesh.CommandLineRequests.exe")

        # FIXME: Set timeout for communicating with Mesh server to 5 minutes, in case Mesh crashes at some
        # point and we're unable to detect it for whatever reason.
        subprocess.check_call([cli_requests_exe, "-w", "PopulateTestModels", "-m", "SimpleThermalModel"])


    def _generate_and_export_data_with_validity(self,
                                                connection: mesh.Connection,
                                                validity_data: dict[uuid.UUID, ValidityInterval],
                                                base_dump_new_mesh_path: str,
                                                dump_with_validity_path: str):
        def callback(connection: mesh.Connection):
            self._do_import(base_dump_new_mesh_path)
            self._set_validity_data(connection, validity_data)
            self._do_export(dump_with_validity_path)

        self._run_mesh_and_do(callback, connection)


    def _run_mesh_and_do(self, callback: Callable, *args):
        mesh_exe = os.path.join(MESH_BUILD_PATH, "Powel.Mesh.Server.exe")

        print("[MARTIN] Starting mesh...")

        # We need to use try/finally instead of 'with subprocess.Popen(...)' since we can't wait on
        # the mesh process (because it won't finish on its own). In addition, for some reason we
        # won't be able to catch any exceptions until we terminate the mesh process.
        mesh_proc = subprocess.Popen([mesh_exe, '--serialization-version', f'{SERIALIZATION_VERSION}'])

        try:
            # Give mesh some time to finish starting up.
            time.sleep(10)

            # Check if mesh has terminated due to some error at this point (e.g. missing mesh.json).
            # This is faster than waiting for a timeout error on Model.ImportExport.
            if not mesh_proc.poll():
                callback(*args)
            else:
                raise RuntimeError(f"Mesh error: {mesh_proc.returncode}")
        finally:
            print("[MARTIN] Terminating mesh...")

            mesh_proc.terminate()


    def _set_validity_data(self,
                           connection: mesh.Connection,
                           validity_data: dict[uuid.UUID, ValidityInterval]):
        # Set validity for our target objects.
        with connection.create_session() as session:
            for object_id, validity_interval in validity_data.items():
                # First, verify that the object doesn't have any validity info set.
                response = self._get_validity(session, object_id)

                assert response.valid_from is None and response.valid_until is None

                # Now, set the validity.
                self._set_validity(session, object_id, validity_interval)

            session.commit()


    def _get_validity_data(self,
                           connection: mesh.Connection,
                           validity_data: dict[uuid.UUID, ValidityInterval]):
        with connection.create_session() as session:
            for object_id in validity_data:
                validity_data[object_id] = self._get_validity(session, object_id)

                print(f"[MARTIN] Validity of object '{object_id}': '{validity_data[object_id]}'")


    def _set_validity(self,
                      session: mesh.Connection.Session,
                      object_id: uuid.UUID,
                      validity_interval: ValidityInterval):
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

        self._call_import_export(["-o", dump_path])


    def _call_import_export(self, args: list[str]):
        imp_exp_exe = os.path.join(MESH_BUILD_PATH, "Powel.Mesh.Model.ImportExport.exe")

        # Make sure we only import and export the model called 'SimpleThermalTestModel', since
        # otherwise the exports will include stuff from 'Utility' which will error out when trying
        # to import it later on.
        # Set timeout for communicating with Mesh server to 5 minutes, in case Mesh crashes at some
        # point and we're unable to detect it for whatever reason.
        subprocess.check_call([imp_exp_exe, "-m", "SimpleThermalTestModel", "-v", f"{SERIALIZATION_VERSION}", "-f", "5"] + args)


if __name__ == "__main__":
    sys.exit(pytest.main(sys.argv))

