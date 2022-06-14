"""
Tests for volue.mesh.aio
"""

from datetime import datetime, timedelta, timezone
import math
import sys
from typing import List, Tuple
import uuid

from dateutil import tz
import grpc
import pyarrow as pa
import pytest

from volue.mesh import MeshObjectId, Timeseries
from volue.mesh.aio import Connection as AsyncConnection
from volue.mesh._attribute import TimeseriesAttribute
from volue.mesh._common import AttributesFilter, _from_proto_guid, _to_proto_guid, _to_proto_curve_type
from volue.mesh.calc import transform
from volue.mesh.calc.common import Timezone
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.proto.core.v1alpha import core_pb2
from volue.mesh.proto.type import resources_pb2
from volue.mesh.tests.test_utilities.utilities import get_attribute_path_principal, get_timeseries_2, get_timeseries_1, \
    get_timeseries_attribute_1, get_timeseries_attribute_2, verify_timeseries_2


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_timeseries_points_async():
    """Check that timeseries points can be read using timeseries key, UUID and full name"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    async with connection.create_session() as session:
        timeseries, start_time, end_time, _, full_name = get_timeseries_2()
        try:
            test_case_1 = {"start_time": start_time, "end_time": end_time,
                           "mesh_object_id": MeshObjectId.with_timskey(timeseries.timeseries_key)}
            test_case_2 = {"start_time": start_time, "end_time": end_time,
                           "mesh_object_id": MeshObjectId.with_uuid_id(timeseries.id)}
            test_case_3 = {"start_time": start_time, "end_time": end_time,
                           "mesh_object_id": MeshObjectId.with_full_name(full_name)}

            test_cases = [test_case_1, test_case_2, test_case_3]
            for test_case in test_cases:
                reply_timeseries = await session.read_timeseries_points(**test_case)
                verify_timeseries_2(reply_timeseries)
        except grpc.RpcError as error:
            pytest.fail(f"Could not read timeseries points: {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_timeseries_points_with_different_datetime_timezones_async():
    """
    Check that timeseries points read accepts time zone aware and
    naive (treated as UTC) datetimes as input arguments.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    async with connection.create_session() as session:
        timeseries, start_time, end_time, _, _ = get_timeseries_2()

        # confirm start_time and end_time are time zone naive
        assert start_time.tzinfo is None and end_time.tzinfo is None

        # replace to UTC, because we treat time zone naive datetime as UTC
        start_time_utc = start_time.replace(tzinfo=tz.UTC)
        end_time_utc = end_time.replace(tzinfo=tz.UTC)

        local_tzinfo = tz.gettz('Europe/Warsaw')

        # now we can convert to different time zones (from time zone aware UTC datetime)
        start_time_local = start_time_utc.astimezone(local_tzinfo)
        end_time_local = end_time_utc.astimezone(local_tzinfo)

        try:
            test_case_naive = {"start_time": start_time, "end_time": end_time,
                               "mesh_object_id": MeshObjectId.with_timskey(timeseries.timeseries_key)}
            test_case_utc = {"start_time": start_time_utc, "end_time": end_time_utc,
                             "mesh_object_id": MeshObjectId.with_timskey(timeseries.timeseries_key)}
            test_case_local = {"start_time": start_time_local, "end_time": end_time_local,
                               "mesh_object_id": MeshObjectId.with_timskey(timeseries.timeseries_key)}
            test_case_mixed = {"start_time": start_time_local, "end_time": end_time_utc,
                               "mesh_object_id": MeshObjectId.with_timskey(timeseries.timeseries_key)}

            test_cases = [test_case_naive, test_case_utc, test_case_local, test_case_mixed]
            for test_case in test_cases:
                reply_timeseries = await session.read_timeseries_points(**test_case)
                verify_timeseries_2(reply_timeseries)
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_write_timeseries_points_async():
    """
    Check that timeseries points write accepts time series with time zone aware and
    naive (treated as UTC) datetimes as input interval (start_time and end_time arguments).
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    async with connection.create_session() as session:
        ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_2()

        # confirm start_time and end_time are time zone naive
        assert start_time.tzinfo is None and end_time.tzinfo is None

        # replace to UTC, because we treat time zone naive datetime as UTC
        start_time_utc = start_time.replace(tzinfo=tz.UTC)
        end_time_utc = end_time.replace(tzinfo=tz.UTC)

        local_tzinfo = tz.gettz('Europe/Warsaw')

        # now we can convert to different time zones (from time zone aware UTC datetime)
        start_time_local = start_time_utc.astimezone(local_tzinfo)
        end_time_local = end_time_utc.astimezone(local_tzinfo)

        test_case_naive = {"start_time": start_time, "end_time": end_time}
        test_case_utc = {"start_time": start_time_utc, "end_time": end_time_utc}
        test_case_local = {"start_time": start_time_local, "end_time": end_time_local}
        test_case_mixed = {"start_time": start_time_local, "end_time": end_time_utc}
        test_case_deduct = {"start_time": None, "end_time": None}  # in this case the start and end time will be taken from PyArrow table

        test_cases = [test_case_naive, test_case_utc, test_case_local, test_case_mixed, test_case_deduct]
        for test_case in test_cases:
            timeseries = Timeseries(table=modified_table, start_time=test_case['start_time'], end_time=test_case['end_time'], full_name=full_name)
            try:
                await session.write_timeseries_points(timeseries)
                written_ts = await session.read_timeseries_points(start_time=datetime(2016, 1, 1, 1, 0, 0),
                                                                  end_time=datetime(2016, 1, 1, 3, 0, 0),
                                                                  mesh_object_id=MeshObjectId.with_uuid_id(ts_entry.id))
                assert written_ts.number_of_points == 3
                utc_time = written_ts.arrow_table[0]
                assert utc_time[0].as_py() == datetime(2016, 1, 1, 1, 0, 0)
                assert utc_time[1].as_py() == datetime(2016, 1, 1, 2, 0, 0)
                assert utc_time[2].as_py() == datetime(2016, 1, 1, 3, 0, 0)
                flags = written_ts.arrow_table[1]
                for flag in flags:
                    assert flag.as_py() == Timeseries.PointFlags.OK.value
                values = written_ts.arrow_table[2]
                assert values[0].as_py() == 0
                assert values[1].as_py() == 10
                assert values[2].as_py() == 1000

                await session.rollback()

            except grpc.RpcError as e:
                pytest.fail(f"Could not write timeseries points {e}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_write_timeseries_points_with_different_pyarrow_table_datetime_timezones_async():
    """
    Check that timeseries points write accepts PyArrow data with time zone aware timestamps.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    async with connection.create_session() as session:
        ts_entry, _, _, _, full_name = get_timeseries_2()

        # There is problem with using in PyArrow time zone from dateutil gettz
        # I've found some PyArrow JIRA ticket with support for dateutil time zones:
        # https://issues.apache.org/jira/browse/ARROW-5248
        # Maybe it will solve the problem observed. It should be available in PyArrow 8.0.0.
        #local_tzinfo = tz.gettz('Europe/Warsaw')

        # For now lets create tzinfo using datetime timezone
        some_tzinfo = timezone(timedelta(hours=-3))

        arrays = [
            pa.array([datetime(2016, 1, 1, 1, tzinfo=some_tzinfo), datetime(2016, 1, 1, 2, tzinfo=some_tzinfo), datetime(2016, 1, 1, 3, tzinfo=some_tzinfo)]),
            pa.array([0, 0, 0]),
            pa.array([4.0, 44.0, 444.0])]
        modified_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

        timeseries = Timeseries(table=modified_table, start_time=datetime(2016, 1, 1, 1, tzinfo=some_tzinfo), end_time=datetime(2016, 1, 1, 4, tzinfo=some_tzinfo), full_name=full_name)
        try:
            await session.write_timeseries_points(timeseries)
            written_ts = await session.read_timeseries_points(start_time=datetime(2016, 1, 1, 1, tzinfo=some_tzinfo),
                                                              end_time=datetime(2016, 1, 1, 3, tzinfo=some_tzinfo),
                                                              mesh_object_id=MeshObjectId.with_uuid_id(ts_entry.id))
            assert written_ts.number_of_points == 3
            utc_time = written_ts.arrow_table[0]
            # Mesh returns timestamps in UTC format, to compare them we need to make both of them either
            # time zone aware or naive. In this case we are converting them to time zone aware objects.
            assert utc_time[0].as_py().replace(tzinfo=tz.UTC) == datetime(2016, 1, 1, 1, tzinfo=some_tzinfo).astimezone(tz.UTC)
            assert utc_time[1].as_py().replace(tzinfo=tz.UTC) == datetime(2016, 1, 1, 2, tzinfo=some_tzinfo).astimezone(tz.UTC)
            assert utc_time[2].as_py().replace(tzinfo=tz.UTC) == datetime(2016, 1, 1, 3, tzinfo=some_tzinfo).astimezone(tz.UTC)
            flags = written_ts.arrow_table[1]
            for flag in flags:
                assert flag.as_py() == Timeseries.PointFlags.OK.value
            values = written_ts.arrow_table[2]
            assert values[0].as_py() == 4
            assert values[1].as_py() == 44
            assert values[2].as_py() == 444

            await session.rollback()

        except grpc.RpcError as error:
            pytest.fail(f"Could not write timeseries points {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_timeseries_async():
    """Check that timeseries entry data can be retrieved"""

    timeseries, full_name = get_timeseries_1()
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        try:
            test_case_1 = {"path": full_name}
            test_case_2 = {"uuid_id": timeseries.id}
            test_case_3 = {"timskey": timeseries.timeseries_key}
            test_cases = [test_case_1, test_case_2, test_case_3]
            for test_case in test_cases:
                timeseries_info = await session.get_timeseries_resource_info(**test_case)
                assert _from_proto_guid(timeseries_info.id) == timeseries.id
                assert timeseries_info.timeseries_key == timeseries.timeseries_key
                assert timeseries_info.path == timeseries.path
                assert timeseries_info.temporary == timeseries.temporary
                assert timeseries_info.curve_type == _to_proto_curve_type(timeseries.curve)
                assert timeseries_info.resolution.type == timeseries.resolution.value
                assert timeseries_info.unit_of_measurement == timeseries.unit_of_measurement

        except grpc.RpcError as error:
            pytest.fail(f"Could not read timeseries entry: {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_timeseries_entry_async():
    """Check that timeseries entry data can be updated"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

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


        except grpc.RpcError as error:
            pytest.fail(f"Could not update timeseries entry: {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_timeseries_attribute_async():
    """Check that timeseries attribute data can be retrieved"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

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
                assert _from_proto_guid(reply.id) is not None
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
                assert _from_proto_guid(reply.id) is not None
                if "path" in test_case:
                    test_case_2["uuid_id"] = reply.id
                    attribute_with_entry.id = reply.id
                assert reply.path == full_name
                assert reply.local_expression == attribute_with_entry.local_expression
                assert reply.template_expression == attribute_with_entry.template_expression
                assert reply.HasField('entry')
                reply_timeseries = reply.entry
                expected_timeseries = attribute_with_entry.timeseries
                assert _from_proto_guid(reply_timeseries.id) == expected_timeseries.id
                assert reply_timeseries.timeseries_key == expected_timeseries.timeseries_key
                assert reply_timeseries.path == expected_timeseries.path
                assert reply_timeseries.temporary == expected_timeseries.temporary
                assert reply_timeseries.curve_type.type == expected_timeseries.curve.value
                assert reply_timeseries.resolution.type == expected_timeseries.resolution.value
                assert reply_timeseries.unit_of_measurement == expected_timeseries.unit_of_measurement
        except grpc.RpcError as error:
            pytest.fail(f"Could not get timeseries attribute {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_timeseries_attribute_with_timeseriescalculation_async():
    """Check that timeseries attribute data with a calculation can be updated"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

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

                await session.rollback()

        except grpc.RpcError as error:
            pytest.fail(f"Could not update timeseries attribute: {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_timeseries_attribute_with_timeseriesreference_async():
    """Check that timeseries attribute data with a reference can be updated"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute, full_name = get_timeseries_attribute_2()
    new_timeseries, _ = get_timeseries_1()
    new_timeseries_entry = new_timeseries.entries[0]
    new_timeseries_entry_id = core_pb2.TimeseriesEntryId(guid=_to_proto_guid(new_timeseries_entry.id))

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
                assert _from_proto_guid(original_attribute.entry.id) == attribute.timeseries.id

                if "path" in test_case:
                    test_case_2["uuid_id"] = original_attribute.id

                await session.update_timeseries_attribute(**test_case)

                updated_attribute = await session.get_timeseries_attribute(model=attribute.model, path=full_name)
                assert updated_attribute.path == full_name
                assert _from_proto_guid(updated_attribute.entry.id) == new_timeseries.id

                await session.rollback()

        except grpc.RpcError as error:
            pytest.fail(f"Could not update timeseries attribute: {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_search_timeseries_attribute_async():
    """Check that timeseries attribute data can be searched for"""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

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
                assert _from_proto_guid(match.id) is not None
                assert match.local_expression == ts_attribute.local_expression
                assert match.template_expression == ts_attribute.template_expression
                assert match.HasField('entry')
                reply_timeseries = match.entry
                expected_timeseries = ts_attribute.timeseries
                assert _from_proto_guid(reply_timeseries.id) == expected_timeseries.id
                assert reply_timeseries.timeseries_key == expected_timeseries.timeseries_key
                assert reply_timeseries.path == expected_timeseries.path
                assert reply_timeseries.temporary == expected_timeseries.temporary
                assert reply_timeseries.curve_type == _to_proto_curve_type(expected_timeseries.curve)
                assert reply_timeseries.resolution.type == expected_timeseries.resolution.value
                assert reply_timeseries.unit_of_measurement == expected_timeseries.unit_of_measurement
        except grpc.RpcError as error:
            pytest.fail(f"Could not update timeseries attribute: {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_write_timeseries_points_using_timskey_async():
    """Check that timeseries can be written to the server using timskey."""

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
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
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute, full_name = get_timeseries_attribute_1()
    new_local_expression = "something"
    old_local_expression = attribute.local_expression

    async with connection.create_session() as session1:
        try:
            # check baseline
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

        except grpc.RpcError as error:
            pytest.fail(f"Could not commit changes: {error}")

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

        except grpc.RpcError as error:
            pytest.fail(f"Could not restore commited changes: {error}")


@pytest.mark.asyncio
@pytest.mark.database
async def test_rollback():
    """Check that rollback discards changes made in the current session."""
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        try:
            _, full_name = get_timeseries_1()
            new_path = "/new_path"

            # check baseline
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

        except grpc.RpcError as error:
            pytest.fail(f"Could not rollback changes: {error}")


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
     [transform.Method.SUM,
      transform.Method.SUMI,
      transform.Method.AVG,
      transform.Method.AVGI,
      transform.Method.FIRST,
      transform.Method.LAST,
      transform.Method.MIN,
      transform.Method.MAX])
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
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = await session.transform_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).transform(
                resolution, method, timezone)

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
                if method is transform.Method.AVG and resolution is Timeseries.Resolution.MIN15:
                    # the original timeseries data is in hourly resolution,
                    # starts with 1 and the value is incremented with each hour up to 9
                    # here we are using 15 min resolution, so the delta between each 15 min point is 0.25
                    assert value == 1 + index * 0.25

            expected_date += delta
            index += 1


@pytest.mark.asyncio
@pytest.mark.database
async def test_read_transformed_timeseries_points_with_uuid():
    """
    Check that transformed timeseries read by full_name or UUID
    (both pointing to the same object) return the same data.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        # set interval where there are no NaNs to comfortably use `assert ==``
        start_time = datetime(2016, 1, 1, 5, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        # first read timeseries UUID (it is set dynamically)
        timeseries = await session.read_timeseries_points(start_time=start_time,
                                                          end_time=end_time,
                                                          mesh_object_id=MeshObjectId.with_full_name(full_name))
        ts_uuid = timeseries.uuid

        reply_timeseries_full_name = await session.transform_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).transform(
                Timeseries.Resolution.MIN15, transform.Method.SUM)

        reply_timeseries_uuid = await session.transform_functions(
            MeshObjectId(uuid_id=ts_uuid), start_time, end_time).transform(
                Timeseries.Resolution.MIN15, transform.Method.SUM)

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
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)

        with pytest.raises(TypeError, match=".*need to specify either timskey, uuid_id or full_name.*"):
            await session.read_timeseries_points(start_time, end_time, MeshObjectId())


@pytest.mark.asyncio
@pytest.mark.database
async def test_forecast_get_all_forecasts():
    """
    Check that running forecast `get_all_forecasts`
    does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = await session.forecast_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).get_all_forecasts()
        assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0


@pytest.mark.asyncio
@pytest.mark.database
@pytest.mark.parametrize('forecast_start',
    [(None, None),
     (datetime(2016, 1, 2), datetime(2016, 1, 8))])
@pytest.mark.parametrize('available_at_timepoint',
    [None,
     datetime(2016, 1, 5, 17, 48, 11, 123456)])
async def test_forecast_get_forecast(forecast_start, available_at_timepoint):
    """
    Check that running forecast `get_forecast`
    does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        forecast_start_min, forecast_start_max = forecast_start
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = await session.forecast_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).get_forecast(
                forecast_start_min, forecast_start_max, available_at_timepoint)
        assert reply_timeseries.is_calculation_expression_result


@pytest.mark.asyncio
@pytest.mark.database
async def test_history_get_ts_as_of_time():
    """
    Check that running history `get_ts_as_of_time`
    does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        available_at_timepoint = datetime(2016, 1, 5, 17, 48, 11, 123456)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = await session.history_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).get_ts_as_of_time(
                available_at_timepoint)
        assert reply_timeseries.is_calculation_expression_result


@pytest.mark.asyncio
@pytest.mark.database
@pytest.mark.parametrize('max_number_of_versions_to_get',
    [1, 2, 5])
async def test_history_get_ts_historical_versions(max_number_of_versions_to_get):
    """
    Check that running history `get_ts_historical_versions`
    does not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = await session.history_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).get_ts_historical_versions(
                max_number_of_versions_to_get)
        assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0


@pytest.mark.asyncio
@pytest.mark.database
async def test_statistical_sum():
    """
    Check that running statistical `sum`
    errordoes not throw exception for any combination of parameters.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = await session.statistical_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).sum(search_query='some_query')
        assert reply_timeseries.is_calculation_expression_result


