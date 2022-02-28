from datetime import datetime
import math
from typing import List
import uuid

import grpc
import pytest

from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh import MeshObjectId, Timeseries, from_proto_guid, to_proto_curve_type, to_proto_guid
from volue.mesh.calc import transform as Transform
from volue.mesh.calc.common import Timezone
from volue.mesh.calc.history import HistoryFunctionsAsync as History
from volue.mesh.calc.statistical import StatisticalFunctionsAsync as Misc
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.proto.core.v1alpha import core_pb2
from volue.mesh.proto.type import resources_pb2
from volue.mesh.tests.test_utilities.utilities import get_timeseries_2, get_timeseries_1, \
    get_timeseries_attribute_1, get_timeseries_attribute_2


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_timeseries_points_async():
    """Check that timeseries points can be read"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)
    async with connection.create_session() as session:
        timeseries, start_time, end_time, _, full_name = get_timeseries_2()
        try:
            test_case_1 = {"start_time": start_time, "end_time": end_time, "timskey": timeseries.timeseries_key}
            test_case_2 = {"start_time": start_time, "end_time": end_time, "uuid_id": timeseries.id}
            test_case_3 = {"start_time": start_time, "end_time": end_time, "full_name": full_name}
            test_cases = [test_case_1, test_case_2, test_case_3]
            for test_case in test_cases:
                reply_timeseries = await session.read_timeseries_points(**test_case)
                assert type(reply_timeseries) is Timeseries
                assert reply_timeseries.number_of_points == 9
                # check timestamps
                utc_date = reply_timeseries.arrow_table[0]
                for count, item in enumerate(utc_date):
                    assert item.as_py() == datetime(2016, 1, 1, count+1, 0)
                # check flags
                flags = reply_timeseries.arrow_table[1]
                assert flags[3].as_py() == Timeseries.PointFlags.NOT_OK.value | Timeseries.PointFlags.MISSING.value
                for number in [0, 1, 2, 4, 5, 6, 7, 8]:
                    assert flags[number].as_py() == Timeseries.PointFlags.OK.value
                # check values
                values = reply_timeseries.arrow_table[2]
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
                                                              end_time=datetime(2016, 1, 1, 3, 0, 0),
                                                              uuid_id=ts_entry.id)
            assert written_ts.number_of_points == 3
            utc_time = written_ts.arrow_table[0]
            assert utc_time[0].as_py() == datetime(2016, 1, 1, 1, 0, 0)
            assert utc_time[1].as_py() == datetime(2016, 1, 1, 2, 0, 0)
            assert utc_time[2].as_py() == datetime(2016, 1, 1, 3, 0, 0)
            flags = written_ts.arrow_table[1]
            assert flags[0].as_py() == 0
            assert flags[1].as_py() == 0
            assert flags[2].as_py() == 0
            values = written_ts.arrow_table[2]
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
                assert timeseries_info.curve_type.type == timeseries.curve.value
                assert timeseries_info.resolution.type == timeseries.resolution.value
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
                timeseries_info = await session.get_timeseries_resource_info(**test_id)

                if "new_path" in test_case:
                    assert timeseries_info.path == new_path
                if "new_curve_type" in test_case:
                    assert timeseries_info.curve_type.type == resources_pb2.Curve.UNKNOWN
                if "new_unit_of_measurement" in test_case:
                    assert timeseries_info.unit_of_measurement == new_unit_of_measurement


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
                assert reply_timeseries.curve_type.type == expected_timeseries.curve.value
                assert reply_timeseries.resolution.type == expected_timeseries.resolution.value
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
    new_timeseries_entry_id = core_pb2.TimeseriesEntryId(guid=to_proto_guid(new_timeseries_entry.id))

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
                # The results should be the one we are looking for
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
                assert reply_timeseries.curve_type == to_proto_curve_type(expected_timeseries.curve)
                assert reply_timeseries.resolution.type == expected_timeseries.resolution.value
                assert reply_timeseries.unit_of_measurement == expected_timeseries.unit_of_measurement
        except grpc.RpcError as e:
            pytest.fail(f"Could not update timeseries attribute: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_write_timeseries_points_using_timskey_async():
    """Check that timeseries can be written to the server using timskey."""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)
    ts_entry, start_time, end_time, modified_table, _ = get_timeseries_2()
    timeseries = Timeseries(table=modified_table, start_time=start_time, end_time=end_time,
                            timskey=ts_entry.timeseries_key)

    async with connection.create_session() as session:
        try:
            await session.write_timeseries_points(
                timeserie=timeseries
            )
        except grpc.RpcError:
            pytest.fail("Could not write timeseries points")


@pytest.mark.asyncio
@pytest.mark.database
async def test_commit():
    """Check that commit keeps changes between sessions"""
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    attribute, full_name = get_timeseries_attribute_1()
    new_local_expression = "something"
    old_local_expression = attribute.local_expression

    async with connection.create_session() as session1:
        try:
            # check base line
            attribute1 = await session1.get_timeseries_attribute(model=attribute.model, path=full_name)
            old_local_expression = attribute1.local_expression
            assert attribute1.local_expression != new_local_expression

            # change something
            await session1.update_timeseries_attribute(path=full_name, new_local_expression=new_local_expression)

            # commit
            await session1.commit()

            # check that the change is in the session
            attribute2 = await session1.get_timeseries_attribute(model=attribute.model, path=full_name)
            assert attribute2.local_expression == new_local_expression

            # rollback
            await session1.rollback()

            # check that changes are still there
            attribute3 = await session1.get_timeseries_attribute(model=attribute.model, path=full_name)
            assert attribute3.local_expression == new_local_expression

        except grpc.RpcError as e:
            pytest.fail("Could not commit changes.")

    async with connection.create_session() as session2:
        try:
            # check that the change is still there
            attribute4 = await session2.get_timeseries_attribute(model=attribute.model, path=full_name)
            assert attribute4.local_expression == new_local_expression

            # change it back to what is was originally
            await session2.update_timeseries_attribute(path=full_name, new_local_expression=old_local_expression)

            # commit
            await session2.commit()

            # check that status has been restored (important to keep db clean)
            attribute5 = await session2.get_timeseries_attribute(model=attribute.model, path=full_name)
            assert attribute5.local_expression == old_local_expression

        except grpc.RpcError as e:
            pytest.fail("Could not restore commited changes.")


@pytest.mark.asyncio
@pytest.mark.database
async def test_rollback():
    """Check that rollback discards changes made in the current session."""
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        try:
            _, full_name = get_timeseries_1()
            new_path = "/new_path"

            # check base line
            timeseries_info0 = await session.get_timeseries_resource_info(path=full_name)
            assert timeseries_info0.path != new_path

            # change something
            await session.update_timeseries_resource_info(path=full_name, new_path=new_path)

            # check that the change is in the session
            timeseries_info1 = await session.get_timeseries_resource_info(path=full_name)
            assert timeseries_info1.path == new_path

            # rollback
            await session.rollback()

            # check that changes have been discarded
            timeseries_info2 = await session.get_timeseries_resource_info(path=full_name)
            assert timeseries_info2.path != new_path

        except grpc.RpcError as e:
            pytest.fail("Could not rollback changes.")


@pytest.mark.asyncio
@pytest.mark.database
@pytest.mark.parametrize('resolution, expected_number_of_points',
    [(Timeseries.Resolution.MIN15, 33),
     (Timeseries.Resolution.HOUR, 9),
     (Timeseries.Resolution.DAY, 1),
     (Timeseries.Resolution.WEEK, 1),
     (Timeseries.Resolution.MONTH, 2),
     (Timeseries.Resolution.YEAR, 2)])
@pytest.mark.parametrize('method',
    [Transform.Method.SUM,
     Transform.Method.SUMI,
     Transform.Method.AVG,
     Transform.Method.AVGI,
     Transform.Method.FIRST,
     Transform.Method.LAST,
     Transform.Method.MIN,
     Transform.Method.MAX])
@pytest.mark.parametrize('timezone',
    [None,
     Timezone.LOCAL,
     Timezone.STANDARD,
    Timezone.UTC])
async def test_read_transformed_timeseries_points(
    resolution, method, timezone,
    expected_number_of_points: int):
    """Check that transformed timeseries points can be read"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        transform_parameters = Transform.Parameters(resolution, method, timezone)
        _, full_name = get_timeseries_attribute_2()

        try:
            reply_timeseries = await session.read_timeseries_points(
                start_time, end_time, full_name=full_name, transformation=transform_parameters)

            assert reply_timeseries.is_calculation_expression_result

            if resolution in [Timeseries.Resolution.HOUR,
                              Timeseries.Resolution.DAY,
                              Timeseries.Resolution.WEEK,
                              Timeseries.Resolution.MONTH,
                              Timeseries.Resolution.YEAR]:
                # logic for those resolutions is complex and depends on other parameters
                # make sure the result has at least 1 point and no error is thrown
                assert reply_timeseries.number_of_points >= 1
                return

            assert reply_timeseries.number_of_points == expected_number_of_points

            expected_date = start_time
            delta = 1 if expected_number_of_points == 1 else (end_time - start_time) / (expected_number_of_points - 1)
            index = 0
            d = reply_timeseries.arrow_table.to_pydict()

            for utc_time, flags, value in zip(d['utc_time'], d['flags'], d['value']):
                # check timestamps
                assert utc_time == expected_date

                # check flags and values
                # hours, flags
                # <1, 3> - OK
                # (3, 4) - MISSING
                # <4, 5) - NOT_OK | MISSING
                # <5, 10) - OK
                if expected_date > datetime(2016, 1, 1, 3) and expected_date < datetime(2016, 1, 1, 4):
                    assert flags == Timeseries.PointFlags.MISSING.value
                    assert math.isnan(value)
                elif expected_date >= datetime(2016, 1, 1, 4) and expected_date < datetime(2016, 1, 1, 5):
                    expected_flags = Timeseries.PointFlags.NOT_OK.value | Timeseries.PointFlags.MISSING.value
                    assert flags == expected_flags
                    assert math.isnan(value)
                else:
                    assert flags == Timeseries.PointFlags.OK.value
                    # check values for one some combinations (method AVG and resolution MIN15)
                    if method is Transform.Method.AVG and resolution is Timeseries.Resolution.MIN15:
                        # the original timeseries data is in hourly resolution,
                        # starts with 1 and the value is incremented with each hour up to 9
                        # here we are using 15 min resolution, so the delta between each 15 min point is 0.25
                        assert value == 1 + index * 0.25

                expected_date += delta
                index += 1

        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_transformed_timeseries_points_with_uuid():
    """
    Check that transformed timeseries read by full_name or UUID
    (both pointing to the same object) return the same data.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        # set interval where there are no NaNs to comfortably use `assert ==``
        start_time = datetime(2016, 1, 1, 5, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        transform_parameters = Transform.Parameters(
            Timeseries.Resolution.MIN15, Transform.Method.AVG)
        _, full_name = get_timeseries_attribute_2()

        # first read timeseries UUID (it is set dynamically)
        timeseries = await session.read_timeseries_points(
            start_time, end_time, full_name=full_name)
        ts_uuid = timeseries.uuid

        reply_timeseries_full_name = await session.read_timeseries_points(
            start_time, end_time, full_name=full_name, transformation=transform_parameters)

        reply_timeseries_uuid = await session.read_timeseries_points(
            start_time, end_time, uuid_id=ts_uuid, transformation=transform_parameters)

        assert reply_timeseries_full_name.is_calculation_expression_result == reply_timeseries_uuid.is_calculation_expression_result
        assert len(reply_timeseries_full_name.arrow_table) == len(reply_timeseries_uuid.arrow_table)

        for column_index in range(0, 3):
            assert reply_timeseries_full_name.arrow_table[column_index] == reply_timeseries_uuid.arrow_table[column_index]


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_timeseries_points_without_specifying_timeseries_should_throw():
    """
    Check that expected exception is thrown when trying to
    read timeseries without specifying timeseries (by full_name, timskey or uuid_id).
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)

        with pytest.raises(TypeError, match=".*need to specify either timskey, uuid_id or full_name.*"):
            await session.read_timeseries_points(start_time, end_time)


