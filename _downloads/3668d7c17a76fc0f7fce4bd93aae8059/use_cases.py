from datetime import datetime, timedelta, timezone
import sys
from typing import List, Any, Tuple
import uuid

from dateutil import tz
import grpc
import matplotlib.pyplot as plt
import pandas as pd
import pyarrow as pa

from volue.mesh import Connection, MeshObjectId, Timeseries
from volue.mesh._common import _from_proto_guid
from volue.mesh.calc import transform as Transform
from volue.mesh.calc.common import Timezone
from volue.mesh.proto.core.v1alpha import core_pb2

"""
These use cases were designed to work with a real customer database (TEKICC_ST@MULLIGAN)
"""

# Ip address for the Mesh server
HOST = "localhost"
# Mesh server port for gRPC communication
PORT = 50051
# Use matplotlib to visualize results
SHOW_PLOT = True
# Save timeseries to CSV file
SAVE_TO_CSV = True
# Which use case to run
# ['all', 'flow_drop_2', 'flow_drop_3', '1' ... '<number_of_use_cases>']
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
    """
    Plots a list of pandas dataframes in a figure.
    """
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


def get_resource_information(resource_object: core_pb2.TimeseriesEntry):
    """
    Create a printable message from a resource object
    """
    message = f"Timeseries with timskey: '{resource_object.timeseries_key}' \n"\
              f"has guid: '{_from_proto_guid(resource_object.id)}', \n"\
              f"path set in the resource silo is: '{resource_object.path}', \n"\
              f"it's curve '{resource_object.curve_type}', \n"\
              f"resolution '{resource_object.resolution}' \n"\
              f"and unit of measurement is: '{resource_object.unit_of_measurement}'\n"
    return message


def get_mesh_object_information(mesh_object: core_pb2.TimeseriesAttribute):
    """
    Create a printable message from a mesh object
    """

    message = f"Mesh object with path: '{mesh_object.path}'  \n"\
              f"has guid: '{_from_proto_guid(mesh_object.id)}', \n"\
              f"its local expression is set to: '{mesh_object.local_expression}' \n"\
              f"and its template expression is: '{mesh_object.template_expression}' \n"
    if hasattr(mesh_object, 'entry') and (mesh_object.entry.timeseries_key != 0):
        message += "It has a timeseries entry connected to it: \n"
        message += get_resource_information(mesh_object.entry)
    return message


def get_mesh_element_information(mesh_element: core_pb2.Object):
    message = f"Mesh object with path: '{mesh_element.path}'  \n"\
              f"has guid: '{_from_proto_guid(mesh_element.id)}', \n"\
              f"name: '{mesh_element.name}', \n"\
              f"type name: '{mesh_element.type_name}', \n"\
              f"owner path: '{mesh_element.owner_id.path}', \n"\
              f"owner guid: '{_from_proto_guid(mesh_element.owner_id.id)}', \n"
    return message

def get_timeseries_information(timeseries: Timeseries):
    """
    Create a printable message from a timeseries
    """
    message = f"Timeseries full name: '{timeseries.full_name}', " \
              f"uuid: '{timeseries.uuid}', " \
              f"timeskey: '{timeseries.timskey}', " \
              f"start time: '{str(timeseries.start_time)}', " \
              f"end time: '{str(timeseries.end_time)}', " \
              f"resolution: '{timeseries.resolution}', " \
              f" it has '{timeseries.number_of_points}' points " \
              f"and this is some of them: \n" \
              f"{timeseries.arrow_table.to_pandas()}"

    return message