@pytest.mark.asyncio
@pytest.mark.database
async def test_statistical_sum_single_timeseries():
    """
    Check that running statistical `sum_single_timeseries` works correctly.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        result = await session.statistical_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).sum_single_timeseries()
        assert isinstance(result, float) and result == 41.0


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_object():
    """
    Check that `get_object` returns specified object with
    all attributes and basic attribute information.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        object_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"

        object = await session.get_object(object_path=object_path)
        assert object.name == "SomePowerPlant1"
        assert object.path == object_path
        assert object.type_name == "PlantElementType"
        assert object.owner_path == "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef"
        assert len(object.attributes) == 23

        for attribute in object.attributes.values():
            assert attribute.name is not None
            assert attribute.path is not None
            assert attribute.id is not None
            # without full info the definition is not set
            assert attribute.definition is None


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_object_with_full_attribute_info():
    """
    Check that `get_object` returns specified object with
    all attributes and full attribute information.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        object_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"

        object = await session.get_object(object_path=object_path, full_attribute_info=True)
        for attribute in object.attributes.values():
            assert attribute.name is not None
            assert attribute.path is not None
            assert attribute.id is not None
            # with full info the definition is set
            assert attribute.definition is not None

        # check one of the attributes
        assert object.attributes["StringAtt"].definition.default_value == "Default string value"


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_object_with_attributes_filter_with_name_mask():
    """
    Check that `get_object` returns specified object with filtered attributes.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        object_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
        attributes_filter = AttributesFilter(name_mask=["StringAtt", "BoolArrayAtt"])

        object = await session.get_object(
            object_path=object_path, attributes_filter=attributes_filter)

        assert object.attributes['StringAtt'] is not None
        assert object.attributes['BoolArrayAtt'] is not None


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_object_with_attributes_filter_with_non_existing_masks():
    """
    Check that `get_object` returns specified object with no attributes
    when non existing masks are used in attributes filter.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        object_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
        attributes_filter = AttributesFilter(namespace_mask=["NON_EXISTING"])

        object = await session.get_object(
            object_path=object_path, attributes_filter=attributes_filter)
        assert len(object.attributes) == 0


@pytest.mark.asyncio
@pytest.mark.database
async def test_get_object_with_attributes_filter_with_return_no_attributes():
    """
    Check that `get_object` returns specified object with no attributes
    when `return_no_attributes` is set to True in attributes filter.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        object_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"
        attributes_filter = AttributesFilter(return_no_attributes=True)

        object = await session.get_object(
            object_path=object_path, attributes_filter=attributes_filter)
        assert len(object.attributes) == 0


