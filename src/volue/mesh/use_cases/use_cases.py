from datetime import datetime, timedelta
import sys
from typing import List, Any, Tuple
import uuid

from dateutil import tz
import grpc
import matplotlib.pyplot as plt
import pandas as pd
import pyarrow as pa

from volue.mesh import (Connection, AttributesFilter, Object,
    RatingCurveSegment, RatingCurveVersion, Timeseries, TimeseriesResource,
    XySet, XyCurve)
from volue.mesh.calc import transform as Transform
from volue.mesh.calc.common import Timezone

"""
These use cases were designed to work with a real customer database (TEKICC_ST@MULLIGAN)
"""

# Ip address for the Mesh server
HOST = "localhost"
# Mesh server port for gRPC communication
PORT = 50051
# Use matplotlib to visualize results
SHOW_PLOT = True
# Save time series to CSV file
SAVE_TO_CSV = False
# Some use cases write new points or update existing objects
# Set this flag to True to commit the changes (made in use cases) to Mesh
COMMIT_CHANGES = False
# Which use case to run
# ['all', 'flow_drop_2', 'flow_drop_3', 'flow_drop_4', '1' ... '<number_of_use_cases>']
RUN_USE_CASE = 'all'
# Set local time zone to be used in every use case (reads time zone from operating system settings)
LOCAL_TIME_ZONE = tz.tzlocal()
# if you want to set explicitly the time zone you can use the following:
#LOCAL_TIME_ZONE = tz.gettz('Europe/Warsaw')
# if you want to set fixed UTC offset (no DST) you can use the following:
#LOCAL_TIME_ZONE = timezone(timedelta(hours=1))


def plot_timeseries(identifier_and_pandas_dataframes: List[Tuple[Any, pd.DataFrame]],
                    title: str,
                    style: str = 'plot') -> None:
    """Plots a list of pandas dataframes in a figure."""
    if SHOW_PLOT:
        legends = []
        for a_pair in identifier_and_pandas_dataframes:
            timeseries_identifier = a_pair[0]
            timeseries_pandas_dataframe = a_pair[1]
            legends.append(timeseries_identifier)

            data = [timeseries_pandas_dataframe['utc_time'], timeseries_pandas_dataframe['value']]
            arguments = {'linestyle': '--',
                         'marker': 'o',
                         'where': 'post'  # making sure line continues to the right of the value until new value
                         }
            if style == 'plot':
                plt.plot(*data)
            elif style == 'step':
                plt.step(*data, **arguments)

        plt.ylabel('value')
        plt.xlabel('local time')
        plt.legend(legends, ncol=2, fontsize=6)
        plt.title(title)
        figure_manager = plt.get_current_fig_manager()
        figure_manager.window.state('zoomed')  # Fullscreen
        plt.show()


def save_timeseries_to_csv(identifier_and_pandas_dataframes: List[Tuple[Any, pd.DataFrame]],
                           file_prefix: str) -> None:
    """
    Saves a pandas dataframe to a CSV file.
    In case of local time the column name will still be called 'utc_time', but the timestamp will be timezone aware.
    """
    if SAVE_TO_CSV:
        for a_pair in identifier_and_pandas_dataframes:
            timeseries_identifier = str(a_pair[0]).replace('/', '.')
            timeseries_pandas_dataframe = a_pair[1]
            timeseries_pandas_dataframe.to_csv(file_prefix + '_' + timeseries_identifier + '.csv', index=False)


def get_timeseries_resource_information(timeseries_resource: TimeseriesResource):
    """Create a printable message from a time series resource."""
    message = (
        f"Time series with timskey: '{timeseries_resource.timeseries_key}' \n"
        f"has name: '{timeseries_resource.name}', \n"
        f"path set in the resource container is: '{timeseries_resource.path}', \n"
        f"curve type: '{timeseries_resource.curve_type}', \n"
        f"resolution: '{timeseries_resource.resolution}', \n"
        f"unit of measurement: '{timeseries_resource.unit_of_measurement}'\n"
    )

    expression = timeseries_resource.virtual_timeseries_expression
    if expression is not None and expression != "":
        message = (
            f"{message}"
            f"virtual time series expression: '{expression}'\n"
        )

    return message

def get_timeseries_information(timeseries: Timeseries):
    """Create a printable message from a time series."""
    message = (
        f"Time series full name: '{timeseries.full_name}', "
        f"uuid: '{timeseries.uuid}', "
        f"timskey: '{timeseries.timskey}', "
        f"start time: '{str(timeseries.start_time)}', "
        f"end time: '{str(timeseries.end_time)}', "
        f"resolution: '{timeseries.resolution}', "
        f"it has '{timeseries.number_of_points}' points "
        f"and this is some of them: \n"
        f"{timeseries.arrow_table.to_pandas()}"
    )
    return message

def get_object_information(object: Object):
    """Create a printable message from an Object."""
    message = (
        f"Object with path: '{object.path}' \n"
        f"has ID: '{object.id}', \n"
        f"name: '{object.name}', \n"
        f"type name: '{object.type_name}', \n"
        f"owner path: '{object.owner_path}', \n"
        f"owner ID: '{object.owner_id}'\n"
    )
    return message


