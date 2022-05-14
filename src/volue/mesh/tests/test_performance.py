"""
Performance tests of reading and writing time series with Python SDK.
The tests are using and extending SimpleThermalTestModel.
"""

from collections import defaultdict
from datetime import datetime, timedelta
import random
import statistics
import time
import uuid

import grpc
import pandas as pd
import pyarrow as pa

from volue.mesh import Connection, MeshObjectId, Timeseries
from volue.mesh._common import _to_proto_guid
from volue.mesh.proto.core.v1alpha import core_pb2

# Ip address for the Mesh server
HOST = "localhost"
# Mesh server port for gRPC communication
PORT = 50051


def _read_timeseries_points(session: Connection.Session, path: str, start_interval: datetime, number_of_points: int):
    start_time = start_interval
    end_time = start_time + timedelta(hours=number_of_points)

    duration_measurement_start = time.time()

    test = session.read_timeseries_points(
        start_time=start_time,
        end_time=end_time,
        mesh_object_id=MeshObjectId.with_full_name(path)
    )

    print(test.arrow_table.to_pandas())

    # in seconds
    return time.time() - duration_measurement_start


def _write_timeseries_points(session: Connection.Session, path: str, start_interval: datetime, number_of_points: int):
    timestamps = pd.date_range(start_interval, periods=number_of_points, freq="1H")
    flags = [Timeseries.PointFlags.OK.value] * number_of_points
    values = []
    for _ in range(number_of_points):
        values.append(random.uniform(0, 100))
    arrays = [
        pa.array(timestamps),
        pa.array(flags),
        pa.array(values)]
    arrow_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    duration_measurement_start = time.time()

    timeseries = Timeseries(table=arrow_table, full_name=path)
    session.write_timeseries_points(timeseries)

    # in seconds
    return time.time() - duration_measurement_start