@pytest.mark.asyncio
@pytest.mark.database
async def test_search_objects():
    """
    Check that `search_objects` returns correct objects according to specified search query.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"
        query = "*[.Type=ChimneyElementType]"

        objects = await session.search_for_objects(query, start_object_path=start_object_path)
        assert len(objects) == 2

        for object in objects:
            assert object.name == "SomePowerPlantChimney1" or object.name == "SomePowerPlantChimney2"
            assert len(object.attributes) == 7


@pytest.mark.asyncio
@pytest.mark.database
async def test_create_object():
    """
    Check that `create_object` creates and returns new object.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        owner_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef"
        new_object_name = "SomeNewPowerPlantChimney"

        new_object = await session.create_object(name=new_object_name, owner_attribute_path=owner_attribute_path)
        assert new_object.name == new_object_name
        assert new_object.path == f"{owner_attribute_path}/{new_object_name}"

        object = await session.get_object(object_id=new_object.id)
        assert new_object.name == object.name
        assert new_object.path == object.path
        assert new_object.type_name == object.type_name
        assert new_object.owner_id == object.owner_id
        assert new_object.owner_path == object.owner_path


@pytest.mark.asyncio
@pytest.mark.database
async def test_update_object():
    """
    Check that `update_object` updates existing object.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        object_to_update_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef/SomePowerPlantChimney2"
        new_owner_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef/SomePowerPlantChimney1.ChimneyToChimneyRef"
        new_object_name = "SomeNewPowerPlantChimney"

        await session.update_object(
            object_path=object_to_update_path,
            new_name=new_object_name,
            new_owner_attribute_path=new_owner_attribute_path)

        new_object_path = f"{new_owner_attribute_path}/{new_object_name}"

        object = await session.get_object(object_path=new_object_path)
        assert object.name == new_object_name
        assert object.path == new_object_path
        assert object.owner_path == new_owner_attribute_path


@pytest.mark.asyncio
@pytest.mark.database
async def test_delete_object():
    """
    Check that `delete_object` deletes existing object without children.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        object_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.PlantToChimneyRef/SomePowerPlantChimney2"

        await session.delete_object(object_path=object_path)
        with pytest.raises(grpc.RpcError, match=r"Object not found:"):
            await session.get_object(object_path=object_path)


