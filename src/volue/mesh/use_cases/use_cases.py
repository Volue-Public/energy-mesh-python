from datetime import datetime, timezone
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import grpc
import sys
from volue.mesh import Connection, from_proto_guid

HOST = "localhost"
PORT = 50051
SHOW_PLOT = True
SAVE_TO_CVS = True


def plot_timeseries(timeseries_pandas, title=''):
    print(timeseries_pandas)
    timeseries_pandas.plot(kind='line', x='utc_time', y='value', color='red', figsize=(14, 7), title=title)
    plt.show()


def save_timeseries_to_csv(timeseries_pandas, timeseries_path, file_prefix):
    filename = timeseries_path.split('/')[-1]
    timeseries_pandas.to_csv(file_prefix + '_' + filename + '.csv', index=False)


def use_case_1():
    """
    Søk1:
    *[.Type=HydroPlant].Production_operative
    Startpunkt = 801896b0-d448-4299-874a-3ecf8ab0e2d4 # Model/MeshTEK/Mesh
    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            model = "MeshTEK"
            start_object_guid = uuid.UUID("801896b0-d448-4299-874a-3ecf8ab0e2d4")  # Model/MeshTEK/Mesh
            start = datetime(2021, 9, 1, tzinfo=timezone.utc)
            end = datetime(2021, 10, 1, tzinfo=timezone.utc)

            # Søk1
            first = session.search_for_timeseries_attribute(model=model, start_object_guid=start_object_guid,
                                                            query="*[.Type=HydroPlant].Production_operative")
            print(f"Søk1: Search resulted in {len(first)} items, ids are:")
            for item in first:
                print(f"id: {from_proto_guid(item.id)}")
                print(f"path: {item.path}")
                ts = session.read_timeseries_points(start_time=start, end_time=end, uuid_id=item.id)
                print("")
                ts_pd = ts[0].arrow_table.to_pandas()
                plot_timeseries(ts_pd, item.path)
                save_timeseries_to_csv(ts_pd, item.path, 'use_case_1')

        except grpc.RpcError as e:
            print(f"{e}")


def use_case_2():
    """
    Søk2:
    *[.Type=Area&&.Name=Norge]/To_HydroProduction/To_WaterCourses/To_Reservoirs.ReservoirVolume_operative
    Startpunkt = 801896b0-d448-4299-874a-3ecf8ab0e2d4 # Model/MeshTEK/Mesh
    """

    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            model = "MeshTEK"
            start_object_guid = uuid.UUID("801896b0-d448-4299-874a-3ecf8ab0e2d4")  # Model/MeshTEK/Mesh
            start = datetime(2021, 9, 1, tzinfo=timezone.utc)
            end = datetime(2021, 10, 1, tzinfo=timezone.utc)

            # Søk2
            second = session.search_for_timeseries_attribute(model=model, start_object_guid=start_object_guid,
                                                             query="*[.Type=Area&&.Name=Norge]/To_HydroProduction/To_WaterCourses/To_Reservoirs.ReservoirVolume_operative")
            print(f"\nSøk2: Search resulted in {len(second)} items, ids are:")
            for item in second:
                print(f"path: {item.path}")
                ts = session.read_timeseries_points(start_time=start, end_time=end, uuid_id=from_proto_guid(item.id))
                ts_pd = ts[0].arrow_table.to_pandas()
                plot_timeseries(ts_pd, item.path)
                save_timeseries_to_csv(ts_pd, item.path, 'use_case_2')

        except grpc.RpcError as e:
            print(f"{e}")


def use_case_3():
    """
    Søk3:
    TimsKey=530,536,537,543,556
    Startpunkt = 801896b0-d448-4299-874a-3ecf8ab0e2d4 # Model/MeshTEK/Mesh
    """
    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            start = datetime(2021, 9, 1, tzinfo=timezone.utc)
            end = datetime(2021, 10, 1, tzinfo=timezone.utc)

            # Søk3:
            print("\nSøk3:")
            timskeys = [530, 536, 537, 543, 556]
            for timskey in timskeys:
                entry = session.get_timeseries_resource_info(timskey=timskey)
                print(f"Guid for timeseries entry with timskey: {timskey} is {entry.id}")
                ts = session.read_timeseries_points(start_time=start, end_time=end, timskey=timskey)
                ts_pd = ts[0].arrow_table.to_pandas()
                plot_timeseries(ts_pd, str(timskey))
                save_timeseries_to_csv(ts_pd, str(timskey), 'use_case_3')


        except grpc.RpcError as e:
            print(f"{e}")


def use_case_4():
    """
    Søk4:
    GUID=
    3fd4ed37-2114-4d95-af90-02b96bd993ed,
    80ea68d4-2859-49a3-ae41-abe6a8b50b30,
    d314151b-2014-4326-95e5-e65b3f72c897,
    867f8b45-5a5c-4ddb-97f4-4ea823ad7b3f,
    840f891c-8850-4af8-8297-774585eace1e
    Startpunkt = 801896b0-d448-4299-874a-3ecf8ab0e2d4 # Model/MeshTEK/Mesh
    """

    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    with connection.create_session() as session:
        try:
            model = "MeshTEK"
            start = datetime(2021, 9, 1, tzinfo=timezone.utc)
            end = datetime(2021, 10, 1, tzinfo=timezone.utc)

            # Søk4:
            print("\nSøk4:")
            guids = [
                "3fd4ed37-2114-4d95-af90-02b96bd993ed",
                "80ea68d4-2859-49a3-ae41-abe6a8b50b30",
                "d314151b-2014-4326-95e5-e65b3f72c897",
                "867f8b45-5a5c-4ddb-97f4-4ea823ad7b3f",
                "840f891c-8850-4af8-8297-774585eace1e"
            ]
            for guid in guids:
                entry = session.get_timeseries_attribute(model=model, uuid_id=uuid.UUID(guid))
                #print(f"Timeseries attribute GUID for timeseries entry with GUID: {guid} is {from_proto_guid(entry.id)}")
                ts = session.read_timeseries_points(start_time=start, end_time=end, uuid_id=from_proto_guid(entry.id))
                ts_pd = ts[0].arrow_table.to_pandas()
                plot_timeseries(ts_pd, entry.path)
                save_timeseries_to_csv(ts_pd, entry.path, 'use_case_4')

        except grpc.RpcError as e:
            print(f"{e}")


def use_case_5():
    """
    Startpunkt: 6a55d0e7-6011-41db-8700-f2aba92e945b
    Model: MeshTEK
    Type:Cases
    Name:Cases

    GUID 1: ff1db73f-8c8a-42f8-a44a-4bbb420874c1
    GUID 2: 801896b0-d448-4299-874a-3ecf8ab0e2d4
    """

    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    start = datetime(2021, 10, 1)
    end = datetime(2021, 11, 1)

    with connection.create_session() as session:
        try:
            # Not working:
            model = "MeshTEK"
            print("\nSøk5:")
            guids = [
                "ff1db73f-8c8a-42f8-a44a-4bbb420874c1",  # (TimeseriesCalculation) Model/MeshTEK/Cases.has_OptimisationCases/Driva_Short_Opt.has_cAreas/Norge.has_cHydroProduction/Vannkraft.has_cWaterCourses/Driva.has_cProdriskAreas/Driva.has_cProdriskModules/Gjevilvatnet.has_cProdriskScenarios/1960.ReservoirVolume/ReservoirVolume
                # "801896b0-d448-4299-874a-3ecf8ab0e2d4"  # (Component) Model/MeshTEK/Mesh - this won't work
                ]
            for guid in guids:
                entry = session.get_timeseries_attribute(model=model, uuid_id=uuid.UUID(guid))
                # print(f"Timeseries attribute GUID for timeseries entry with GUID: {guid} is {from_proto_guid(entry.id)}")
                ts = session.read_timeseries_points(start_time=start, end_time=end, uuid_id=from_proto_guid(entry.id))
                ts_pd = ts[0].arrow_table.to_pandas()
                plot_timeseries(ts_pd, entry.path)
                save_timeseries_to_csv(ts_pd, entry.path, 'use_case_5')

        except grpc.RpcError as e:
            print(f"{e}")

def use_case_6():

    """
    Startpunkt: 6a55d0e7-6011-41db-8700-f2aba92e945b
    Model: MeshTEK
    Type:Cases
    Name:Cases

    TimsKey: 265831
    (denne tidsserien er ikke knyttet inn i Mesh finnes kun i db,
    men slik jeg har forstått det skal det være mulig å hente ut dette.
    Usikker på hva som skal være startpunkt for dette)
    """

    connection = Connection(host=HOST, port=PORT, secure_connection=False)
    start = datetime(2021, 9, 1)
    end = datetime(2021, 10, 1)

    with connection.create_session() as session:
        try:
            # Not working:
            print("\nSøk6:")
            timskeys = [265831]  # this timeskey does not have values
            for timskey in timskeys:
                #entry = session.get_timeseries_resource_info(timskey=timskey)
                #print(f"Guid for timeseries entry with timskey: {timskey} is {from_proto_guid(entry.id)}")
                ts = session.read_timeseries_points(start_time=start, end_time=end, timskey=timskey)
                ts_pd = ts[0].arrow_table.to_pandas()
                plot_timeseries(ts_pd, str(timskey))
                save_timeseries_to_csv(ts_pd, str(timskey), 'use_case_6')
        except grpc.RpcError as e:
            print(f"{e}")


def use_case_7():
    """
    Ny use case for drop 2 - skriving til tidsserie. Samme startpunkt i modellen som tidligere (use case 1)

    Tidsserien det skal skrives til: bruk GUID'en

    !Model: MeshTEK Type: Unit Name:Morre G1 Attribute: Production_raw
    !@MeshRead('MeshTEK', '*[.Type=Unit&&.Name=Morre G1].Production_raw')
    ## = @MeshRead('3fd4ed37-2114-4d95-af90-02b96bd993ed')

    Verdier som skal skrives:
    28/09/21 01	11.50
    Hour 02	11.91
    Hour 03	11.88
    Hour 04	11.86
    Hour 05	11.66
    Hour 06	11.73
    Hour 07	11.80
    Hour 08	11.88
    Hour 09	11.97
    Hour 10	9.87
    Hour 11	9.47
    Hour 12	9.05
    Hour 13	9.20
    Hour 14	9.00
    Hour 15	8.91
    Hour 16	10.62
    Hour 17	12.00
    Hour 18	12.07
    Hour 19	12.00
    Hour 20	11.78
    Hour 21	5.08
    Hour 22	0.00
    Hour 23	0.00
    Hour 24	0.00
    """
    pass


if __name__ == "__main__":
    # Alle use cases kan vises for perioden 01.9.2021 - 01.10.2021

    if len(sys.argv) <= 1:
        usecase = '1'
    else:
        usecase = sys.argv[1]

    if usecase == '1':
        use_case_1()
    elif usecase == '2':
        use_case_2()
    elif usecase == '3':
        use_case_3()
    elif usecase == '4':
        use_case_4()
    elif usecase == '5':
        use_case_5()
    elif usecase == '6':
        use_case_6()
    elif usecase == '7':
        use_case_7()
    else:
        use_case_1()