def use_case_1():
    """
    Scenario:
    We want to find all timeseries which show the production of a hydro plant.

    Start point:        Model/MeshTEK/Mesh which has guid 801896b0-d448-4299-874a-3ecf8ab0e2d4
    Search expression:  *[.Type=HydroPlant].Production_operative
    Time interval:      1.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 1"
            model = "MeshTEK"
            start_object_guid = uuid.UUID("801896b0-d448-4299-874a-3ecf8ab0e2d4")  # Model/MeshTEK/Mesh
            search_query = "*[.Type=HydroPlant].Production_operative"
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 1, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Search for mesh objects
            search_matches = session.search_for_timeseries_attribute(model=model,
                                                                     start_object_guid=start_object_guid,
                                                                     query=search_query)
            print(f"Search resulted in {len(search_matches)} object(s) that match(es) the search criteria: {search_query}")

            # Retrieve timeseries connected to the mesh objects found
            path_and_pandas_dataframe = []
            for number, mesh_object in enumerate(search_matches):
                timeseries = session.read_timeseries_points(start_time=start,
                                                            end_time=end,
                                                            mesh_object_id=MeshObjectId.with_uuid_id(mesh_object.id))
                print(f"{number + 1}. \n"
                      f"-----\n"
                      f"{get_mesh_object_information(mesh_object)}")
                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                path_and_pandas_dataframe.append((mesh_object.path, pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe, f"{use_case_name}: {search_query}")
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_1')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_2():
    """
    Scenario:
    We want to find timeseries which contain reservoir volume for all reservoirs in Norway (Norge).

    Start point:        Model/MeshTEK/Mesh which has guid 801896b0-d448-4299-874a-3ecf8ab0e2d4
    Search expression:  *[.Type=Area&&.Name=Norge]/To_HydroProduction/To_WaterCourses/To_Reservoirs.ReservoirVolume_operative
    Time interval:      1.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 2"
            model = "MeshTEK"
            start_object_guid = uuid.UUID("801896b0-d448-4299-874a-3ecf8ab0e2d4")  # Model/MeshTEK/Mesh
            search_query = "*[.Type=Area&&.Name=Norge]/To_HydroProduction/To_WaterCourses/To_Reservoirs.ReservoirVolume_operative"
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 1, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Search for mesh objects
            search_matches = session.search_for_timeseries_attribute(model=model,
                                                                     start_object_guid=start_object_guid,
                                                                     query=search_query)
            print(f"Search resulted in {len(search_matches)} object(s) that match(es) the search criteria: {search_query}")

            # Retrieve timeseries connected to the mesh objects found
            path_and_pandas_dataframe = []
            for number, mesh_object in enumerate(search_matches):
                timeseries = session.read_timeseries_points(start_time=start,
                                                            end_time=end,
                                                            mesh_object_id=MeshObjectId.with_uuid_id(mesh_object.id))
                print(f"{number + 1}. \n"
                      f"-----\n"
                      f"{get_mesh_object_information(mesh_object)}")
                pandas_dataframe = timeseries.arrow_table.to_pandas()
                # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
                pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
                path_and_pandas_dataframe.append((mesh_object.path, pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe, f"{use_case_name}: {search_query}")
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_2')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_3():
    """
    Scenario:
    We want to find timeseries which has a known timskey.

    Timskeys:           [530, 536, 537, 543, 556]
    Time interval:      1.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 3"
            model = "MeshTEK"
            timskeys = [530, 536, 537, 543, 556]
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 1, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timskey_and_pandas_dataframe = []
            for timskey in timskeys:

                # Get information about the timeseries
                resource_object = session.get_timeseries_resource_info(timskey=timskey)
                print(f"[{timskey}]: \n"
                      f"-----\n"
                      f"{get_resource_information(resource_object)}")

                # Retrieve the timeseries values in a given interval
                timeseries = session.read_timeseries_points(start_time=start,
                                                            end_time=end,
                                                            mesh_object_id=MeshObjectId.with_timskey(timskey))
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
    We want to find timeseries, and its related information, which is connected to an object with a known guid.

    Guids:              [
                        "ff1db73f-8c8a-42f8-a44a-4bbb420874c1"
                        ]
    Time interval:      10.01.2022 - 27.03.2022

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 4"
            model = "MeshTEK"
            guids = [
                "ff1db73f-8c8a-42f8-a44a-4bbb420874c1"
            ]
            start = datetime(2022, 1, 10, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2022, 3, 27, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timskey_and_pandas_dataframe = []
            for guid in guids:

                # Retrieve the timeseries values in a given interval
                timeseries = session.read_timeseries_points(start_time=start,
                                                            end_time=end,
                                                            mesh_object_id=MeshObjectId.with_uuid_id(uuid.UUID(guid)))

                # Retrieve information connected to the timeseries
                mesh_object = session.get_timeseries_attribute(model=model,
                                                               uuid_id=uuid.UUID(guid))

                print(f"[{guid}]: \n"
                      f"-----\n"
                      f"{get_mesh_object_information(mesh_object)}")

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
    We want to find timeseries, and its related information, which is connected to an object with a known path.
    This use cases shows usage of two path types (including full name) that point to the same time series attribute.

    Time interval:      10.01.2022 - 27.03.2022

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 4b"
            model = "MeshTEK"
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

                # Retrieve the timeseries values in a given interval
                timeseries = session.read_timeseries_points(start_time=start,
                                                            end_time=end,
                                                            mesh_object_id=MeshObjectId.with_full_name(path))

                # Retrieve information connected to the timeseries
                mesh_object = session.get_timeseries_attribute(model=model,
                                                               path=path)

                print(f"[{path}]: \n"
                      f"-----\n"
                      f"{get_mesh_object_information(mesh_object)}")

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
    We want to write some values to an existing timeseries with a known guid.

    Guid:              ['3fd4ed37-2114-4d95-af90-02b96bd993ed']  # Model/MeshTEK/Mesh.To_Areas/Norge.To_HydroProduction/Vannkraft.To_WaterCourses/Mørre.To_HydroPlants/Mørre.To_Units/Morre G1.Production_raw
    Time interval:      28.09.2021 - 29.09.2021
    Values:             [11.50, 11.91, 11.88, 11.86, 11.66, 11.73, 11.80, 11.88, 11.97, 9.87, 9.47, 9.05,
                        9.20, 9.00, 8.91, 10.62, 12.00, 12.07, 12.00, 11.78, 5.08, 0.00, 0.00, 0.00]

    """
    connection = Connection(host=HOST, port=PORT)

    with connection.create_session() as session:
        try:
            use_case_name = "Use case 5"
            model = "MeshTEK"
            guid = uuid.UUID('3fd4ed37-2114-4d95-af90-02b96bd993ed')

            start = datetime(2021, 9, 28, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 29, tzinfo=LOCAL_TIME_ZONE)

            resolution = timedelta(hours=1.0)
            timskey_and_pandas_dataframe = []
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Get timeseries data before write
            timeseries_before = session.read_timeseries_points(start_time=start,
                                                               end_time=end,
                                                               mesh_object_id=MeshObjectId.with_uuid_id(guid))
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

            # Send request to write timeseries based on timskey
            session.write_timeseries_points(timeserie=timeseries)

            # Get timeseries data before write
            timeseries_after = session.read_timeseries_points(start_time=start,
                                                              end_time=end,
                                                              mesh_object_id=MeshObjectId.with_uuid_id(guid))
            print(f"After writing points: \n"
                  f"-----\n"
                  f"{get_timeseries_information(timeseries=timeseries_after)}")

            pandas_dataframe = timeseries_after.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            timskey_and_pandas_dataframe.append(("after", pandas_dataframe))

            # Commit changes
            session.commit()

            plot_timeseries(timskey_and_pandas_dataframe,
                            f"{use_case_name}: Before and after writing")
            save_timeseries_to_csv(timskey_and_pandas_dataframe, 'use_case_5')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_6():
    """
    Scenario:
    We want to transform existing timeseries from breakpoint resolution to hourly.

    Object guid:                '012d70e3-8f40-40af-9c0a-5d84fc239776'
    Transformation expression:  ## = @TRANSFORM(Object guid,'HOUR','AVGI')
    Time interval:              5.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 6"
            model = "MeshTEK"
            object_guid = '012d70e3-8f40-40af-9c0a-5d84fc239776'
            start = datetime(2021, 9, 5, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 1, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information connected to the timeseries
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh object
            path_and_pandas_dataframe = []
            timeseries_original = session.read_timeseries_points(start_time=start,
                                                                 end_time=end,
                                                                 mesh_object_id=MeshObjectId.with_uuid_id(mesh_object.id))
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"{get_mesh_object_information(mesh_object)}")

            pandas_dataframe = timeseries_original.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append((f"original", pandas_dataframe))

            # Transform timeseries from breakpoint to hourly
            timeserie_transformed = session.transform_functions(
                MeshObjectId(uuid_id=mesh_object.id), start_time=start, end_time=end).transform(
                    Timeseries.Resolution.HOUR, Transform.Method.AVGI, Timezone.LOCAL)

            pandas_dataframe = timeserie_transformed.arrow_table.to_pandas()
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
    We want to transform existing timeseries from hourly resolution to daily.

    Object guid:                '7608c9e2-c4fc-4570-b5b2-069f29a34f22' which is:
                                Model/MeshTEK/Mesh/Norge/Vannkraft/Mørre/Mørre.Production_operative (TimeseriesCalculation)
    Transformation expression:  ## = @TRANSFORM(Object guid,'DAY','AVG')
    Time interval:              5.09.2021 - 15.09.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 7"
            model = "MeshTEK"
            object_guid = '7608c9e2-c4fc-4570-b5b2-069f29a34f22'
            start = datetime(2021, 9, 5, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 15, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information connected to the timeseries
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh object
            path_and_pandas_dataframe = []
            timeseries_original = session.read_timeseries_points(start_time=start,
                                                                 end_time=end,
                                                                 mesh_object_id=MeshObjectId.with_uuid_id(mesh_object.id))
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"{get_mesh_object_information(mesh_object)}")

            pandas_dataframe = timeseries_original.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append((f"original", pandas_dataframe))

            # Transform timeseries from hourly to daily
            timeserie_transformed = session.transform_functions(
                MeshObjectId(uuid_id=mesh_object.id), start_time=start, end_time=end).transform(
                    Timeseries.Resolution.DAY, Transform.Method.AVG, Timezone.LOCAL)

            pandas_dataframe = timeserie_transformed.arrow_table.to_pandas()
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
    We want to summarize an array of timeseries

    Start point:                36395abf-9a39-40ef-b29c-b1d59db855e3
    Search expression:          *[.Type=Reservoir].ReservoirVolume_operative
    Calculation expression:     ## = @SUM(@T('*[.Type=Reservoir].ReservoirVolume_operative'))
    Time interval:              5.9.2021 - 15.9.2021

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 8"
            model = "MeshTEK"
            start_object_guid = '36395abf-9a39-40ef-b29c-b1d59db855e3'
            search_query = "*[.Type=Reservoir].ReservoirVolume_operative"
            start = datetime(2021, 9, 5, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 15, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Summarize timeseries
            summarized_timeseries = session.statistical_functions(
                MeshObjectId(uuid_id=uuid.UUID(start_object_guid)), start_time=start, end_time=end).sum(
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
    We want to get the historical data for a timeseries on a specific date.

    Mesh object:                333a4648-bd2a-4331-acd8-ab88e4a1a5f5 which is:
                                Model/MeshTEK/Cases/Morre_Short_Opt/Norge/Vannkraft/Mørre/Mørre/Storvatnet/1962.Inflow' (TimeseriesCalculation)
    Time interval:              01.09.2021 - 15.09.2021
    Historical date:            07.09.2021
    Calculation expression:     ## = @GetTsAsOfTime(@t('.Inflow'),'20210907000000000')

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 9"
            model = "MeshTEK"
            object_guid = '333a4648-bd2a-4331-acd8-ab88e4a1a5f5'
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 15, tzinfo=LOCAL_TIME_ZONE)
            historical_date = datetime(2021, 9, 7, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the object
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh objects found
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        mesh_object_id=MeshObjectId.with_uuid_id(mesh_object.id))
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"{get_mesh_object_information(mesh_object)}")

            pandas_dataframe = timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(('Original', pandas_dataframe))

            historical_timeseries = session.history_functions(
                MeshObjectId(uuid_id=uuid.UUID(object_guid)), start_time=start, end_time=end).get_ts_as_of_time(
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
    We want to get the last 5 historical versions of a known timeseries

    Mesh object:                f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd which is:
                                Model/MeshTEK/Mesh/Norge/HydroForecast/Mørre/Mørre.Inflow (TimeseriesCalculation)
    Time interval:              01.09.2021 - 15.09.2021
    Number of versions to get:  5
    Calculation expression:     ## = @GetTsHistoricalVersions(@t('.Inflow'),5)

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 10"
            model = "MeshTEK"
            object_guid = 'f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd'
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 15, tzinfo=LOCAL_TIME_ZONE)
            max_number_of_versions_to_get = 5
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the object
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh objects found
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        mesh_object_id=MeshObjectId.with_uuid_id(mesh_object.id))
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"{get_mesh_object_information(mesh_object)}")
            pandas_dataframe = timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(('Original', pandas_dataframe))

            # Get historical timeseries
            historical_timeseries = session.history_functions(
                MeshObjectId(uuid_id=uuid.UUID(object_guid)), start_time=start, end_time=end).get_ts_historical_versions(
                    max_number_of_versions_to_get)

            for number, timeserie in enumerate(historical_timeseries):
                pandas_dataframe = timeserie.arrow_table.to_pandas()
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
    We want to get all forecasts for a specific object

    Mesh object:                f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd which is:
                                Model/MeshTEK/Mesh/Norge/HydroForecast/Mørre/Mørre.Inflow (TimeseriesCalculation)
    Time interval:              01.09.2021 - 28.09.2021
    Calculation expression:     ## = @GetAllForecasts(@t('.Inflow'))

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 11"
            model = "MeshTEK"
            object_guid = 'f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd'
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 9, 28, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the object
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh objects found
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        mesh_object_id=MeshObjectId.with_uuid_id(mesh_object.id))
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"{get_mesh_object_information(mesh_object)}")
            pandas_dataframe = timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(('Original', pandas_dataframe))

            # Get forecast timeseries
            forecast_timeseries = session.forecast_functions(
                MeshObjectId(uuid_id=uuid.UUID(object_guid)), start_time=start, end_time=end).get_all_forecasts()

            for number, timeserie in enumerate(forecast_timeseries):
                pandas_dataframe = timeserie.arrow_table.to_pandas()
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
    We want to get some specific forecasts for an object

    Mesh object:                f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd which is:
                                Model/MeshTEK/Mesh/Norge/HydroForecast/Mørre/Mørre.Inflow (TimeseriesCalculation)
    Time interval:              01.09.2021 - 12.10.2021
    Calculation expression:     ## = @GetForecast(@t('.Inflow'),'20210831000000000','20210902000000000','20210901090000000')

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 12"
            model = "MeshTEK"
            object_guid = 'f84ab6f7-0c92-4006-8fc3-ffa0c9e2cefd'
            start = datetime(2021, 9, 1, tzinfo=LOCAL_TIME_ZONE)
            end = datetime(2021, 10, 12, tzinfo=LOCAL_TIME_ZONE)
            forecast_start_min = datetime(2021, 8, 31, tzinfo=LOCAL_TIME_ZONE)
            forecast_start_max = datetime(2021, 9, 2, tzinfo=LOCAL_TIME_ZONE)
            available_at_timepoint = datetime(2021, 9, 1, 9, tzinfo=LOCAL_TIME_ZONE)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the object
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh objects found
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        mesh_object_id=MeshObjectId.with_uuid_id(mesh_object.id))
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"{get_mesh_object_information(mesh_object)}")
            pandas_dataframe = timeseries.arrow_table.to_pandas()
            # Post processing: convert to UTC timezone-aware datetime object and then to given time zone
            pandas_dataframe['utc_time'] = pd.to_datetime(pandas_dataframe['utc_time'], utc=True).dt.tz_convert(LOCAL_TIME_ZONE)
            path_and_pandas_dataframe.append(('Original', pandas_dataframe))

            # Get forecast timeseries
            forecast_timeseries = session.forecast_functions(
                MeshObjectId(uuid_id=uuid.UUID(object_guid)), start_time=start, end_time=end).get_forecast(
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

            reply = session.search_for_objects(search_query, start_object_id=start_object_guid)

            for number, object in enumerate(reply):
                print(f"{number + 1}. \n"
                      f"-------------------------------------------\n"
                      f"{get_mesh_element_information(object)}")

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_14():
    """
    Scenario:
    We want to create a new object of type `WindPark` for a specific `WindProduction` object.
    First we will search for an existing object of type `WindPark` to get ID or path of
    the relationship attribute that is needed as owner for the new object to create.

    Start point:        Model/MeshTEK/Mesh/Norge/Wind which has guid d9673f4f-d117-4c1e-9ffd-0e533a644728
    Search expression:  *[.Type=WindPark]
    New object name:    NewWindPark

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 14"
            start_object_guid = uuid.UUID("d9673f4f-d117-4c1e-9ffd-0e533a644728")  # Model/MeshTEK/Mesh/Norge/Wind
            search_query = '*[.Type=WindPark]'
            new_object_name = "NewWindPark"

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Get relationship attribute from already existing objects of `WindPark` type
            # Owner of the new object must be a relationship attribute of Object Collection type.
            # E.g.: for `SomePowerPlant1` object with path:
            # - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1
            # Owner will be the `ThermalPowerToPlantRef` attribute.
            reply = session.search_for_objects(search_query, start_object_id=start_object_guid)
            if len(reply) > 0:
                relationship_attribute_path = reply[0].owner_id.path

                new_object = session.create_object(new_object_name, owner_attribute_path=relationship_attribute_path)
                print(get_mesh_element_information(new_object))

                # Commit changes
                #session.commit()

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_15():
    """
    Scenario:
    We want to delete a specific, existing object of type `WindPark`, named `Roan`.

    Object path: Model/MeshTEK/Mesh/Norge/Wind/Roan

    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 15"
            object_path = "Model/MeshTEK/Mesh/Norge/Wind/Roan"

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            session.delete_object(object_path=object_path, recursive_delete=True)

            # Commit changes
            #session.commit()

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_16():
    """
    Scenario:
    We want to rename a specific, existing object of type `WindPark`, named `Roan`.

    Object path:        Model/MeshTEK/Mesh/Norge/Wind/Roan which has guid 8faf6a61-5b3a-443a-8632-c628ea59c86b
    New object name:    Roan2
    
    """
    connection = Connection(host=HOST, port=PORT)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 16"
            object_guid = uuid.UUID("8faf6a61-5b3a-443a-8632-c628ea59c86b")
            new_object_name = "Roan2"

            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            session.update_object(object_id=object_guid, new_name=new_object_name)
            updated_object = session.get_object(object_id=object_guid)
            print(get_mesh_element_information(updated_object))

            # Commit changes
            #session.commit()

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
    else:
        default_use_case = ALL_USE_CASE_FUNCTIONS['1']
        print(f"Invalid use case selected: {RUN_USE_CASE}, selecting default use case {default_use_case.__name__}")
        default_use_case()