@pytest.mark.asyncio
@pytest.mark.database
async def test_recursive_delete_object():
    """
    Check that `delete_object` deletes recursively existing object with children.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                                 sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        object_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1"

        await session.delete_object(object_path=object_path, recursive_delete=True)
        with pytest.raises(grpc.RpcError, match=r"Object not found:"):
            await session.get_object(object_path=object_path)

@pytest.mark.asyncio
@pytest.mark.database
async def test_get_bool_array_attribute():
    """
    Check that 'get_attribute' with full attribute view retrieves a boolean array attribute and its definition.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    attribute_name = "BoolArrayAtt"
    bool_array_att_path = get_attribute_path_principal() + attribute_name
    bool_array_values = [False, True, False, True, False]
    async with connection.create_session() as session:
        attribute = await session.get_attribute(attribute_path=bool_array_att_path, full_attribute_info=True)
        assert attribute.path == bool_array_att_path
        assert attribute.name == attribute_name
        assert attribute.definition.path == "Repository/SimpleThermalTestRepository/PlantElementType/" + attribute_name
        assert attribute.name == attribute_name
        assert attribute.definition.description == "Array of bools"
        assert len(attribute.definition.tags) == 0
        assert attribute.definition.namespace == "SimpleThermalTestRepository"
        assert attribute.definition.value_type == "BooleanArrayAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 0
        assert attribute.definition.maximum_cardinality == 10
        for values in zip(attribute.value, bool_array_values):
            assert values[0] == values[1]

