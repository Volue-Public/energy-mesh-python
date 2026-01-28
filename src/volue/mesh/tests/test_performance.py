"""
Performance tests of reading and writing time series with Python SDK.
The tests are using and extending SimpleThermalTestModel.
"""

import random
import statistics
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

import grpc
import pandas as pd
import pyarrow as pa
from volue.mesh import Connection, Timeseries

# Ip address for the Mesh server
HOST = "localhost"
# Mesh server port for gRPC communication
PORT = 50051


def _read_timeseries_points(
    session: Connection.Session,
    path: str,
    start_interval: datetime,
    number_of_points: int,
):
    """Reads values from specific time series and interval."""
    start_time = start_interval
    end_time = start_time + timedelta(hours=number_of_points)

    duration_measurement_start = time.time()

    timeseries = session.read_timeseries_points(
        target=path, start_time=start_time, end_time=end_time
    )

    # useful for debugging purposes
    # print(timeseries.arrow_table.to_pandas())

    # in seconds
    return time.time() - duration_measurement_start


def _write_timeseries_points(
    session: Connection.Session,
    path: str,
    start_interval: datetime,
    number_of_points: int,
):
    """Writes random values to specific time series and interval."""
    timestamps = pd.date_range(start_interval, periods=number_of_points, freq="1h")
    flags = [Timeseries.PointFlags.OK.value] * number_of_points
    values = []
    for _ in range(number_of_points):
        values.append(random.uniform(0, 100))
    arrays = [pa.array(timestamps), pa.array(flags), pa.array(values)]
    arrow_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    duration_measurement_start = time.time()

    timeseries = Timeseries(table=arrow_table, full_name=path)
    session.write_timeseries_points(timeseries)

    # in seconds
    return time.time() - duration_measurement_start