class PerformanceTestRunner():

    # Prefix of new objects created for testing purposes
    NEW_OBJECT_NAME_PREFIX = "TestPowerPlant"
    # Prefix of new objects created for testing purposes
    NEW_OBJECT_OWNER_PATH = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    # Time series read/write operation start interval datetime
    START_INTERVAL = datetime(2022, 1, 1)
    # Physical time series attribute name
    PHYSICAL_TIMESERIES_ATTRIBUTE_NAME = "TsRawAtt"
    # Virtual time series attribute name
    VIRTUAL_TIMESERIES_ATTRIBUTE_NAME = "VtsAtt"
    # Calculation time series attribute name
    CALCULATION_TIMESERIES_ATTRIBUTE_NAME = "TsCalcAtt2"
    # Physical time series ID (entry in resources)
    PHYSICAL_TIMESERIES_ID = uuid.UUID("00000004-0001-0000-0000-000000000000")
    # Virtual time series ID (entry in resources)
    VIRTUAL_TIMESERIES_ID = uuid.UUID("00000004-000D-0000-0000-000000000000")


    def __init__(self, connection: Connection, max_objects_count: int):
        self.connection = connection
        self.max_objects_count = max_objects_count
        self.results = defaultdict(list)

    def prepare_model(self, number_of_points: int):
        with self.connection.create_session() as session:
            for object_index in range(self.max_objects_count):
                # create new object
                new_object_name = f"{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                new_object = session.create_object(new_object_name, owner_attribute_path=self.NEW_OBJECT_OWNER_PATH)

                # connect physical time series to the correct attribute of the new object
                physical_time_series_attribute_path = f"{new_object.path}.{self.PHYSICAL_TIMESERIES_ATTRIBUTE_NAME}"
                entry_id = core_pb2.TimeseriesEntryId()
                entry_id.guid.CopyFrom(_to_proto_guid(self.PHYSICAL_TIMESERIES_ID))
                session.update_timeseries_attribute(
                    path=physical_time_series_attribute_path, new_timeseries_entry_id=entry_id)

                # connect virtual time series to the correct attribute of the new object
                virtual_time_series_attribute_path = f"{new_object.path}.{self.VIRTUAL_TIMESERIES_ATTRIBUTE_NAME}"
                entry_id = core_pb2.TimeseriesEntryId()
                entry_id.guid.CopyFrom(_to_proto_guid(self.VIRTUAL_TIMESERIES_ID))
                session.update_timeseries_attribute(
                    path=virtual_time_series_attribute_path, new_timeseries_entry_id=entry_id)

                # update expressions in calculation time series to make sure at least
                # two time series are used for calculation
                calculation_time_series_attribute_path = f"{new_object.path}.{self.CALCULATION_TIMESERIES_ATTRIBUTE_NAME}"
                expression = "##= @t('.TsCalcAtt') + @t('.TsRawAtt')\n"
                session.update_timeseries_attribute(
                    path=calculation_time_series_attribute_path, new_local_expression=expression)

                # write points to physical time series
                _write_timeseries_points(
                    session, physical_time_series_attribute_path, self.START_INTERVAL, number_of_points)

            # commit
            session.commit()
            print('Model prepared for testing')


    def clean_model(self):
        with self.connection.create_session() as session:
            for object_index in range(self.max_objects_count):
                object_path = f"{self.NEW_OBJECT_OWNER_PATH}/{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                session.delete_object(object_path=object_path, recursive_delete=True)

            session.commit()


    def read_physical_timeseries(self, time_series_count: int, number_of_points: int):
        total_duration = 0

        with self.connection.create_session() as session:
            for object_index in range(time_series_count):
                object_path = f"{self.NEW_OBJECT_OWNER_PATH}/{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                time_series_attribute_path = f"{object_path}.{self.PHYSICAL_TIMESERIES_ATTRIBUTE_NAME}"

                total_duration += _read_timeseries_points(
                    session, time_series_attribute_path, self.START_INTERVAL, number_of_points)

        test_case_name = f"TS1_N{time_series_count}_M{number_of_points}"
        self.results[test_case_name].append(total_duration)
        print(f'\tRead physical time series: {time_series_count} time series count, {number_of_points} points, operation took {round(total_duration, 2)} seconds.')


    def read_virtual_timeseries(self, time_series_count: int, number_of_points: int):
        total_duration = 0

        with self.connection.create_session() as session:
            for object_index in range(time_series_count):
                object_path = f"{self.NEW_OBJECT_OWNER_PATH}/{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                time_series_attribute_path = f"{object_path}.{self.VIRTUAL_TIMESERIES_ATTRIBUTE_NAME}"

                total_duration += _read_timeseries_points(
                    session, time_series_attribute_path, self.START_INTERVAL, number_of_points)

        test_case_name = f"TS2_N{time_series_count}_M{number_of_points}"
        self.results[test_case_name].append(total_duration)
        print(f'\tRead virtual time series: {time_series_count} time series count, {number_of_points} points, operation took {round(total_duration, 2)} seconds.')


    def read_calculation_timeseries(self, time_series_count: int, number_of_points: int):
        total_duration = 0

        with self.connection.create_session() as session:
            for object_index in range(time_series_count):
                object_path = f"{self.NEW_OBJECT_OWNER_PATH}/{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                time_series_attribute_path = f"{object_path}.{self.CALCULATION_TIMESERIES_ATTRIBUTE_NAME}"

                total_duration += _read_timeseries_points(
                    session, time_series_attribute_path, self.START_INTERVAL, number_of_points)

        test_case_name = f"TS3_N{time_series_count}_M{number_of_points}"
        self.results[test_case_name].append(total_duration)
        print(f'\tRead calculation time series: {time_series_count} time series count, {number_of_points} points, operation took {round(total_duration, 2)} seconds.')


    def write_physical_timeseries(self, time_series_count: int, number_of_points: int, commit: bool):
        total_duration = 0

        with self.connection.create_session() as session:
            for object_index in range(time_series_count):
                object_path = f"{self.NEW_OBJECT_OWNER_PATH}/{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                time_series_attribute_path = f"{object_path}.{self.PHYSICAL_TIMESERIES_ATTRIBUTE_NAME}"

                total_duration += _write_timeseries_points(
                    session, time_series_attribute_path, self.START_INTERVAL, number_of_points)

                if commit:
                    measurement_duration_start = time.time()
                    session.commit()
                    total_duration += time.time() - measurement_duration_start

        test_case_name = f"TS5_N{time_series_count}_M{number_of_points}" if commit else f"TS4_N{time_series_count}_M{number_of_points}"
        self.results[test_case_name].append(total_duration)
        print(f'\tWrite physical time series: {time_series_count} time series count, {number_of_points} points, commit={commit}, operation took {round(total_duration, 2)} seconds.')


if __name__ == '__main__':

    number_of_timeseries = [100, 1000]
    number_of_points = [1, 100, 500, 1000, 10000]
    iterations = 5

    connection = Connection(host=HOST, port=PORT)
    try:
        test_runner = PerformanceTestRunner(connection, max(number_of_timeseries))
        test_runner.prepare_model(max(number_of_points))

        for i in range(iterations):
            print(f"Iteration: {i+1}")
            for time_series_count in number_of_timeseries:
                for points in number_of_points:
                    if points > 1:
                        test_runner.read_physical_timeseries(time_series_count, points)
                        test_runner.read_virtual_timeseries(time_series_count, points)
                        test_runner.read_calculation_timeseries(time_series_count, points)
                    test_runner.write_physical_timeseries(time_series_count, points, False)
                    test_runner.write_physical_timeseries(time_series_count, points, True)

        for test_case in test_runner.results:
            average = statistics.mean(test_runner.results[test_case])
            print(f'Test case: {test_case}, average duration: {average} seconds, values: {test_runner.results[test_case]}')

    except grpc.RpcError as e:
        print(f"Failed to run performance tests: {e}")
    finally:
        test_runner.clean_model()