@pytest.mark.asyncio
@pytest.mark.database
async def test_get_xy_set_attribute():
    """
    Check that 'get_attribute' with full attribute view retrieves a XY set attribute and its definition.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    attribute_name = "XYSetAtt"
    xySetAttPath = get_attribute_path_principal() + attribute_name
    async with connection.create_session() as session:
        attribute = await session.get_attribute(attribute_path=xySetAttPath, full_attribute_info=True)
        assert attribute.path == xySetAttPath
        assert attribute.name == attribute_name
        assert attribute.definition.path == "Repository/SimpleThermalTestRepository/PlantElementType/" + attribute_name
        assert attribute.name == attribute_name
        assert attribute.definition.description == ""
        assert len(attribute.definition.tags) == 0
        assert attribute.definition.namespace == "SimpleThermalTestRepository"
        assert attribute.definition.value_type == "XYSetAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 1
        assert attribute.definition.maximum_cardinality == 1
        # so far no definition

@pytest.mark.asyncio
@pytest.mark.database
async def test_get_utc_time_attribute():
    """
    Check that 'get_attribute' with full attribute view retrieves a UtcDateTime attribute and its definition.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    attribute_name = "UtcDateTimeAtt"
    utc_date_time_att_path = get_attribute_path_principal() + attribute_name
    # your UtcDateTimeAtt in SimpleThermalModel should be populated with this value
    utc_time_value = datetime(2022, 5, 10, 7, 24, 15, tzinfo=tz.UTC)

    async with connection.create_session() as session:
        attribute = await session.get_attribute(attribute_path=utc_date_time_att_path, full_attribute_info=True)
        assert attribute.value == utc_time_value
        assert attribute.path == utc_date_time_att_path
        assert attribute.name == attribute_name
        assert attribute.definition.path == "Repository/SimpleThermalTestRepository/PlantElementType/" + attribute_name
        assert attribute.name == attribute_name
        assert attribute.definition.description == ""
        assert len(attribute.definition.tags) == 0
        assert attribute.definition.namespace == "SimpleThermalTestRepository"
        assert attribute.definition.value_type == "UtcDateTimeAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 1
        assert attribute.definition.maximum_cardinality == 1
        assert attribute.definition.default_value == "UTC20220510072415"
        assert attribute.definition.minimum_value == None
        assert attribute.definition.maximum_value == None