@pytest.mark.asyncio
@pytest.mark.database
async def test_history_get_all_forecasts():
    """
    Check that running history `get_all_forecasts` does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        try:
            reply_timeseries = await session.history_functions(
                MeshObjectId(full_name=full_name), start_time, end_time).get_all_forecasts()
            assert isinstance(reply_timeseries, List) and len(reply_timeseries) is 0
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.asyncio
@pytest.mark.database
@pytest.mark.parametrize('available_at_timepoint',
    [None,
     datetime(2016, 1, 5, 17, 48, 11, 123456)])
@pytest.mark.parametrize('timezone',
    [None,
     Timezone.LOCAL,
     Timezone.STANDARD,
     Timezone.UTC])
async def test_history_get_forecasts(available_at_timepoint, timezone):
    """
    Check that running history `get_forecasts` does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        t0_min = datetime(2016, 1, 2)
        t0_max = datetime(2016, 1, 8)
        _, full_name = get_timeseries_attribute_2()

        try:
            reply_timeseries = await session.history_functions(
                MeshObjectId(full_name=full_name), start_time, end_time).get_forecast(
                    t0_min, t0_max, available_at_timepoint, timezone)
            assert reply_timeseries.is_calculation_expression_result
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.asyncio
@pytest.mark.database
@pytest.mark.parametrize('timezone',
    [None,
     Timezone.LOCAL,
     Timezone.STANDARD,
     Timezone.UTC])
