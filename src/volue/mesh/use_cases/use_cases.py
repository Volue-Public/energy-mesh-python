from datetime import datetime, timedelta, timezone
import uuid
from typing import List, Any, Tuple
import pandas as pd
import pyarrow as pa
import matplotlib.pyplot as plt
import grpc
import sys
from volue.mesh import Connection, Timeseries, from_proto_guid, to_proto_guid, to_protobuf_utcinterval, read_proto_reply
from volue.mesh.calc import transform as Transform
from volue.mesh.proto import mesh_pb2

"""
These use cases were designed to work with a real customer database (TEKICC_ST@MULLIGAN)
"""

# Ip address for the mesh server
HOST = "localhost"
# HOST = "tdtrhsmg125b2"
# Mesh server port for gRPC communication
PORT = 50051
# Use matplotlib to visualize results
SHOW_PLOT = True
# Save timeseries to CSV file
SAVE_TO_CSV = True
# Which use case to run
# ['all', 'flow_drop_2', 'flow_drop_3', '1' ... '<number_of_use_cases>']
RUN_USE_CASE = 'all'


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
        plt.xlabel('utc time')
        plt.legend(legends, ncol=2, fontsize=6)
        plt.title(title)
        figure_manager = plt.get_current_fig_manager()
        figure_manager.window.state('zoomed')  # Fullscreen
        plt.show()


def save_timeseries_to_csv(identifier_and_pandas_dataframes: List[Tuple[Any, pd.DataFrame]],
                           file_prefix: str) -> None:
    """
    Saves a pandas dataframe to a CSV file.
    """
    if SAVE_TO_CSV:
        for a_pair in identifier_and_pandas_dataframes:
            timeseries_identifier = str(a_pair[0]).replace('/', '.')
            timeseries_pandas_dataframe = a_pair[1]
            timeseries_pandas_dataframe.to_csv(file_prefix + '_' + timeseries_identifier + '.csv', index=False)


def get_resource_information(resource_object: mesh_pb2.TimeseriesEntry):
    """
    Create a printable message from a resource object
    """
    message = f"Timeseries with timskey: '{resource_object.timeseries_key}' \n"\
              f"has guid: '{from_proto_guid(resource_object.id)}', \n"\
              f"path set in the resource silo is: '{resource_object.path}', \n"\
              f"it's curve '{resource_object.curveType}', \n"\
              f"resolution '{resource_object.delta_t}' \n"\
              f"and unit of measurement is: '{resource_object.unit_of_measurement}'\n"
    return message