@pytest.mark.asyncio
@pytest.mark.database
async def test_get_boolean_attribute():
    """
    Check that 'get_attribute' with full attribute view retrieves a boolean attribute and its definition.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    attribute_name = "BoolAtt"
    bool_attribute_path = get_attribute_path_principal() + attribute_name

    async with connection.create_session() as session:
        attribute = await session.get_attribute(attribute_path=bool_attribute_path, full_attribute_info=False)
        bool_attribute_id = attribute.id
        assert attribute.path == bool_attribute_path
        assert attribute.name == attribute_name
        assert attribute.value == True
        # now check if get by id succeeds as well
        attribute = await session.get_attribute(attribute_id=bool_attribute_id, full_attribute_info=True)
        assert attribute.path == bool_attribute_path
        assert attribute.name == attribute_name
        assert attribute.value == True
        assert attribute.definition.path == "Repository/SimpleThermalTestRepository/PlantElementType/" + attribute_name
        assert attribute.name == attribute_name
        assert attribute.definition.description == ""
        assert len(attribute.definition.tags) == 0
        assert attribute.definition.namespace == "SimpleThermalTestRepository"
        assert attribute.definition.value_type == "BooleanAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 1
        assert attribute.definition.maximum_cardinality == 1
        assert attribute.definition.default_value == True

def verify_time_series_calculation_attribute(
    attribute: TimeseriesAttribute, attribute_info: Tuple[str, bool], attribute_name: str):

    expression = attribute_info[0]
    is_local_expression = attribute_info[1]

    str_atttribute_path = get_attribute_path_principal() + attribute_name
    assert attribute.path == str_atttribute_path
    assert attribute.name == attribute_name
    assert attribute.expression == expression
    assert attribute.is_local_expression == is_local_expression
    assert attribute.definition.path == "Repository/SimpleThermalTestRepository/PlantElementType/" + attribute_name
    assert attribute.name == attribute_name
    assert attribute.definition.description == ""
    assert len(attribute.definition.tags) == 0
    assert attribute.definition.namespace == "SimpleThermalTestRepository"
    assert attribute.definition.value_type == "TimeseriesAttributeDefinition"
    assert attribute.definition.minimum_cardinality == 1
    assert attribute.definition.maximum_cardinality == 1
    assert attribute.definition.template_expression == expression

@pytest.mark.asyncio
@pytest.mark.database
async def test_get_calc_time_series_attribute():
    """
    Check that 'get_attribute' with full attribute view retrieves a calculation time series attribute and its definition.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute_name = "TsCalcAtt2"
    expression = "##= @SUM(@T('ReferenceSeriesCollectionAtt.TsRawAtt'))\n\n"
    str_atttribute_path = get_attribute_path_principal() + attribute_name
    is_local_expression = False
    async with connection.create_session() as session:
        attribute = await session.get_attribute(attribute_path=str_atttribute_path, full_attribute_info=True)
        verify_time_series_calculation_attribute(attribute=attribute, attribute_info=tuple((expression, is_local_expression)), attribute_name=attribute_name)