async def test_history_get_ts_as_of_time(timezone):
    """
    Check that running history `get_ts_as_of_time` does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        available_at_timepoint = datetime(2016, 1, 5, 17, 48, 11, 123456)
        _, full_name = get_timeseries_attribute_2()

        try:
            reply_timeseries = await session.history_functions(
                MeshObjectId(full_name=full_name), start_time, end_time).get_ts_as_of_time(
                    available_at_timepoint, timezone)
            assert reply_timeseries.is_calculation_expression_result
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.asyncio
@pytest.mark.database
@pytest.mark.parametrize('max_number_of_versions_to_get',
    [1, 2, 5])
async def test_history_get_ts_historical_versions(max_number_of_versions_to_get):
    """
    Check that running history `get_ts_historical_versions` does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        try:
            reply_timeseries = await session.history_functions(
                MeshObjectId(full_name=full_name), start_time, end_time).get_ts_historical_versions(
                    max_number_of_versions_to_get)
            assert isinstance(reply_timeseries, List) and len(reply_timeseries) is 0
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_statistical_sum():
    """
    Check that running misc `sum` does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.SECURE_CONNECTION)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        try:
            reply_timeseries = await session.statistical_functions(
                MeshObjectId(full_name=full_name), start_time, end_time).sum()
            assert reply_timeseries.is_calculation_expression_result
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


if __name__ == '__main__':
    pytest.main()
