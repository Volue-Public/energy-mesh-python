import uuid, math
from datetime import date, datetime
from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh import Timeseries, from_proto_guid, to_proto_curve_type, to_proto_guid
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.proto import mesh_pb2
from volue.mesh.tests.test_utilities.utilities import get_timeseries_2, get_timeseries_1, \
    get_timeseries_attribute_1, get_timeseries_attribute_2
import grpc
import pytest


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_timeseries_points_async():
    """Check that timeseries points can be read"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)
    async with connection.create_session() as session:
        timeseries, start_time, end_time, modified_table, full_name = get_timeseries_2()
        try:
            test_case_1 = {"start_time": start_time, "end_time": end_time, "timskey": timeseries.timeseries_key}
            test_case_2 = {"start_time": start_time, "end_time": end_time, "uuid_id": timeseries.id}
            test_case_3 = {"start_time": start_time, "end_time": end_time, "full_name": full_name}
            test_cases = [test_case_1, test_case_2, test_case_3]
            for test_case in test_cases:
                reply_timeseries = await session.read_timeseries_points(**test_case)
                assert len(reply_timeseries) == 1
                ts = reply_timeseries[0]
                assert ts.number_of_points == 9
                # check timestamps
                utc_date = ts.arrow_table[0]
                for count, item in enumerate(utc_date):
                    assert item.as_py() == datetime(2016, 1, 1, count+1, 0)
                # check flags
                flags = ts.arrow_table[1]
                assert flags[3].as_py() == 1140850688
                for number in [0, 1, 2, 4, 5, 6, 7, 8]:
                    assert flags[number].as_py() == 0
                # check values
                values = ts.arrow_table[2]
                values[3].as_py()
                assert math.isnan(values[3].as_py())
                for number in [0, 1, 2, 4, 5, 6, 7, 8]:
                    assert values[number].as_py() == (number + 1) * 100
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_write_timeseries_points_async():
    """Check that timeseries points can be written"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)
    async with connection.create_session() as session:
        ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_2()
        timeseries = Timeseries(table=modified_table, start_time=start_time, end_time=end_time, full_name=full_name)
        try:
            await session.write_timeseries_points(timeseries)
            written_ts = await session.read_timeseries_points(start_time=datetime(2016, 1, 1, 1, 0, 0),
                                                              end_time=datetime(2016, 1, 1, 4, 0, 0),
                                                              uuid_id=ts_entry.id)
            assert written_ts[0].number_of_points == 3
            utc_time = written_ts[0].arrow_table[0]
            assert utc_time[0].as_py() == datetime(2016, 1, 1, 2, 0, 0)
            assert utc_time[1].as_py() == datetime(2016, 1, 1, 3, 0, 0)
            assert utc_time[2].as_py() == datetime(2016, 1, 1, 4, 0, 0)
            flags = written_ts[0].arrow_table[1]
            assert flags[0].as_py() == 0
            assert flags[1].as_py() == 0
            assert flags[2].as_py() == 0
            values = lags = written_ts[0].arrow_table[2]
            assert values[0].as_py() == 0
            assert values[1].as_py() == 10
            assert values[2].as_py() == 1000

        except grpc.RpcError as e:
            pytest.fail(f"Could not write timeseries points {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_timeseries_async():
    """Check that timeseries entry data can be retrieved"""

    timeseries, full_name = get_timeseries_1()
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        try:
            test_case_1 = {"path": full_name}
            test_case_2 = {"uuid_id": timeseries.id}
            test_case_3 = {"timskey": timeseries.timeseries_key}
            test_cases = [test_case_1, test_case_2, test_case_3]
            for test_case in test_cases:
                timeseries_info = await session.get_timeseries_resource_info(**test_case)
                assert from_proto_guid(timeseries_info.id) == timeseries.id
                assert timeseries_info.timeseries_key == timeseries.timeseries_key
                assert timeseries_info.path == timeseries.path
                assert timeseries_info.temporary == timeseries.temporary
                assert timeseries_info.curveType.type == timeseries.curve.value
                assert timeseries_info.delta_t.type == timeseries.resolution.value
                assert timeseries_info.unit_of_measurement == timeseries.unit_of_measurement

        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries entry: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_timeseries_entry_async():
    """Check that timeseries entry data can be updated"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    new_path = "/test"
    new_curve_type = "curvy"  # -> UNKNOWN
    new_unit_of_measurement = "mega watt"

    async with connection.create_session() as session:
        try:
            ts_entry, full_name = get_timeseries_1()

            test_ids = [{"path": full_name}, {"uuid_id": ts_entry.id}, {"timskey": ts_entry.timeseries_key}]
            test_new_path = {"new_path": new_path}
            test_new_curve_type = {"new_curve_type": new_curve_type}
            test_new_unit_of_measurement = {"new_unit_of_measurement": new_unit_of_measurement}
            test_cases = []
            for test_id in test_ids:
                test_cases.extend(
                    [{**test_id, **test_new_path},
                     {**test_id, **test_new_curve_type},
                     {**test_id, **test_new_unit_of_measurement},
                     {**test_id, **test_new_path, **test_new_curve_type},
                     {**test_id, **test_new_path, **test_new_unit_of_measurement},
                     {**test_id, **test_new_curve_type, **test_new_unit_of_measurement},
                     {**test_id, **test_new_path, **test_new_curve_type, **test_new_unit_of_measurement}]
                )
            for test_case in test_cases:
                await session.update_timeseries_resource_info(**test_case)
                # TODO: assert something

        except grpc.RpcError as e:
            pytest.fail(f"Could not update timeseries entry: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_timeseries_attribute_async():
    """Check that timeseries attribute data can be retrieved"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        try:
            # Calculation
            # Testing attribute without an entry connected to it
            attribute_without_entry, full_path = get_timeseries_attribute_1()
            test_case_1 = {"model": attribute_without_entry.model,
                           "path": attribute_without_entry.silo + attribute_without_entry.path}
            test_case_2 = {"model": attribute_without_entry.model,
                           "uuid_id": None}  # since it is generated we find it through the first test case
            test_cases = [test_case_1, test_case_2]
            for test_case in test_cases:
                reply = await session.get_timeseries_attribute(**test_case)
                assert reply is not None
                assert from_proto_guid(reply.id) is not None
                if "path" in test_case:
                    test_case_2["uuid_id"] = reply.id
                    attribute_without_entry.id = reply.id
                assert reply.path == full_path
                assert not reply.HasField('entry')
                assert reply.local_expression == attribute_without_entry.local_expression
                assert reply.template_expression == attribute_without_entry.template_expression

            # Reference
            # Testing attribute with an entry connected to it
            attribute_with_entry, full_name = get_timeseries_attribute_2()
            test_case_1 = {"model": attribute_with_entry.model,
                           "path": full_name}
            test_case_2 = {"model": attribute_with_entry.model,
                           "uuid_id": None}  # since it is generated we find it through the first test case
            test_cases = [test_case_1, test_case_2]
            for test_case in test_cases:
                reply = await session.get_timeseries_attribute(**test_case)
                assert reply is not None
                assert from_proto_guid(reply.id) is not None
                if "path" in test_case:
                    test_case_2["uuid_id"] = reply.id
                    attribute_with_entry.id = reply.id
                assert reply.path == full_name
                assert reply.local_expression == attribute_with_entry.local_expression
                assert reply.template_expression == attribute_with_entry.template_expression
                assert reply.HasField('entry')
                reply_timeseries = reply.entry
                expected_timeseries = attribute_with_entry.timeseries
                assert from_proto_guid(reply_timeseries.id) == expected_timeseries.id
                assert reply_timeseries.timeseries_key == expected_timeseries.timeseries_key
                assert reply_timeseries.path == expected_timeseries.path
                assert reply_timeseries.temporary == expected_timeseries.temporary
                assert reply_timeseries.curveType.type == expected_timeseries.curve.value
                assert reply_timeseries.delta_t.type == expected_timeseries.resolution.value
                assert reply_timeseries.unit_of_measurement == expected_timeseries.unit_of_measurement
        except grpc.RpcError as e:
            pytest.fail(f"Could not get timeseries attribute {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_timeseries_attribute_with_timeseriescalculation_async():
    """Check that timeseries attribute data with a calculation can be updated"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    attribute, full_name = get_timeseries_attribute_1()
    new_local_expression = "something"

    async with connection.create_session() as session:
        try:
            test_new_local_expression = {"new_local_expression": new_local_expression}
            test_case_1 = {"path": full_name, **test_new_local_expression}
            test_case_2 = {"uuid_id": None,
                           **test_new_local_expression}  # since it is generated we find it through the first test case
            test_cases = [test_case_1, test_case_2]

            for test_case in test_cases:

                await session.update_timeseries_attribute(**test_case)

                updated_attribute = await session.get_timeseries_attribute(model=attribute.model, path=full_name)
                assert updated_attribute.path == full_name
                assert updated_attribute.local_expression == new_local_expression

                if "path" in test_case:
                    test_case_2["uuid_id"] = updated_attribute.id

        except grpc.RpcError as e:
            pytest.fail(f"Could not update timeseries attribute: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_timeseries_attribute_with_timeseriesreference_async():
    """Check that timeseries attribute data can be updated"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    attribute, full_name = get_timeseries_attribute_2()
    new_timeseries, _ = get_timeseries_1()
    new_timeseries_entry = new_timeseries.entries[0]
    new_timeseries_entry_id = mesh_pb2.TimeseriesEntryId(guid=to_proto_guid(new_timeseries_entry.id))

    async with connection.create_session() as session:
        try:
            test_new_timeseries_entry_id = {"new_timeseries_entry_id": new_timeseries_entry_id}
            test_case_1 = {"path": full_name, **test_new_timeseries_entry_id}
            test_case_2 = {"uuid_id": None,
                           **test_new_timeseries_entry_id}  # since it is generated we find it through the first test case
            test_cases = [test_case_1, test_case_2]
            for test_case in test_cases:
                original_attribute = await session.get_timeseries_attribute(model=attribute.model, path=full_name)
                assert original_attribute.path == full_name
                assert from_proto_guid(original_attribute.entry.id) == attribute.timeseries.id

                if "path" in test_case:
                    test_case_2["uuid_id"] = original_attribute.id

                await session.update_timeseries_attribute(**test_case)

                updated_attribute = await session.get_timeseries_attribute(model=attribute.model, path=full_name)
                assert updated_attribute.path == full_name
                assert from_proto_guid(updated_attribute.entry.id) == new_timeseries.id

                await session.rollback()

        except grpc.RpcError as e:
            pytest.fail(f"Could not update timeseries attribute: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_search_timeseries_attribute_async():
    """Check that timeseries attribute data can be searched for"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    ts_attribute, full_name = get_timeseries_attribute_2()

    query = "{*}.TsRawAtt"
    start_object_path = "ThermalComponent"
    start_object_guid = uuid.UUID("0000000b-0001-0000-0000-000000000000")  # ThermalComponent

    async with connection.create_session() as session:
        try:
            test_case_1 = {"model": ts_attribute.model,
                           "query": query,
                           "start_object_path": start_object_path}
            test_case_2 = {"model": ts_attribute.model,
                           "query": query,
                           "start_object_guid": start_object_guid}
            test_cases = [test_case_1, test_case_2]
            for test_case in test_cases:
                reply = await session.search_for_timeseries_attribute(**test_case)
                assert reply is not None
                assert len(reply) == 3
                # One the results should be the one we are looking for
                assert any(attribute.path == full_name for attribute in reply)
                match = next((x for x in reply if x.path == full_name), None)
                assert match is not None
                assert from_proto_guid(match.id) is not None
                assert match.local_expression == ts_attribute.local_expression
                assert match.template_expression == ts_attribute.template_expression
                assert match.HasField('entry')
                reply_timeseries = match.entry
                expected_timeseries = ts_attribute.timeseries
                assert from_proto_guid(reply_timeseries.id) == expected_timeseries.id
                assert reply_timeseries.timeseries_key == expected_timeseries.timeseries_key
                assert reply_timeseries.path == expected_timeseries.path
                assert reply_timeseries.temporary == expected_timeseries.temporary
                assert reply_timeseries.curveType == to_proto_curve_type(expected_timeseries.curve)
                assert reply_timeseries.delta_t.type == expected_timeseries.resolution.value
                assert reply_timeseries.unit_of_measurement == expected_timeseries.unit_of_measurement
        except grpc.RpcError as e:
            pytest.fail(f"Could not update timeseries attribute: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_write_timeseries_points_using_timskey_async():
    """Check that timeseries can be written to the server using timskey."""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)
    ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_2()
    timeseries = Timeseries(table=modified_table, start_time=start_time, end_time=end_time,
                            timskey=ts_entry.timeseries_key)

    async with connection.create_session() as session:
        try:
            await session.write_timeseries_points(
                timeserie=timeseries
            )
        except grpc.RpcError:
            pytest.fail("Could not write timeseries points")


if __name__ == '__main__':
    pytest.main()