@pytest.mark.asyncio
@pytest.mark.database
async def test_get_physical_time_series_attribute():
    """
    Check that 'get_attribute' with full attribute view retrieves a physical time series attribute and its definition.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute_name = "TsRawAtt"
    str_atttribute_path = get_attribute_path_principal() + attribute_name
    async with connection.create_session() as session:
        base_attribute = await session.get_attribute(attribute_path=str_atttribute_path, full_attribute_info=True)

        for attribute in [base_attribute]:
            assert attribute.path == str_atttribute_path
            assert attribute.name == attribute_name
            assert attribute.time_series_resource.timeseries_key == 0
            assert attribute.time_series_resource.temporary == False
            assert attribute.time_series_resource.curve_type == Timeseries.Curve.PIECEWISELINEAR
            assert attribute.time_series_resource.resolution == Timeseries.Resolution.HOUR
            assert attribute.time_series_resource.unit_of_measurement == "Unit2"
            assert attribute.expression == ""
            assert attribute.is_local_expression == False
            assert attribute.definition.path == "Repository/SimpleThermalTestRepository/PlantElementType/" + attribute_name
            # attribute definition name is the same as attribute name
            assert attribute.definition.name == attribute_name
            assert attribute.definition.description == ""
            assert len(attribute.definition.tags) == 0
            assert attribute.definition.namespace == "SimpleThermalTestRepository"
            assert attribute.definition.value_type == "TimeseriesAttributeDefinition"
            assert attribute.definition.minimum_cardinality == 1
            assert attribute.definition.maximum_cardinality == 1
            assert attribute.definition.template_expression == ""

@pytest.mark.asyncio
@pytest.mark.database
async def test_get_string_attribute():
    """
    Check that 'get_attribute' with full attribute view retrieves a string attribute and its definition.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute_name = "StringAtt"
    str_atttribute_path = get_attribute_path_principal() + attribute_name
    default_string_value = "Default string value"
    async with connection.create_session() as session:
        attribute = await session.get_attribute(attribute_path=str_atttribute_path, full_attribute_info=True)
        assert attribute.path == str_atttribute_path
        assert attribute.name == attribute_name
        assert attribute.value == default_string_value
        assert attribute.definition.path == "Repository/SimpleThermalTestRepository/PlantElementType/" + attribute_name
        assert attribute.name == attribute_name
        assert attribute.definition.description == ""
        assert len(attribute.definition.tags) == 0
        assert attribute.definition.namespace == "SimpleThermalTestRepository"
        assert attribute.definition.value_type == "StringAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 1
        assert attribute.definition.maximum_cardinality == 1
        assert attribute.definition.default_value == default_string_value

def verify_double_attribute(attribute: core_pb2.Attribute, dbl_attribute_path: str, attribute_name: str):
        assert attribute.path == dbl_attribute_path
        assert attribute.name == attribute_name
        assert attribute.value == 1000
        assert attribute.definition.path == "Repository/SimpleThermalTestRepository/PlantElementType/" + attribute_name
        assert attribute.name == attribute_name
        assert attribute.definition.description == ""
        assert len(attribute.definition.tags) == 0
        assert attribute.definition.namespace == "SimpleThermalTestRepository"
        assert attribute.definition.value_type == "DoubleAttributeDefinition"
        assert attribute.definition.minimum_cardinality == 1
        assert attribute.definition.maximum_cardinality == 1
        assert attribute.definition.default_value == 1000
        assert attribute.definition.minimum_value == -sys.float_info.max
        assert attribute.definition.maximum_value == sys.float_info.max
        assert attribute.definition.unit_of_measurement == None

@pytest.mark.asyncio
@pytest.mark.database
async def test_get_double_attribute():
    """
    Check that 'get_attribute' with full attribute view retrieves a double attribute and its definition.
    """

    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute_name = "DblAtt"
    dbl_attribute_path = get_attribute_path_principal() + attribute_name

    async with connection.create_session() as session:
        attribute = await session.get_attribute(attribute_path=dbl_attribute_path, full_attribute_info=True)
        verify_double_attribute(attribute=attribute, dbl_attribute_path=dbl_attribute_path, attribute_name=attribute_name)

@pytest.mark.asyncio
@pytest.mark.database
async def test_search_multiple_attributes():
    """
    Check that 'search_for_attributes' with full attribute view retrieves requested attributes and their definitions.
    """
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    start_object_path = "Model/SimpleThermalTestModel"

    #requested attributes
    attributes_names = ["TsCalcAtt", "TsCalcAtt2", "TsCalcAtt4", "TsCalcAtt7"]
    # holds an expression and information about it's expression locality
    attributes_info = {
        attributes_names[0]: tuple(("@PDLOG(12004, 'TEST') \n##= @d('.DblAtt') + @t('.TsRawAtt') + @SUM(@D('PlantToPlantRef.DblAtt'))\n\n", True)),
        attributes_names[1]: tuple(("##= @SUM(@T('ReferenceSeriesCollectionAtt.TsRawAtt'))\n\n", False)),
        attributes_names[2]: tuple(("temp=@t('.TsRawAtt')\ngt2 = @ABS(temp) > 2\n## = temp - 1000\nIF (gt2) THEN\n## = temp + 1000\nENDIF\n", False)),
        attributes_names[3]: tuple(("##=@Restriction('ProductionMin[MW]', 'Proposed|Recommended', @t('.TsRawAtt'), 'Minimum')\n", False))
    }
    # search query
    query = "*[.Name=SomePowerPlant1]." + ",".join(attributes_names)

    async with connection.create_session() as session:
        attributes = await session.search_for_attributes(
            query=query,
            start_object_path=start_object_path,
            full_attribute_info=True)
        assert len(attributes) == len(attributes_names)
        for attribute in attributes:
            assert attribute.name in attributes_names
            verify_time_series_calculation_attribute(attribute=attribute, attribute_info=attributes_info[attribute.name], attribute_name=attribute.name)