def use_case_1():
    """
    Scenario:
    We want to find all time series which show the production of a hydro plant.

    Start point:        Model/MeshTEK/Mesh which has guid 801896b0-d448-4299-874a-3ecf8ab0e2d4
    Search expression:  *[.Type=HydroPlant].Production_operative
    Time interval:      1.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 1"
            start_object_guid = uuid.UUID("801896b0-d448-4299-874a-3ecf8ab0e2d4")  # Model/MeshTEK/Mesh
            search_query = "*[.Type=HydroPlant].Production_operative"
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 1, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timeseries_attributes = session.search_for_timeseries_attributes(
                start_object_guid, search_query)
            print(f"Search resulted in {len(timeseries_attributes)} object(s) that match(es) the search criteria: {search_query}")

            # Retrieve time series points connected to the found time series attributes
            path_and_pandas_dataframe = []
            for number, timeseries_attribute in enumerate(timeseries_attributes):
                timeseries = session.read_timeseries_points(target=timeseries_attribute.id,
                                                            start_time=start,
                                                            end_time=end)
                print(f"{number + 1}. \n"
                      f"-----\n"
                      f"{timeseries_attribute}")
                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                path_and_pandas_dataframe.append((timeseries_attribute.path, pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe, f"{use_case_name}: {search_query}")
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_1')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_2():
    """
    Scenario:
    We want to find time series which contain reservoir volume for all reservoirs in Norway (Norge).

    Start point:        Model/MeshTEK/Mesh which has guid 801896b0-d448-4299-874a-3ecf8ab0e2d4
    Search expression:  *[.Type=Area&&.Name=Norge]/To_HydroProduction/To_WaterCourses/To_Reservoirs.ReservoirVolume_operative
    Time interval:      1.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 2"
            start_object_guid = uuid.UUID("801896b0-d448-4299-874a-3ecf8ab0e2d4")  # Model/MeshTEK/Mesh
            search_query = "*[.Type=Area&&.Name=Norge]/To_HydroProduction/To_WaterCourses/To_Reservoirs.ReservoirVolume_operative"
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 1, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timeseries_attributes = session.search_for_timeseries_attributes(
                start_object_guid, search_query)
            print(f"Search resulted in {len(timeseries_attributes)} object(s) that match(es) the search criteria: {search_query}")

            # Retrieve time series points connected to the found time series attributes
            path_and_pandas_dataframe = []
            for number, timeseries_attribute in enumerate(timeseries_attributes):
                timeseries = session.read_timeseries_points(target=timeseries_attribute.id,
                                                            start_time=start,
                                                            end_time=end)
                print(f"{number + 1}. \n"
                      f"-----\n"
                      f"{timeseries_attribute}")
                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                path_and_pandas_dataframe.append((timeseries_attribute.path, pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe, f"{use_case_name}: {search_query}")
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_2')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_3():
    """
    Scenario:
    We want to find time series which has a known timskey.

    Timskeys:           [530, 536, 537, 543, 556]
    Time interval:      1.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 3"
            timskeys = [530, 536, 537, 543, 556]
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 1, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timskey_and_pandas_dataframe = []
            for timskey in timskeys:

                # Get information about the time series
                timeseries_resource = session.get_timeseries_resource_info(timeseries_key=timskey)
                print(f"[{timskey}]: \n"
                      f"-----\n"
                      f"{get_timeseries_resource_information(timeseries_resource)}")

                # Retrieve the time series points in a given interval
                timeseries = session.read_timeseries_points(target=timskey,
                                                            start_time=start,
                                                            end_time=end)
                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                timskey_and_pandas_dataframe.append((timskey, pandas_dataframe))

            # Post process data
            plot_timeseries(timskey_and_pandas_dataframe, f"{use_case_name}: Timskeys: {timskeys}")
            save_timeseries_to_csv(timskey_and_pandas_dataframe, 'use_case_3')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_4():
    """
    Scenario:
    We want to find time series, and its related information, which is connected to an object with a known guid.

    Guids:              [
                        "ff1db73f-8c8a-42f8-a44a-4bbb420874c1"
                        ]
    Time interval:      10.01.2022 - 27.03.2022

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 4"
            guids = [
                "ff1db73f-8c8a-42f8-a44a-4bbb420874c1"
            ]
            start = datetime(2022, 1, 10, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2022, 3, 27, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timskey_and_pandas_dataframe = []
            for guid in guids:

                # Retrieve the time series points in a given interval
                timeseries = session.read_timeseries_points(target=uuid.UUID(guid),
                                                            start_time=start,
                                                            end_time=end)

                # Retrieve information about the time series attribute
                timeseries_attribute = session.get_timeseries_attribute(uuid.UUID(guid), full_attribute_info=True)
                print(f"[{guid}]: \n"
                      f"-----\n"
                      f"{timeseries_attribute}")

                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                timskey_and_pandas_dataframe.append((guid, pandas_dataframe))

            # Post process data
            plot_timeseries(timskey_and_pandas_dataframe,
                            f"{use_case_name}: {len(guids)} known guid(s)",
                            style='step')
            save_timeseries_to_csv(timskey_and_pandas_dataframe, 'use_case_4')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_4b():
    """
    Scenario:
    We want to find time series, and its related information, which is connected to an object with a known path.
    This use cases shows usage of two path types (including full name) that point to the same time series attribute.

    Time interval:      10.01.2022 - 27.03.2022

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 4b"
            # Both paths are pointing to the same time series attribute:
            # - first path includes just object names
            # - second path includes also relationship attributes (e.g.: has_cAreas pointing to Norge object)
            # Path including also relationship attributes is called full name.
            # It uniquely identifies an object or attribute we are looking for,
            # because depending on the model it may happen that a parent object has more than one
            # relationship attribute pointing to objects with the same names, e.g.:
            # - ParentObject.has_cAreas/Norge
            # - ParentObject.has_cProductionAreas/Norge
            paths = [
                "Model/MeshTEK/Cases/Driva_Short_Opt/Norge/Vannkraft/Driva/Driva/Gjevilvatnet/1975.Production",  # path using only objects
                "Model/MeshTEK/Cases.has_OptimisationCases/Driva_Short_Opt.has_cAreas/Norge.has_cHydroProduction/Vannkraft.has_cWaterCourses/Driva.has_cProdriskAreas/Driva.has_cProdriskModules/Gjevilvatnet.has_cProdriskScenarios/1975.Production"  # path using full name (objects and attributes)
            ]
            start = datetime(2022, 1, 10, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2022, 3, 27, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timskey_and_pandas_dataframe = []
            for path in paths:

                # Retrieve the time series points in a given interval
                timeseries = session.read_timeseries_points(target=path,
                                                            start_time=start,
                                                            end_time=end)

                # Retrieve information connected to the timeseries
                timeseries_attribute = session.get_timeseries_attribute(path)

                print(f"[{path}]: \n"
                      f"-----\n"
                      f"{timeseries_attribute}")

                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                timskey_and_pandas_dataframe.append((path, pandas_dataframe))

            # Post process data
            plot_timeseries(timskey_and_pandas_dataframe,
                            f"{use_case_name}: {len(paths)} known path(s)",
                            style='step')
            save_timeseries_to_csv(timskey_and_pandas_dataframe, 'use_case_4b')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_5():
    """
    Scenario:
    We want to write some values to an existing time series with a known guid.

    Guid:              ['3fd4ed37-2114-4d95-af90-02b96bd993ed']  # Model/MeshTEK/Mesh.To_Areas/Norge.To_HydroProduction/Vannkraft.To_WaterCourses/Mørre.To_HydroPlants/Mørre.To_Units/Morre G1.Production_raw
    Time interval:      28.09.2021 - 29.09.2021
    Values:             [11.50, 11.91, 11.88, 11.86, 11.66, 11.73, 11.80, 11.88, 11.97, 9.87, 9.47, 9.05,
                        9.20, 9.00, 8.91, 10.62, 12.00, 12.07, 12.00, 11.78, 5.08, 0.00, 0.00, 0.00]

    """
    connection = Connection(host=HOST, port=PORT)

    with connection.create_session() as session:
        try:
            use_case_name = "Use case 5"
            guid = uuid.UUID('3fd4ed37-2114-4d95-af90-02b96bd993ed')

            start = datetime(2021, 9, 28, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 29, tzinfo=LOCAL_TIME_ZONE)

            resolution = timedelta(hours=1.0)
            timskey_and_pandas_dataframe = []
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Get time series data before write
            timeseries_before = session.read_timeseries_points(target=guid,
                                                               start_time=start,
                                                               end_time=end)
            print(f"Before writing points: \n"
                  f"-----\n"
                  f"{get_timeseries_information(timeseries=timeseries_before)}")

            pandas_dataframe = timeseries_before.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            timskey_and_pandas_dataframe.append(("before", pandas_dataframe))

            # Defining the data we want to write
            # Mesh data is organized as an Arrow table with the following schema:
            # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
            # flags - [pa.uint32]
            # value - [pa.float64]
            timestamps = []
            for i in range(0, 24):
                # there is problem with using in PyArrow time zone from dateutil
                # with time zone defined as fixed UTC offset (using `timezone(timedelta(hours=...))`) it is working correctly
                # for dateutil time zones use `astimezone` to UTC
                timestamps.append((start + resolution * i).astimezone(tz.UTC))

            utc_time = pa.array(timestamps)
            flags = pa.array([0] * 24)  # flag 0 -> Common::TimeseriesPointFlags::Ok
            new_values = pa.array([11.50, 11.91, 11.88, 11.86, 11.66, 11.73, 11.80, 11.88, 11.97, 9.87, 9.47, 9.05,
                                   9.20, 9.00, 8.91, 10.62, 12.00, 12.07, 12.00, 11.78, 5.08, 0.00, 0.00, 0.00])

            # Write new values
            new_arrays = [
                utc_time,
                flags,
                new_values
            ]
            table = pa.Table.from_arrays(arrays=new_arrays, schema=Timeseries.schema)
            timeseries = Timeseries(table=table, uuid_id=guid)

            # Send request to write time series based on timskey
            session.write_timeseries_points(timeseries=timeseries)

            # Get time series data before write
            timeseries_after = session.read_timeseries_points(target=guid,
                                                              start_time=start,
                                                              end_time=end)
            print(f"After writing points: \n"
                  f"-----\n"
                  f"{get_timeseries_information(timeseries=timeseries_after)}")

            pandas_dataframe = timeseries_after.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            timskey_and_pandas_dataframe.append(("after", pandas_dataframe))

            # Commit changes
            if COMMIT_CHANGES:
                session.commit()

            plot_timeseries(timskey_and_pandas_dataframe,
                            f"{use_case_name}: Before and after writing")
            save_timeseries_to_csv(timskey_and_pandas_dataframe, 'use_case_5')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_6():
    """
    Scenario:
    We want to transform existing time series from breakpoint resolution to hourly.

    Time series attribute ID:   '012d70e3-8f40-40af-9c0a-5d84fc239776'
    Transformation expression:  ## = @TRANSFORM(Object guid,'HOUR','AVGI')
    Time interval:              5.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 6"
            timeseries_attribute_id = '012d70e3-8f40-40af-9c0a-5d84fc239776'
            start = datetime(2021, 9, 5, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 1, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the time series attribute
            timeseries_attribute = session.get_timeseries_attribute(
                uuid.UUID(timeseries_attribute_id))

            # Retrieve time series points connected to the time series attribute
            path_and_pandas_dataframe = []
            timeseries_original = session.read_timeseries_points(target=timeseries_attribute.id,
                                                                 start_time=start,
                                                                 end_time=end)
            print(timeseries_attribute)

            pandas_dataframe = timeseries_original.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append((f"original", pandas_dataframe))

            # Transform time series from breakpoint to hourly
            timeseries_transformed = session.transform_functions(
                timeseries_attribute.id, start_time=start, end_time=end).transform(
                    Timeseries.Resolution.HOUR, Transform.Method.AVGI, Timezone.LOCAL)

            pandas_dataframe = timeseries_transformed.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(("transformed", pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: transforming resolution",
                            style='step')
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_6')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_7():
    """
    Scenario:
    We want to transform existing time series from hourly resolution to daily.

    Time series attribute ID:   '7608c9e2-c4fc-4570-b5b2-069f29a34f22' which is:
                                Model/MeshTEK/Mesh/Norge/Vannkraft/Mørre/Mørre.Production_operative (TimeseriesCalculation)
    Transformation expression:  ## = @TRANSFORM(Object guid,'DAY','AVG')
    Time interval:              5.09.2021 - 15.09.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 7"
            timeseries_attribute_id = '7608c9e2-c4fc-4570-b5b2-069f29a34f22'
            start = datetime(2021, 9, 5, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 15, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the time series attribute
            timeseries_attribute = session.get_timeseries_attribute(
                uuid.UUID(timeseries_attribute_id))

            # Retrieve time series connected to the time series attribute
            path_and_pandas_dataframe = []
            timeseries_original = session.read_timeseries_points(target=timeseries_attribute.id,
                                                                 start_time=start,
                                                                 end_time=end)
            print(timeseries_attribute)

            pandas_dataframe = timeseries_original.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append((f"original", pandas_dataframe))

            # Transform time series from hourly to daily
            timeseries_transformed = session.transform_functions(
                timeseries_attribute.id, start_time=start, end_time=end).transform(
                    Timeseries.Resolution.DAY, Transform.Method.AVG, Timezone.LOCAL)

            pandas_dataframe = timeseries_transformed.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(("transformed", pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: transforming resolution",
                            style='step')
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_7')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_8():
    """
    Scenario:
    We want to summarize an array of time series

    Start point:                36395abf-9a39-40ef-b29c-b1d59db855e3
    Search expression:          *[.Type=Reservoir].ReservoirVolume_operative
    Calculation expression:     ## = @SUM(@T('*[.Type=Reservoir].ReservoirVolume_operative'))
    Time interval:              5.9.2021 - 15.9.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 8"
            start_object_guid = '36395abf-9a39-40ef-b29c-b1d59db855e3'
            search_query = "*[.Type=Reservoir].ReservoirVolume_operative"
            start = datetime(2021, 9, 5, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 15, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Summarize timeseries
            summarized_timeseries = session.statistical_functions(
                uuid.UUID(start_object_guid), start_time=start, end_time=end).sum(
                    search_query=search_query)

            path_and_pandas_dataframe = []
            pandas_dataframe = summarized_timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(("Sum", pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: summarize @SUM(@T('*[.Type=Reservoir].ReservoirVolume_operative'))")
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_8')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_9():
    """
    Scenario:
    We want to get the historical data for a time series on a specific date.

    Time series attribute ID:   333a4648-bd2a-4331-acd8-ab88e4a1a5f5 which is:
                                Model/MeshTEK/Cases/Morre_Short_Opt/Norge/Vannkraft/Mørre/Mørre/Storvatnet/1962.Inflow' (TimeseriesCalculation)
    Time interval:              01.09.2021 - 15.09.2021
    Historical date:            07.09.2021
    Calculation expression:     ## = @GetTsAsOfTime(@t('.Inflow'),'20210907000000000')

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 9"
            timeseries_attribute_id = '333a4648-bd2a-4331-acd8-ab88e4a1a5f5'
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 15, tzinfo=LOCAL_TIME_ZONE)
            historical_date = datetime(2021, 9, 7, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the time series attribute
            timeseries_attribute = session.get_timeseries_attribute(
                uuid.UUID(timeseries_attribute_id))

            # Retrieve time series connected to the time series attribute
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(target=timeseries_attribute.id,
                                                        start_time=start,
                                                        end_time=end)
            print(f"{timeseries_attribute_id}: \n"
                  f"-----\n"
                  f"{timeseries_attribute}")

            pandas_dataframe = timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(('Original', pandas_dataframe))

            historical_timeseries = session.history_functions(
                timeseries_attribute.id, start_time=start, end_time=end).get_ts_as_of_time(
                    available_at_timepoint=historical_date)

            pandas_dataframe = historical_timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append((f'History on {historical_date.strftime("%Y%m%d%H%M%S")}', pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: historical data",
                            style='step'
                            )
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_9')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_10():
    """
    Scenario:
    We want to get the last 5 historical versions of a known time series.

    Time series attribute ID:   f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd which is:
                                Model/MeshTEK/Mesh/Norge/HydroForecast/Mørre/Mørre.Inflow (TimeseriesCalculation)
    Time interval:              01.09.2021 - 15.09.2021
    Number of versions to get:  5
    Calculation expression:     ## = @GetTsHistoricalVersions(@t('.Inflow'),5)

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 10"
            timeseries_attribute_id = 'f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd'
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 15, tzinfo=LOCAL_TIME_ZONE)
            max_number_of_versions_to_get = 5
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the time series attribute
            timeseries_attribute = session.get_timeseries_attribute(
                uuid.UUID(timeseries_attribute_id))

            # Retrieve time series connected to the time series attribute
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(target=timeseries_attribute.id,
                                                        start_time=start,
                                                        end_time=end)
            print(f"{timeseries_attribute_id}: \n"
                  f"-----\n"
                  f"{timeseries_attribute}")
            pandas_dataframe = timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(('Original', pandas_dataframe))

            # Get historical time series
            historical_timeseries = session.history_functions(
                timeseries_attribute.id, start_time=start, end_time=end).get_ts_historical_versions(
                    max_number_of_versions_to_get)

            for number, timeseries in enumerate(historical_timeseries):
                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                path_and_pandas_dataframe.append((f'Version {number}', pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: historical versions",
                            style='step'
                            )
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_10')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_11():
    """
    Scenario:
    We want to get all forecasts of a known time series.

    Time series attribute ID:   f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd which is:
                                Model/MeshTEK/Mesh/Norge/HydroForecast/Mørre/Mørre.Inflow (TimeseriesCalculation)
    Time interval:              01.09.2021 - 28.09.2021
    Calculation expression:     ## = @GetAllForecasts(@t('.Inflow'))

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 11"
            timeseries_attribute_id = 'f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd'
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 28, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the time series attribute
            timeseries_attribute = session.get_timeseries_attribute(
                uuid.UUID(timeseries_attribute_id))

            # Retrieve time series connected to the time series attribute
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(target=timeseries_attribute.id,
                                                        start_time=start,
                                                        end_time=end)
            print(f"{timeseries_attribute_id}: \n"
                  f"-----\n"
                  f"{timeseries_attribute}")
            pandas_dataframe = timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(('Original', pandas_dataframe))

            # Get forecast time series
            forecast_timeseries = session.forecast_functions(
                timeseries_attribute.id, start_time=start, end_time=end).get_all_forecasts()

            for number, timeseries in enumerate(forecast_timeseries):
                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                path_and_pandas_dataframe.append((f'Version {number}', pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: get all forecasts"
                            )
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_11')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_12():
    """
    Scenario:
    We want to get some specific forecasts for a known time series.

    Time series attribute ID:   f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd which is:
                                Model/MeshTEK/Mesh/Norge/HydroForecast/Mørre/Mørre.Inflow (TimeseriesCalculation)
    Time interval:              01.09.2021 - 12.10.2021
    Calculation expression:     ## = @GetForecast(@t('.Inflow'),'20210831000000000','20210902000000000','20210901090000000')

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 12"
            timeseries_attribute_id = 'f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd'
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 12, tzinfo=LOCAL_TIME_ZONE)
            forecast_start_min = datetime(2021, 8, 31, tzinfo=LOCAL_TIME_ZONE)
            forecast_start_max = datetime(2021, 9, 2, tzinfo=LOCAL_TIME_ZONE)
            available_at_timepoint = datetime(2021, 9, 1, 9, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the time series attribute
            timeseries_attribute = session.get_timeseries_attribute(
                uuid.UUID(timeseries_attribute_id))

            # Retrieve time series connected to the time series attribute
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(target=timeseries_attribute.id,
                                                        start_time=start,
                                                        end_time=end)
            print(f"{timeseries_attribute_id}: \n"
                  f"-----\n"
                  f"{timeseries_attribute}")
            pandas_dataframe = timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(('Original', pandas_dataframe))

            # Get forecast time series
            forecast_timeseries = session.forecast_functions(
                timeseries_attribute.id, start_time=start, end_time=end).get_forecast(
                    forecast_start_min, forecast_start_max, available_at_timepoint=available_at_timepoint)

            pandas_dataframe = forecast_timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append((f'Forecast for {available_at_timepoint.strftime("%Y%m%d%H%M%S")}', pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: get some forecasts"
                            )
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_12')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_13():
    """
    Scenario:
    We want to find all objects of type `WindPark` for a specific `WindProduction` object.

    Start point:        Model/MeshTEK/Mesh/Norge/Wind which has guid d9673f4f-d117-4c1e-9ffd-0e533a644728
    Search expression:  *[.Type=WindPark]

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 13"
            start_object_guid = uuid.UUID("d9673f4f-d117-4c1e-9ffd-0e533a644728")  # Model/MeshTEK/Mesh/Norge/Wind
            search_query = '*[.Type=WindPark]'

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            objects = session.search_for_objects(start_object_guid, search_query)

            for number, object in enumerate(objects):
                print(f"{number + 1}. \n"
                      f"-------------------------------------------\n"
                      f"{get_object_information(object)}")

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_14():
    """
    Scenario:
    We want to create new objects of type `WindPark` for a specific `WindProduction` object.

    Parent object:      Model/MeshTEK/Mesh/Norge/Wind which has guid d9673f4f-d117-4c1e-9ffd-0e533a644728
    New objects:        NewWindPark, NewWindPark2, NewWindPark3
    New object's type:  WindPark

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 14"
            parent_object_guid = uuid.UUID("d9673f4f-d117-4c1e-9ffd-0e533a644728")  # Model/MeshTEK/Mesh/Norge/Wind
            new_object_type = 'WindPark'
            new_objects_names = ["NewWindPark", "NewWindPark2", "NewWindPark3"]

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Owner of the new object must be a relationship attribute of Object Collection type.
            # E.g.: for `SomePowerPlant1` object with path:
            # - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1
            # Owner will be the `ThermalPowerToPlantRef` attribute.

            # First we need to find correct relationship attribute that
            # will serve as owner for the new objects.
            parent_object = session.get_object(
                parent_object_guid, full_attribute_info=True)
            relationship_attribute_path = None

            for attribute in parent_object.attributes.values():
                if (attribute.definition.value_type == 'ElementCollectionAttributeDefinition' and
                    attribute.definition.object_type == new_object_type):
                    relationship_attribute_path = attribute.path

            if relationship_attribute_path is None:
                print(f"Required relationship attribute (type='{new_object_type}') not found")
                return

            for number, new_object_name in enumerate(new_objects_names):
                new_object = session.create_object(
                    relationship_attribute_path, new_object_name)
                print(f"{number + 1}. \n"
                      f"-------------------------------------------\n"
                      f"{get_object_information(new_object)}")

            # Commit changes
            if COMMIT_CHANGES:
                session.commit()

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_15():
    """
    Scenario:
    We want to delete some existing objects of type `WindPark`, named `Roan`.

    Parent object path: Model/MeshTEK/Mesh/Norge/Wind
    Objects to delete:  NewWindPark2, NewWindPark3

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 15"
            parent_object_path = "Model/MeshTEK/Mesh/Norge/Wind"
            objects_names = ["NewWindPark2", "NewWindPark3"]

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            for object_name in objects_names:
                object_path = f"{parent_object_path}/{object_name}"
                session.delete_object(object_path, recursive_delete=True)
                print(f"Object: '{object_path}' was deleted")

            # Commit changes
            if COMMIT_CHANGES:
                session.commit()

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_16():
    """
    Scenario:
    We want to rename a specific, existing object of type `WindPark`, named `NewWindPark`.

    Object path:        Model/MeshTEK/Mesh/Norge/Wind/NewWindPark
    New object name:    NewestWindPark
    
    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 16"
            parent_object_path = "Model/MeshTEK/Mesh/Norge/Wind"
            old_object_name = "NewWindPark"
            new_object_name = "NewestWindPark"

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            old_object_path = f"{parent_object_path}/{old_object_name}"
            new_object_path = f"{parent_object_path}/{new_object_name}"

            session.update_object(old_object_path, new_name=new_object_name)
            updated_object = session.get_object(new_object_path)
            print(get_object_information(updated_object))

            # Commit changes
            if COMMIT_CHANGES:
                session.commit()

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_17():
    """
    Scenario:
    For a specific object of type `WindPark`, named `Bessaker` we want to find all attributes
    (except TimeseriesAttributes).

    Object path: Model/MeshTEK/Mesh/Norge/Wind/Bessaker which has guid d3c41952-504d-4a47-b06c-c07e901c1c5b

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 17"
            object_guid = uuid.UUID("d3c41952-504d-4a47-b06c-c07e901c1c5b")

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            object = session.get_object(object_guid, full_attribute_info=True)
            print(get_object_information(object))

            number = 1
            for attribute in object.attributes.values():
                if attribute.definition.value_type != 'TimeseriesAttributeDefinition':
                    print(f"{number}. \n"
                        f"-------------------------------------------\n"
                        f"{attribute}")
                    number += 1

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_18():
    """
    Scenario:
    For a specific object of type `WindPark`, named `Bessaker` we want to find all attributes
    (except TimeseriesAttributes) with specific namespace and tags.

    Object path:    Model/MeshTEK/Mesh/Norge/Wind/Bessaker which has guid d3c41952-504d-4a47-b06c-c07e901c1c5b
    Tags:           ProductionProperties, SystemSettings
    Namespace:      Wind

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 18"
            object_guid = uuid.UUID("d3c41952-504d-4a47-b06c-c07e901c1c5b")

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            tags = ['ProductionProperties', 'SystemSettings']
            namespaces = ['Wind']
            attributes_filter = AttributesFilter(tag_mask=tags, namespace_mask=namespaces)

            object = session.get_object(object_guid,
                full_attribute_info=True,
                attributes_filter=attributes_filter)
            print(get_object_information(object))

            number = 1
            for attribute in object.attributes.values():
                if attribute.definition.value_type != 'TimeseriesAttributeDefinition':
                    print(f"{number}. \n"
                        f"-------------------------------------------\n"
                        f"{attribute}")
                    number += 1

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_19():
    """
    Scenario:
    We want to update 2 attributes of a specific, existing object of type
    `WindPark`, named `NewestWindPark`.

    Object path:            Model/MeshTEK/Mesh/Norge/Wind/NewWindPark
    Attributes to update:   HubHeight (new value = 100)
                            MaxProduction (new value = 50)

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 19"
            object_path = "Model/MeshTEK/Mesh/Norge/Wind/NewWindPark"

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            names = ['HubHeight', 'MaxProduction']
            attributes_filter = AttributesFilter(name_mask=names)

            print("Attribute values before update:")
            object = session.get_object(object_path,
                attributes_filter=attributes_filter)
            for attribute in object.attributes.values():
                print(attribute)

            session.update_simple_attribute(
                object.attributes['HubHeight'].path, value=100)

            session.update_simple_attribute(
                object.attributes['MaxProduction'].path, value=50)

            print("\nAttribute values after update:")
            object = session.get_object(object_path,
                attributes_filter=attributes_filter)
            for attribute in object.attributes.values():
                print(attribute)

            # Commit changes
            if COMMIT_CHANGES:
                session.commit()

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_20():
    """Add an XY-set version at 2022-01-01 to a versioned XY-set attribute.

    Attribute path: Model/MeshTEK/Mesh/Norge/Wind/Bessaker/T01.WindPowerCurve
    """
    use_case_name = "Use case 20"
    target = "Model/MeshTEK/Mesh/Norge/Wind/Bessaker/T01.WindPowerCurve"

    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            print(f"{use_case_name}")
            print("--------------------------------------------------------------")

            xy_sets = session.get_xy_sets(target, datetime.min, datetime.max)
            print(f"Attribute value before update: {xy_sets}")

            start_time = datetime(2022, 1, 1, tzinfo=LOCAL_TIME_ZONE)
            new_xy_set = XySet(valid_from_time=start_time,
                               xy_curves=[XyCurve(0.0, [(1.0, 15), (2.0, 30)])])
            session .update_xy_sets(target, start_time, datetime.max, [new_xy_set])

            xy_sets = session.get_xy_sets(target, datetime.min, datetime.max)
            print(f"Attribute value after update: {xy_sets}")

            # Commit changes
            if COMMIT_CHANGES:
                session.commit()

        except grpc.RpcError as e:
            print(f"use case 20 resulted in a error: {e}")


def use_case_21():
    """
    Scenario:
    We want to read specific rating curve attribute information and its rating
    curve versions.

    Attribute path: Model/MeshTEK/Mesh/Norge/Målestasjoner/Nidelva/Kobberdammen.HydStationRatingCurve
    Time interval:  10.01.2020 - 27.03.2022

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 21"
            attribute_path = "Model/MeshTEK/Mesh/Norge/Målestasjoner/Nidelva/Kobberdammen.HydStationRatingCurve"
            start = datetime(2012, 1, 10, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2022, 3, 27, tzinfo=LOCAL_TIME_ZONE)

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # First read the attribute using `get_attribute`.
            # We can get standard information like name, ID, tags, etc.
            rating_curve_attribute = session.get_attribute(
                attribute_path, full_attribute_info=True)
            print(f"Basic information about the rating curve attribute:\n{rating_curve_attribute}\n")

            # Because the rating curve can potentially contain large amounts of data,
            # specialized methods exist to handle those values.
            versions = session.get_rating_curve_versions(
                target=attribute_path,
                start_time=start,
                end_time=end)

            print((
                f"There is/are {len(versions)} rating curve version(s) for the time interval: "
                f"{start:%d.%m.%Y} - {end:%d.%m.%Y}:\n"
            ))
            for i, version in enumerate(versions):
                print(f'Version {i+1}:\n{version}')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_22():
    """
    Scenario:
    We want to update specific rating curve attribute with new rating curve
    versions.

    Attribute path: Model/MeshTEK/Mesh/Norge/Målestasjoner/Orkla/Svorkmo.HydStationRatingCurve
    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 22"
            attribute_path = "Model/MeshTEK/Mesh/Norge/Målestasjoner/Orkla/Svorkmo.HydStationRatingCurve"

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            new_versions = []
            new_versions.append(
                RatingCurveVersion(
                    valid_from_time=datetime(2017, 5, 1, tzinfo=LOCAL_TIME_ZONE),
                    x_range_from=1.0,
                    x_value_segments=[
                        RatingCurveSegment( 3,  3, 22.1, -1.1),
                        RatingCurveSegment( 5,  4, -1.2,  2.7),
                        RatingCurveSegment(20, 15,  2.5, 34.3)
                    ]
                )
            )
            new_versions.append(
                RatingCurveVersion(
                    valid_from_time=datetime(2022, 1, 1, tzinfo=LOCAL_TIME_ZONE),
                    x_range_from=1.0,
                    x_value_segments=[
                        RatingCurveSegment( 2,   5,  0, 1),
                        RatingCurveSegment( 4,  12, -1, 2),
                        RatingCurveSegment(10, 100, -2, 3)
                    ]
                )
            )

            session.update_rating_curve_versions(
                target=attribute_path,
                start_time=new_versions[0].valid_from_time,
                end_time=datetime.max,
                new_versions=new_versions)

            # Now read it.
            versions = session.get_rating_curve_versions(
                target=attribute_path,
                start_time=datetime.min,
                end_time=datetime.max)

            print("Rating curve versions:")
            for i, version in enumerate(versions):
                print(f'Version {i+1}:\n{version}')

            # Commit changes
            if COMMIT_CHANGES:
                session.commit()

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_23():
    """
    Scenario:
    We want to delete rating curve versions from specific rating curve attribute.

    Attribute path: Model/MeshTEK/Mesh/Norge/Målestasjoner/Orkla/Svorkmo.HydStationRatingCurve

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 23"
            attribute_path = "Model/MeshTEK/Mesh/Norge/Målestasjoner/Orkla/Svorkmo.HydStationRatingCurve"

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # First read current versions, with `versions_only` flag
            # because we need only versions' `valid_from_time` timestamps.
            versions = session.get_rating_curve_versions(
                target=attribute_path,
                start_time=datetime.min,
                end_time=datetime.max,
                versions_only=True)

            # Remove last version by replacing last version
            # interval with empty new version.
            session.update_rating_curve_versions(
                target=attribute_path,
                start_time=versions[-1].valid_from_time,
                end_time=datetime.max,
                new_versions=[])

            # Now read it.
            versions = session.get_rating_curve_versions(
                target=attribute_path,
                start_time=datetime.min,
                end_time=datetime.max)
            print("Rating curve versions after removing the last version:")
            for i, version in enumerate(versions):
                print(f'Version {i+1}:\n{version}')

            # Rollback the changes.
            session.rollback()
            print("Rollback done. All versions are back.")

            # Now remove all versions with `valid_from_time` timestamps within
            # the specified time interval by replacing them with empty new
            # version.
            session.update_rating_curve_versions(
                target=attribute_path,
                start_time=datetime.min,
                end_time=datetime(2019, 1, 1, tzinfo=LOCAL_TIME_ZONE),
                new_versions=[])

            # Now read it.
            versions = session.get_rating_curve_versions(
                target=attribute_path,
                start_time=datetime.min,
                end_time=datetime.max)

            print("Rating curve versions after removing the first version:")
            for i, version in enumerate(versions):
                print(f'Version {i+1}:\n{version}')

            # Now remove all versions by replacing the whole time interval
            # [min, max) interval with empty new version.
            session.update_rating_curve_versions(
                target=attribute_path,
                start_time=datetime.min,
                end_time=datetime.max,
                new_versions=[])

            versions = session.get_rating_curve_versions(
                target=attribute_path,
                start_time=datetime.min,
                end_time=datetime.max)

            if len(versions) == 0:
                print("Removed all rating curve versions.")

            # Commit changes
            if COMMIT_CHANGES:
                session.commit()

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        RUN_USE_CASE = sys.argv[1]

    ALL_USE_CASE_FUNCTIONS = {key.strip('use_case_'): value for key, value in locals().items() if 'use_case_' in key}

    if RUN_USE_CASE in ALL_USE_CASE_FUNCTIONS.keys():
        ALL_USE_CASE_FUNCTIONS[RUN_USE_CASE]()
    elif RUN_USE_CASE == 'all':
        for _, use_case in ALL_USE_CASE_FUNCTIONS.items():
            use_case()
    elif RUN_USE_CASE == 'flow_drop_2':
        flow_drop_2_use_cases = ['1', '2', '3', '4', '4b', '5']
        for use_case_key in flow_drop_2_use_cases:
            if use_case_key in ALL_USE_CASE_FUNCTIONS.keys():
                ALL_USE_CASE_FUNCTIONS[use_case_key]()
    elif RUN_USE_CASE == 'flow_drop_3':
        flow_drop_3_use_cases = ['6', '7', '8', '9', '10', '11', '12']
        for use_case_key in flow_drop_3_use_cases:
            if use_case_key in ALL_USE_CASE_FUNCTIONS.keys():
                ALL_USE_CASE_FUNCTIONS[use_case_key]()
    elif RUN_USE_CASE == 'flow_drop_4':
        flow_drop_4_use_cases = ['13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
        for use_case_key in flow_drop_4_use_cases:
            if use_case_key in ALL_USE_CASE_FUNCTIONS.keys():
                ALL_USE_CASE_FUNCTIONS[use_case_key]()
    else:
        default_use_case = ALL_USE_CASE_FUNCTIONS['1']
        print(f"Invalid use case selected: {RUN_USE_CASE}, selecting default use case {default_use_case.__name__}")
        default_use_case()