def get_mesh_object_information(mesh_object: mesh_pb2.TimeseriesAttribute):
    """
    Create a printable message from a mesh object
    """

    message = f"Mesh object with path: '{mesh_object.path}'  \n"\
              f"has guid: '{from_proto_guid(mesh_object.id)}', \n"\
              f"its local expression is set to: '{mesh_object.local_expression}' \n"\
              f"and its template expression is: '{mesh_object.template_expression}' \n"
    if hasattr(mesh_object, 'entry') and (mesh_object.entry.timeseries_key != 0):
        message += "It has a timeseries entry connected to it: \n"
        message += get_resource_information(mesh_object.entry)
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
              f" it has '{timeseries.number_of_points}' number of points " \
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
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 1"
            model = "MeshTEK"
            start_object_guid = uuid.UUID("801896b0-d448-4299-874a-3ecf8ab0e2d4")  # Model/MeshTEK/Mesh
            search_query = "*[.Type=HydroPlant].Production_operative"
            start = datetime(2021, 9, 1)
            end = datetime(2021, 10, 1)
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
                                                            uuid_id=mesh_object.id)
                print(f"{number + 1}. \n"
                      f"-----\n"
                      f"" + get_mesh_object_information(mesh_object) + f"")
                for timeserie in timeseries:
                    pandas_dataframe = timeserie.arrow_table.to_pandas()
                    path_and_pandas_dataframe.append((mesh_object.path, pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe, f"{use_case_name}: {search_query}")
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_1')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_2():
    """
    Scenario:
    We want to find timeseries which contain reservoir volume for all reservoirs in a Norway (Norge).

    Start point:        Model/MeshTEK/Mesh which has guid 801896b0-d448-4299-874a-3ecf8ab0e2d4
    Search expression:  *[.Type=Area&&.Name=Norge]/To_HydroProduction/To_WaterCourses/To_Reservoirs.ReservoirVolume_operative
    Time interval:      1.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 2"
            model = "MeshTEK"
            start_object_guid = uuid.UUID("801896b0-d448-4299-874a-3ecf8ab0e2d4")  # Model/MeshTEK/Mesh
            search_query = "*[.Type=Area&&.Name=Norge]/To_HydroProduction/To_WaterCourses/To_Reservoirs.ReservoirVolume_operative"
            start = datetime(2021, 9, 1)
            end = datetime(2021, 10, 1)
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
                                                            uuid_id=mesh_object.id)
                print(f"{number + 1}. \n"
                      f"-----\n"
                      f"" + get_mesh_object_information(mesh_object) + f"")
                for timeserie in timeseries:
                    pandas_dataframe = timeserie.arrow_table.to_pandas()
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
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 3"
            model = "MeshTEK"
            timskeys = [530, 536, 537, 543, 556]
            start = datetime(2021, 9, 1)
            end = datetime(2021, 10, 1)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timskey_and_pandas_dataframe = []
            for timskey in timskeys:

                # Get information about the timeseries
                resource_object = session.get_timeseries_resource_info(timskey=timskey)
                print(f"[{timskey}]: \n"
                      f"-----\n"
                      f"" + get_resource_information(resource_object) + f"")

                # Retrieve the timeseries values in a given interval
                timeseries = session.read_timeseries_points(start_time=start,
                                                            end_time=end,
                                                            timskey=timskey)
                for timeserie in timeseries:
                    pandas_dataframe = timeserie.arrow_table.to_pandas()
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
    Time interval:      1.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 4"
            model = "MeshTEK"
            guids = [
                "ff1db73f-8c8a-42f8-a44a-4bbb420874c1"
            ]
            start = datetime(2021, 9, 1)
            end = datetime(2021, 10, 1)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            timskey_and_pandas_dataframe = []
            for guid in guids:

                # Retrieve the timeseries values in a given interval
                timeseries = session.read_timeseries_points(start_time=start,
                                                            end_time=end,
                                                            uuid_id=uuid.UUID(guid))

                # Retrieve information connected to the timeseries
                mesh_object = session.get_timeseries_attribute(model=model,
                                                               uuid_id=uuid.UUID(guid))

                print(f"[{guid}]: \n"
                      f"-----\n"
                      f"" + get_mesh_object_information(mesh_object) + f"")

                for timeserie in timeseries:
                    pandas_dataframe = timeserie.arrow_table.to_pandas()
                    timskey_and_pandas_dataframe.append((guid, pandas_dataframe))

            # Post process data
            plot_timeseries(timskey_and_pandas_dataframe,
                            f"{use_case_name}: {len(guids)} known guids",
                            style='step')
            save_timeseries_to_csv(timskey_and_pandas_dataframe, 'use_case_4')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_5():
    """
    Scenario:
    We want to write some values to an existing timeseries with a known guid.

    Guid:              ['3fd4ed37-2114-4d95-af90-02b96bd993ed']  # Model/MeshTEK/Mesh.To_Areas/Norge.To_HydroProduction/Vannkraft.To_WaterCourses/Mørre.To_HydroPlants/Mørre.To_Units/Morre G1.Production_raw
    Time interval:      28.9.2021, kl 01 - 28.10.2021, kl 24
    Values:             [11.50, 11.91, 11.88, 11.86, 11.66, 11.73, 11.80, 11.88, 11.97, 9.87, 9.47, 9.05,
                        9.20, 9.00, 8.91, 10.62, 12.00, 12.07, 12.00, 11.78, 5.08, 0.00, 0.00, 0.00]

    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)

    with connection.create_session() as session:
        try:
            use_case_name = "Use case 5"
            model = "MeshTEK"
            guid = uuid.UUID('3fd4ed37-2114-4d95-af90-02b96bd993ed')
            start = datetime(2021, 9, 28, 0, 0, 0, tzinfo=timezone.utc)
            end = datetime(2021, 9, 30, 1, 0, 0, tzinfo=timezone.utc)
            resolution = timedelta(hours=1.0)
            timskey_and_pandas_dataframe = []
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Get timeseries data before write
            timeseries_before = session.read_timeseries_points(start_time=start,
                                                               end_time=end,
                                                               uuid_id=guid)
            print(f"Before writing points: \n"
                  f"-----\n"
                  f"" + get_timeseries_information(timeseries=timeseries_before[0])
                  )

            for timeserie in timeseries_before:
                pandas_dataframe = timeserie.arrow_table.to_pandas()
                timskey_and_pandas_dataframe.append(("before", pandas_dataframe))

            # Defining the data we want to write
            # Mesh data is organized as an Arrow table with the following schema:
            # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
            # flags - [pa.uint32]
            # value - [pa.float64]
            timestamps = []
            for i in range(1, 24 + 1):
                timestamps.append(start + resolution * i)

            utc_time = pa.array(timestamps)
            flags = pa.array([0] * 24)  # flag 0 -> Common::TimeseriesPointFlags::Ok
            old_values = pa.array([0.0] * 24)
            new_values = pa.array([11.50, 11.91, 11.88, 11.86, 11.66, 11.73, 11.80, 11.88, 11.97, 9.87, 9.47, 9.05,
                                   9.20, 9.00, 8.91, 10.62, 12.00, 12.07, 12.00, 11.78, 5.08, 0.00, 0.00, 0.00])

            # Write new values
            old_arrays = [
                utc_time,
                flags,
                new_values
            ]
            table = pa.Table.from_arrays(arrays=old_arrays, schema=Timeseries.schema)
            timeseries = Timeseries(table=table, start_time=start, end_time=end, uuid_id=guid)

            # Send request to write timeseries based on timskey
            session.write_timeseries_points(timeserie=timeseries)

            # Get timeseries data before write
            timeseries_after = session.read_timeseries_points(start_time=start,
                                                              end_time=end,
                                                              uuid_id=guid)
            print(f"After writing points: \n"
                  f"-----\n"
                  f"" + get_timeseries_information(timeseries=timeseries_after[0])
                  )

            for timeserie in timeseries_after:
                pandas_dataframe = timeserie.arrow_table.to_pandas()
                timskey_and_pandas_dataframe.append(("after", pandas_dataframe))

            # Commit changes
            session.commit()

            # Reset to old values
            old_arrays = [
                utc_time,
                flags,
                old_values
            ]
            table = pa.Table.from_arrays(arrays=old_arrays, schema=Timeseries.schema)
            timeseries = Timeseries(table=table, start_time=start, end_time=end, uuid_id=guid)

            # Send request to write timeseries based on timskey
            session.write_timeseries_points(timeserie=timeseries)

            # Commit changes
            session.commit()

            # Post process data
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
    Transformation expression:  ##=@TRANSFORM(Object guid,'HOUR','AVGI')
    Time interval:              5.9.2021 - 1.10.2021

    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 6"
            model = "MeshTEK"
            object_guid = '012d70e3-8f40-40af-9c0a-5d84fc239776'
            start = datetime(2021, 9, 5)
            end = datetime(2021, 10, 1)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information connected to the timeseries
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh object
            path_and_pandas_dataframe = []
            timeseries_original = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        uuid_id=mesh_object.id)
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"" + get_mesh_object_information(mesh_object) + f"")
            for timeserie in timeseries_original:
                pandas_dataframe = timeserie.arrow_table.to_pandas()
                path_and_pandas_dataframe.append((f"original", pandas_dataframe))

            # Transform timeseries from breakpoint to hourly
            from_breakpoint_to_hourly = Transform.Parameters(
                resolution=Timeseries.Resolution.HOUR,
                method=Transform.Method.AVGI,
                timezone=Transform.Timezone.UTC
            )

            timeserie_transformed = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        uuid_id=mesh_object.id,
                                                        transformation=from_breakpoint_to_hourly)

            pandas_dataframe = timeserie_transformed.arrow_table.to_pandas()
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

    Object guid:                '7608c9e2-c4fc-4570-b5b2-069f29a34f22'
    Transformation expression:  ##=@TRANSFORM(Object guid,'DAY','AVG')
    Time interval:              5.09.2021 - 15.09.2021


    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 7"
            model = "MeshTEK"
            object_guid = '7608c9e2-c4fc-4570-b5b2-069f29a34f22'
            start = datetime(2021, 9, 5)
            end = datetime(2021, 9, 15)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information connected to the timeseries
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh object
            path_and_pandas_dataframe = []
            timeseries_original = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        uuid_id=mesh_object.id)
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"" + get_mesh_object_information(mesh_object) + f"")
            for timeserie in timeseries_original:
                pandas_dataframe = timeserie.arrow_table.to_pandas()
                path_and_pandas_dataframe.append((f"original", pandas_dataframe))

            # Transform timeseries from breakpoint to hourly
            from_breakpoint_to_hourly = Transform.Parameters(
                resolution=Timeseries.Resolution.DAY,
                method=Transform.Method.AVG,
                timezone=Transform.Timezone.UTC
            )

            timeserie_transformed = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        uuid_id=mesh_object.id,
                                                        transformation=from_breakpoint_to_hourly)

            pandas_dataframe = timeserie_transformed.arrow_table.to_pandas()
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

    Start point:                801896b0-d448-4299-874a-3ecf8ab0e2d4 # Model/MeshTEK/Mesh
    Search expression:          *[.Type=Reservoir].ReservoirVolume_operative
    Transformation expression:  ## = @SUM(@T('*[.Type=Reservoir].ReservoirVolume_operative'))
    Time interval:              5.9.2021 - 15.9.2021

    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 8"
            model = "MeshTEK"
            start_object_guid = '801896b0-d448-4299-874a-3ecf8ab0e2d4'
            search_query = '*[.Type=Reservoir].ReservoirVolume_operative'
            start = datetime(2021, 9, 5)
            end = datetime(2021, 9, 15)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Summarize timeseries
            start_object = mesh_pb2.ObjectId(
                guid=to_proto_guid(uuid.UUID('801896b0-d448-4299-874a-3ecf8ab0e2d4'))
            )
            search_query = "'*[.Type=Reservoir].ReservoirVolume_operative'"
            expression = f"## = @SUM(@T({search_query}))\n"
            request = mesh_pb2.CalculationRequest(
                session_id=to_proto_guid(session.session_id),
                expression=expression,
                interval=to_protobuf_utcinterval(start, end),
                relative_to=start_object
            )
            response = session.mesh_service.RunCalculation(request)
            summarized_timeseries = read_proto_reply(response.timeseries_results)

            path_and_pandas_dataframe = []
            pandas_dataframe = summarized_timeseries[0].arrow_table.to_pandas()
            path_and_pandas_dataframe.append(("Sum", pandas_dataframe))

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: summarize {expression}")
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_8')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")