@pytest.mark.asyncio
@pytest.mark.database
async def test_search_with_absent_attribute():
    """
    Check that 'search_for_attributes' with query containing absent attribute will return all of the existing attributes
    """
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    start_object_path = "Model/SimpleThermalTestModel"

    #requested attributes, one doesn't exist
    attributes_names = ["DblAtt", "ABSENT_ATTRIBUTE_NAME"]
    # search query
    query = "*[.Name=SomePowerPlant1]." + ",".join(attributes_names)
    dbl_attribute_path = get_attribute_path_principal() + attributes_names[0]

    async with connection.create_session() as session:
        attributes = await session.search_for_attributes(
            query=query,
            start_object_path=start_object_path,
            full_attribute_info=True)
        assert len(attributes) == 1
        verify_double_attribute(attribute=attributes[0], dbl_attribute_path=dbl_attribute_path, attribute_name=attributes_names[0])

async def update_double_attribute(session: AsyncConnection.Session, new_double_value):
    attribute_path = get_attribute_path_principal() + "DblAtt"

    double_attribute = await session.get_attribute(attribute_path=attribute_path)
    assert not math.isclose(new_double_value, double_attribute.value)

    await session.update_simple_attribute(
        attribute_path=attribute_path,
        value=new_double_value
    )

    double_attribute = await session.get_attribute(attribute_path=attribute_path)
    assert math.isclose(new_double_value, double_attribute.value)

@pytest.mark.asyncio
@pytest.mark.database
async def test_update_attribute_invalid_request():
    """
    Check that 'update_attribute' with invalid request
     (wrong value type and dimension) will throw
    """
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                        sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute_path = get_attribute_path_principal() + "BoolArrayAtt"
    async with connection.create_session() as session:
        # boolean array attribute, wrong value type and dimension
        array_attribute = await session.get_attribute(attribute_path=attribute_path)
        original_values = array_attribute.value

        with pytest.raises(grpc.RpcError):
            await session.update_simple_attribute(attribute_path=attribute_path, value=7)
        
        array_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert array_attribute.value == original_values
        
@pytest.mark.asyncio
@pytest.mark.database
async def test_update_simple_array_attribute():
    """
    Check that 'update_attribute' will correctly update array attribute values
    """
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute_path = get_attribute_path_principal() + "BoolArrayAtt"
    async with connection.create_session() as session:
        #boolean array attribute
        new_boolean_array_values = [False, False, True, False, False]

        array_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert array_attribute.value != new_boolean_array_values

        await session.update_simple_attribute(attribute_path=attribute_path, value=new_boolean_array_values)
        
        array_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert array_attribute.value == new_boolean_array_values

@pytest.mark.asyncio
@pytest.mark.database
async def test_update_single_simple_attribute():
    """
    Check that 'update_attribute' will correctly update single attributes values
    """
    connection = AsyncConnection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    async with connection.create_session() as session:
        await update_double_attribute(session, 5.0) # float provided
        await update_double_attribute(session, 13) # int provided

        # int attribute
        new_int_value = 69
        attribute_path = get_attribute_path_principal() + "Int64Att"
        int_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert new_int_value != int_attribute.value

        await session.update_simple_attribute(attribute_path=attribute_path, value=new_int_value)

        int_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert int_attribute.value == new_int_value

        # boolean attribute
        new_boolean_value = False
        attribute_path = get_attribute_path_principal() + "BoolAtt"
        boolean_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert new_boolean_value != boolean_attribute.value
        await session.update_simple_attribute(attribute_path=attribute_path, value=new_boolean_value)

        boolean_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert boolean_attribute.value == new_boolean_value

        # string attribute
        new_string_value = "my test string attribute value"
        attribute_path = get_attribute_path_principal() + "StringAtt"
        string_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert new_string_value != string_attribute.value
        await session.update_simple_attribute(attribute_path=attribute_path, value=new_string_value)

        string_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert string_attribute.value == new_string_value

        # utcDateTime attribute
        new_utc_value = datetime(2022, 5, 14, 13, 44, 45, 0, tzinfo=tz.UTC)
        attribute_path = get_attribute_path_principal() + "UtcDateTimeAtt"
        utc_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert new_utc_value != utc_attribute.value

        await session.update_simple_attribute(attribute_path=attribute_path, value=new_utc_value)

        utc_attribute = await session.get_attribute(attribute_path=attribute_path)
        assert utc_attribute.value == new_utc_value

if __name__ == '__main__':
    pytest.main()