class PerformanceTestRunner:
    # Prefix of new objects created for testing purposes
    NEW_OBJECT_NAME_PREFIX = "TestPowerPlant"
    # Prefix of new objects created for testing purposes
    NEW_OBJECT_OWNER_PATH = (
        "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
    )
    # Time series read/write operation start interval datetime
    START_INTERVAL = datetime(2022, 1, 1)
    # Physical time series attribute name
    PHYSICAL_TIMESERIES_ATTRIBUTE_NAME = "TsRawAtt"
    # Virtual time series attribute name
    VIRTUAL_TIMESERIES_ATTRIBUTE_NAME = "VtsAtt"
    # Calculation time series attribute name
    CALCULATION_TIMESERIES_ATTRIBUTE_NAME = "TsCalcAtt2"
    # Physical time series key
    PHYSICAL_TIMESERIES_KEY = 2
    # Virtual time series key
    VIRTUAL_TIMESERIES_KEY = 4

    def __init__(
        self,
        connection: Connection,
        test_case_number_of_timeseries: List[int],
        test_case_number_of_points: List[int],
        test_iterations: int,
    ):
        self._connection = connection
        self._test_case_number_of_timeseries = test_case_number_of_timeseries
        self._test_case_number_of_points = test_case_number_of_points
        self._test_iterations = test_iterations
        self._results = defaultdict(list)
        self._objects_to_create = max(self._test_case_number_of_timeseries)

    def _prepare_model(self):
        """
        Creates new objects needed for running test cases and
        initially writes some random data to physical time series.
        """
        with self._connection.create_session() as session:
            for object_index in range(self._objects_to_create):
                # create new object
                new_object_name = f"{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                new_object = session.create_object(
                    target=self.NEW_OBJECT_OWNER_PATH, name=new_object_name
                )

                # connect physical time series to the correct attribute of the new object
                physical_time_series_attribute_path = (
                    f"{new_object.path}.{self.PHYSICAL_TIMESERIES_ATTRIBUTE_NAME}"
                )
                session.update_timeseries_attribute(
                    physical_time_series_attribute_path,
                    new_timeseries_resource_key=self.PHYSICAL_TIMESERIES_KEY,
                )

                # connect virtual time series to the correct attribute of the new object
                virtual_time_series_attribute_path = (
                    f"{new_object.path}.{self.VIRTUAL_TIMESERIES_ATTRIBUTE_NAME}"
                )
                session.update_timeseries_attribute(
                    virtual_time_series_attribute_path,
                    new_timeseries_resource_key=self.VIRTUAL_TIMESERIES_KEY,
                )

                # update expressions in calculation time series to make sure at least
                # two time series are used for calculation
                calculation_time_series_attribute_path = (
                    f"{new_object.path}.{self.CALCULATION_TIMESERIES_ATTRIBUTE_NAME}"
                )
                expression = "##= @t('.TsCalcAtt') + @t('.TsRawAtt')\n"
                session.update_timeseries_attribute(
                    calculation_time_series_attribute_path,
                    new_local_expression=expression,
                )

                # write points to physical time series
                # write maximum number of points from test cases
                _write_timeseries_points(
                    session,
                    physical_time_series_attribute_path,
                    self.START_INTERVAL,
                    max(self._test_case_number_of_points),
                )

            # commit
            session.commit()
            print("Model prepared for testing")

    def _clean_model(self):
        """Removes all objects created during model preparation."""
        with self._connection.create_session() as session:
            for object_index in range(self._objects_to_create):
                object_path = f"{self.NEW_OBJECT_OWNER_PATH}/{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                session.delete_object(object_path, recursive_delete=True)

            session.commit()

    def _read_timeseries(
        self,
        attribute_name: str,
        time_series_count: int,
        number_of_points: int,
        test_case_name: str,
        timeseries_type: str,
    ):
        total_duration = 0

        with self._connection.create_session() as session:
            for object_index in range(time_series_count):
                object_path = f"{self.NEW_OBJECT_OWNER_PATH}/{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                time_series_attribute_path = f"{object_path}.{attribute_name}"

                total_duration += _read_timeseries_points(
                    session,
                    time_series_attribute_path,
                    self.START_INTERVAL,
                    number_of_points,
                )

        self._results[test_case_name].append(total_duration)
        print(
            f"\tRead {timeseries_type} time series: {time_series_count} time series count, {number_of_points} points, operation took {round(total_duration, 2)} seconds."
        )

    def _read_physical_timeseries(self, time_series_count: int, number_of_points: int):
        """Test: reading physical time series."""
        test_case_name = f"TS1_N{time_series_count}_M{number_of_points}"
        self._read_timeseries(
            self.PHYSICAL_TIMESERIES_ATTRIBUTE_NAME,
            time_series_count,
            number_of_points,
            test_case_name,
            timeseries_type="physical",
        )

    def _read_virtual_timeseries(self, time_series_count: int, number_of_points: int):
        """Test: reading virtual time series."""
        test_case_name = f"TS2_N{time_series_count}_M{number_of_points}"
        self._read_timeseries(
            self.PHYSICAL_TIMESERIES_ATTRIBUTE_NAME,
            time_series_count,
            number_of_points,
            test_case_name,
            timeseries_type="virtual",
        )

    def _read_calculation_timeseries(
        self, time_series_count: int, number_of_points: int
    ):
        """Test: reading calculation time series."""
        test_case_name = f"TS3_N{time_series_count}_M{number_of_points}"
        self._read_timeseries(
            self.PHYSICAL_TIMESERIES_ATTRIBUTE_NAME,
            time_series_count,
            number_of_points,
            test_case_name,
            timeseries_type="calculation",
        )

    def _write_physical_timeseries(
        self, time_series_count: int, number_of_points: int, commit: bool
    ):
        """Test: writing physical time series."""
        total_duration = 0

        with self._connection.create_session() as session:
            for object_index in range(time_series_count):
                object_path = f"{self.NEW_OBJECT_OWNER_PATH}/{self.NEW_OBJECT_NAME_PREFIX}{object_index}"
                time_series_attribute_path = (
                    f"{object_path}.{self.PHYSICAL_TIMESERIES_ATTRIBUTE_NAME}"
                )

                total_duration += _write_timeseries_points(
                    session,
                    time_series_attribute_path,
                    self.START_INTERVAL,
                    number_of_points,
                )

                if commit:
                    measurement_duration_start = time.time()
                    session.commit()
                    total_duration += time.time() - measurement_duration_start

        test_case_name = (
            f"TS5_N{time_series_count}_M{number_of_points}"
            if commit
            else f"TS4_N{time_series_count}_M{number_of_points}"
        )
        self._results[test_case_name].append(total_duration)
        print(
            f"\tWrite physical time series: {time_series_count} time series count, {number_of_points} points, commit={commit}, operation took {round(total_duration, 2)} seconds."
        )

    def _print_results(self):
        """Prints aggregated test results."""
        for test_case in self._results:
            average = statistics.mean(self._results[test_case])
            print(
                f"Test case: {test_case}, average duration: {average} seconds, values: {self._results[test_case]}"
            )

    def run_tests(self):
        """Prepares model, runs all test cases, prints results and cleans the model afterwards."""
        try:
            self._prepare_model()

            for i in range(self._test_iterations):
                print(f"Iteration: {i+1}")
                for time_series_count in self._test_case_number_of_timeseries:
                    for points in self._test_case_number_of_points:
                        if points > 1:
                            self._read_physical_timeseries(time_series_count, points)
                            self._read_virtual_timeseries(time_series_count, points)
                            self._read_calculation_timeseries(time_series_count, points)
                        self._write_physical_timeseries(
                            time_series_count, points, False
                        )
                        self._write_physical_timeseries(time_series_count, points, True)

            self._print_results()
        except grpc.RpcError as e:
            print(f"Failed to run performance tests: {e}")
        finally:
            self._clean_model()
            pass


if __name__ == "__main__":
    number_of_timeseries = [100, 1000]
    number_of_points = [1, 100, 500, 1000, 10000]
    iterations = 5

    connection = Connection(host=HOST, port=PORT)
    test_runner = PerformanceTestRunner(
        connection, number_of_timeseries, number_of_points, iterations
    )
    test_runner.run_tests()