def use_case_9():
    """
    Scenario:
    We want to get the historical data for a timeseries on a specific date.

    Mesh object:                7fd23545-a8b6-4614-90fd-0e3b65f61403
    Time interval:              15.11.2021 - 15.02.2022
    Historical date:            17.09.2021
    Transformation expression:  ## = @GetTsAsOfTime(@t('.ReservoirVolume'),'20210917000000000')

    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            use_case_name = "Use case 9"
            model = "MeshTEK"
            object_guid = '7fd23545-a8b6-4614-90fd-0e3b65f61403'
            start = datetime(2021, 11, 15)
            end = datetime(2022, 2, 15)
            transform_expression = "## = @GetTsAsOfTime(@t('.ReservoirVolume'),'20210917000000000')"
            historical_date = datetime(2021, 9, 17)
            print(f"{use_case_name}:")
            print("--------------------------------------------------------------")

            # Retrieve information about the object
            mesh_object = session.get_timeseries_attribute(model=model,
                                                           uuid_id=uuid.UUID(object_guid))

            # Retrieve timeseries connected to the mesh objects found
            path_and_pandas_dataframe = []
            timeseries = session.read_timeseries_points(start_time=start,
                                                        end_time=end,
                                                        uuid_id=mesh_object.id)
            print(f"{object_guid}: \n"
                  f"-----\n"
                  f"" + get_mesh_object_information(mesh_object) + f"")
            for timeserie in timeseries:
                pandas_dataframe = timeserie.arrow_table.to_pandas()
                path_and_pandas_dataframe.append((mesh_object.path, pandas_dataframe))

            # TODO: get historical version

            # Post process data
            plot_timeseries(path_and_pandas_dataframe,
                            f"{use_case_name}: transforming resolution",
                            style='step'
                            )
            save_timeseries_to_csv(path_and_pandas_dataframe, 'use_case_9')

        except grpc.RpcError as e:
            print(f"{use_case_name} resulted in an error: {e}")

if __name__ == "__main__":

    if len(sys.argv) > 1:
        RUN_USE_CASE = sys.argv[1]

    ALL_USE_CASE_FUNCTIONS = {key.strip('use_case_'): value for key, value in locals().items() if 'use_case_' in key}

    if RUN_USE_CASE.isnumeric() and (RUN_USE_CASE in ALL_USE_CASE_FUNCTIONS.keys()):
        ALL_USE_CASE_FUNCTIONS[RUN_USE_CASE]()
    elif RUN_USE_CASE == 'all':
        for _, use_case in ALL_USE_CASE_FUNCTIONS:
            use_case()
    elif RUN_USE_CASE == 'flow_drop_2':
        flow_drop_2_use_cases = [1, 2, 3, 4, 5]
        for number, use_case in ALL_USE_CASE_FUNCTIONS.items():
            if int(number) in flow_drop_2_use_cases:
                use_case()
    elif RUN_USE_CASE == 'flow_drop_3':
        flow_drop_2_use_cases = [6, 7, 8, 9, 10, 11]
        for number, use_case in ALL_USE_CASE_FUNCTIONS.items():
            if int(number) in flow_drop_2_use_cases:
                use_case()
    else:
        default_use_case = ALL_USE_CASE_FUNCTIONS['1']
        print(f"Invalid use case selected: {RUN_USE_CASE}, selecting default use case {default_use_case.__name__}")
        default_use_case()


