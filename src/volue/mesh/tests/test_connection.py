"""
Tests for volue.mesh.Connection
"""

from datetime import datetime, timedelta, timezone
import math
from typing import List
import uuid

from dateutil import tz
import grpc
import pyarrow as pa
import pytest

from volue.mesh import Connection, MeshObjectId, Timeseries
from volue.mesh._common import _from_proto_guid, _to_proto_curve_type, _to_proto_guid
from volue.mesh.calc import transform as Transform
from volue.mesh.calc.common import Timezone
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.proto.core.v1alpha import core_pb2
from volue.mesh.proto.type import resources_pb2
from volue.mesh.tests.test_utilities.utilities import get_timeseries_2, get_timeseries_1, \
    get_timeseries_attribute_1, get_timeseries_attribute_2, verify_timeseries_2


@pytest.mark.database
def test_read_timeseries_points():
    """Check that timeseries points can be read using timeseries key, UUID and full name"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    with connection.create_session() as session:
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
                reply_timeseries = session.read_timeseries_points(**test_case)
                verify_timeseries_2(reply_timeseries)
        except grpc.RpcError as error:
            pytest.fail(f"Could not read timeseries points: {error}")


@pytest.mark.database
def test_read_timeseries_points_with_different_datetime_timezones():
    """
    Check that timeseries points read accepts time zone aware and
    naive (treated as UTC) datetimes as input arguments.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    with connection.create_session() as session:
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
                reply_timeseries = session.read_timeseries_points(**test_case)
                verify_timeseries_2(reply_timeseries)
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.database
def test_write_timeseries_points():
    """
    Check that timeseries points write accepts time series with time zone aware and
    naive (treated as UTC) datetimes as input interval (start_time and end_time arguments).
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    with connection.create_session() as session:
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

        test_cases = [test_case_naive, test_case_utc, test_case_local, test_case_mixed]
        for test_case in test_cases:
            timeseries = Timeseries(table=modified_table, start_time=test_case['start_time'], end_time=test_case['end_time'], full_name=full_name)
            try:
                session.write_timeseries_points(timeseries)
                written_ts = session.read_timeseries_points(start_time=datetime(2016, 1, 1, 1, 0, 0),
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

                session.rollback()

            except grpc.RpcError as e:
                pytest.fail(f"Could not write timeseries points {e}")


@pytest.mark.database
def test_write_timeseries_points_with_different_pyarrow_table_datetime_timezones():
    """
    Check that timeseries points write accepts PyArrow data with time zone aware timestamps.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    with connection.create_session() as session:
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
            session.write_timeseries_points(timeseries)
            written_ts = session.read_timeseries_points(start_time=datetime(2016, 1, 1, 1, tzinfo=some_tzinfo),
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

            session.rollback()

        except grpc.RpcError as error:
            pytest.fail(f"Could not write timeseries points {error}")


@pytest.mark.database
def test_get_timeseries():
    """Check that timeseries entry data can be retrieved"""

    timeseries, full_name = get_timeseries_1()
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        try:
            test_case_1 = {"path": full_name}
            test_case_2 = {"uuid_id": timeseries.id}
            test_case_3 = {"timskey": timeseries.timeseries_key}
            test_cases = [test_case_1, test_case_2, test_case_3]
            for test_case in test_cases:
                timeseries_info = session.get_timeseries_resource_info(**test_case)
                assert _from_proto_guid(timeseries_info.id) == timeseries.id
                assert timeseries_info.timeseries_key == timeseries.timeseries_key
                assert timeseries_info.path == timeseries.path
                assert timeseries_info.temporary == timeseries.temporary
                assert timeseries_info.curve_type == _to_proto_curve_type(timeseries.curve)
                assert timeseries_info.resolution.type == timeseries.resolution.value
                assert timeseries_info.unit_of_measurement == timeseries.unit_of_measurement

        except grpc.RpcError as error:
            pytest.fail(f"Could not read timeseries entry: {error}")


@pytest.mark.database
def test_update_timeseries_entry():
    """Check that timeseries entry data can be updated"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    new_path = "/test"
    new_curve_type = "curvy"  # -> UNKNOWN
    new_unit_of_measurement = "mega watt"

    with connection.create_session() as session:
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
                session.update_timeseries_resource_info(**test_case)
                timeseries_info = session.get_timeseries_resource_info(**test_id)

                if "new_path" in test_case:
                    assert timeseries_info.path == new_path
                if "new_curve_type" in test_case:
                    assert timeseries_info.curve_type.type == resources_pb2.Curve.UNKNOWN
                if "new_unit_of_measurement" in test_case:
                    assert timeseries_info.unit_of_measurement == new_unit_of_measurement

                session.rollback()

        except grpc.RpcError as error:
            pytest.fail(f"Could not update timeseries entry: {error}")


@pytest.mark.database
def test_read_timeseries_attribute():
    """Check that timeseries attribute data can be retrieved"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
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
                reply = session.get_timeseries_attribute(**test_case)
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
                reply = session.get_timeseries_attribute(**test_case)
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


@pytest.mark.database
def test_update_timeseries_attribute_with_timeseriescalculation():
    """Check that timeseries attribute data with a calculation can be updated"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute, full_name = get_timeseries_attribute_1()
    new_local_expression = "something"

    with connection.create_session() as session:
        try:
            test_new_local_expression = {"new_local_expression": new_local_expression}
            test_case_1 = {"path": full_name, **test_new_local_expression}
            test_case_2 = {"uuid_id": None,
                           **test_new_local_expression}  # since it is generated we find it through the first test case
            test_cases = [test_case_1, test_case_2]

            for test_case in test_cases:

                session.update_timeseries_attribute(**test_case)

                updated_attribute = session.get_timeseries_attribute(model=attribute.model, path=full_name)
                assert updated_attribute.path == full_name
                assert updated_attribute.local_expression == new_local_expression

                if "path" in test_case:
                    test_case_2["uuid_id"] = updated_attribute.id

                session.rollback()

        except grpc.RpcError as error:
            pytest.fail(f"Could not update timeseries attribute: {error}")


@pytest.mark.database
def test_update_timeseries_attribute_with_timeseriesreference():
    """Check that timeseries attribute data with a reference can be updated"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute, full_name = get_timeseries_attribute_2()

    new_timeseries, _ = get_timeseries_1()
    new_timeseries_entry = new_timeseries.entries[0]
    new_timeseries_entry_id = core_pb2.TimeseriesEntryId(guid=_to_proto_guid(new_timeseries_entry.id))

    with connection.create_session() as session:
        try:
            test_new_timeseries_entry_id = {"new_timeseries_entry_id": new_timeseries_entry_id}
            test_case_1 = {"path": full_name, **test_new_timeseries_entry_id}
            test_case_2 = {"uuid_id": None,
                           **test_new_timeseries_entry_id}  # since it is generated we find it through the first test case
            test_cases = [test_case_1, test_case_2]
            for test_case in test_cases:
                original_attribute = session.get_timeseries_attribute(model=attribute.model, path=full_name)
                assert original_attribute.path == full_name
                assert _from_proto_guid(original_attribute.entry.id) == attribute.timeseries.id

                if "path" in test_case:
                    test_case_2["uuid_id"] = original_attribute.id

                session.update_timeseries_attribute(**test_case)

                updated_attribute = session.get_timeseries_attribute(model=attribute.model, path=full_name)
                assert updated_attribute.path == full_name
                assert _from_proto_guid(updated_attribute.entry.id) == new_timeseries.id

                session.rollback()

        except grpc.RpcError as error:
            pytest.fail(f"Could not update timeseries attribute: {error}")


@pytest.mark.database
def test_search_timeseries_attribute():
    """Check that timeseries attribute data can be searched for"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    ts_attribute, full_name = get_timeseries_attribute_2()

    query = "{*}.TsRawAtt"
    start_object_path = "ThermalComponent"
    start_object_guid = uuid.UUID("0000000b-0001-0000-0000-000000000000")  # ThermalComponent

    with connection.create_session() as session:
        try:
            test_case_1 = {"model": ts_attribute.model,
                           "query": query,
                           "start_object_path": start_object_path}
            test_case_2 = {"model": ts_attribute.model,
                           "query": query,
                           "start_object_guid": start_object_guid}
            test_cases = [test_case_1, test_case_2]
            for test_case in test_cases:
                reply = session.search_for_timeseries_attribute(**test_case)
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


@pytest.mark.database
async def test_write_timeseries_points_using_timskey_async():
    """Check that timeseries can be written to the server using timskey."""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)
    ts_entry, start_time, end_time, modified_table, _ = get_timeseries_2()
    timeseries = Timeseries(table=modified_table, start_time=start_time, end_time=end_time,
                            timskey=ts_entry.timeseries_key)

    with connection.create_session() as session:
        try:
            session.write_timeseries_points(
                timeserie=timeseries
            )
        except grpc.RpcError:
            pytest.fail("Could not write timeseries points")


@pytest.mark.database
def test_commit():
    """Check that commit keeps changes between sessions"""
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    attribute, full_name = get_timeseries_attribute_1()
    new_local_expression = "something"
    old_local_expression = attribute.local_expression

    with connection.create_session() as session1:
        try:
            # check base line
            attribute1 = session1.get_timeseries_attribute(model=attribute.model, path=full_name)
            old_local_expression = attribute1.local_expression
            assert attribute1.local_expression != new_local_expression

            # change something
            session1.update_timeseries_attribute(path=full_name, new_local_expression=new_local_expression)

            # commit
            session1.commit()

            # check that the change is in the session
            attribute2 = session1.get_timeseries_attribute(model=attribute.model, path=full_name)
            assert attribute2.local_expression == new_local_expression

            # rollback
            session1.rollback()

            # check that changes are still there
            attribute3 = session1.get_timeseries_attribute(model=attribute.model, path=full_name)
            assert attribute3.local_expression == new_local_expression

        except grpc.RpcError as error:
            pytest.fail(f"Could not commit changes: {error}")

    with connection.create_session() as session2:
        try:
            # check that the change is still there
            attribute4 = session2.get_timeseries_attribute(model=attribute.model, path=full_name)
            assert attribute4.local_expression == new_local_expression

            # change it back to what is was originally
            session2.update_timeseries_attribute(path=full_name, new_local_expression=old_local_expression)

            # commit
            session2.commit()

            # check that status has been restored (important to keep db clean)
            attribute5 = session2.get_timeseries_attribute(model=attribute.model, path=full_name)
            assert attribute5.local_expression == old_local_expression

        except grpc.RpcError as error:
            pytest.fail(f"Could not restore commited changes: {error}")


@pytest.mark.database
def test_rollback():
    """Check that rollback discards changes made in the current session."""
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        try:
            _, full_name = get_timeseries_1()
            new_path = "/new_path"

            # check base line
            timeseries_info0 = session.get_timeseries_resource_info(path=full_name)
            assert timeseries_info0.path != new_path

            # change something
            session.update_timeseries_resource_info(path=full_name, new_path=new_path)

            # check that the change is in the session
            timeseries_info1 = session.get_timeseries_resource_info(path=full_name)
            assert timeseries_info1.path == new_path

            # rollback
            session.rollback()

            # check that changes have been discarded
            timeseries_info2 = session.get_timeseries_resource_info(path=full_name)
            assert timeseries_info2.path != new_path

        except grpc.RpcError as error:
            pytest.fail(f"Could not rollback changes: {error}")


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
def test_read_transformed_timeseries_points(
    resolution, method, timezone,
    expected_number_of_points: int):
    """Check that transformed timeseries points can be read"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = session.transform_functions(
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
                if method is Transform.Method.AVG and resolution is Timeseries.Resolution.MIN15:
                    # the original timeseries data is in hourly resolution,
                    # starts with 1 and the value is incremented with each hour up to 9
                    # here we are using 15 min resolution, so the delta between each 15 min point is 0.25
                    assert value == 1 + index * 0.25

            expected_date += delta
            index += 1


@pytest.mark.database
def test_read_transformed_timeseries_points_with_uuid():
    """
    Check that transformed timeseries read by full_name or UUID
    (both pointing to the same object) return the same data.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        # set interval where there are no NaNs to comfortably use `assert ==``
        start_time = datetime(2016, 1, 1, 5, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        # first read timeseries UUID (it is set dynamically)
        timeseries = session.read_timeseries_points(start_time=start_time,
                                                    end_time=end_time,
                                                    mesh_object_id=MeshObjectId.with_full_name(full_name))
        ts_uuid = timeseries.uuid

        reply_timeseries_full_name = session.transform_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).transform(
                Timeseries.Resolution.MIN15, Transform.Method.SUM)

        reply_timeseries_uuid = session.transform_functions(
            MeshObjectId(uuid_id=ts_uuid), start_time, end_time).transform(
                Timeseries.Resolution.MIN15, Transform.Method.SUM)

        assert reply_timeseries_full_name.is_calculation_expression_result == reply_timeseries_uuid.is_calculation_expression_result
        assert len(reply_timeseries_full_name.arrow_table) == len(reply_timeseries_uuid.arrow_table)

        for column_index in range(0, 3):
            assert reply_timeseries_full_name.arrow_table[column_index] == reply_timeseries_uuid.arrow_table[column_index]


@pytest.mark.database
def test_read_timeseries_points_without_specifying_timeseries_should_throw():
    """
    Check that expected exception is thrown when trying to
    read timeseries without specifying timeseries (by full_name, timskey or uuid_id).
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)

        with pytest.raises(TypeError, match=".*need to specify either timskey, uuid_id or full_name.*"):
            session.read_timeseries_points(start_time, end_time, MeshObjectId())


@pytest.mark.database
def test_forecast_get_all_forecasts():
    """
    Check that running forecast `get_all_forecasts`
    does not throw exception for any combination of parameters.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = session.forecast_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).get_all_forecasts()
        assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0


@pytest.mark.database
@pytest.mark.parametrize('forecast_start',
    [(None, None),
     (datetime(2016, 1, 2), datetime(2016, 1, 8))])
@pytest.mark.parametrize('available_at_timepoint',
    [None,
     datetime(2016, 1, 5, 17, 48, 11, 123456)])
def test_forecast_get_forecast(forecast_start, available_at_timepoint):
    """
    Check that running forecast `get_forecast`
    does not throw exception for any combination of parameters.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        forecast_start_min, forecast_start_max = forecast_start
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = session.forecast_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).get_forecast(
                forecast_start_min, forecast_start_max, available_at_timepoint)
        assert reply_timeseries.is_calculation_expression_result


@pytest.mark.database
def test_history_get_ts_as_of_time():
    """
    Check that running history `get_ts_as_of_time`
    does not throw exception for any combination of parameters.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        available_at_timepoint = datetime(2016, 1, 5, 17, 48, 11, 123456)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = session.history_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).get_ts_as_of_time(
                available_at_timepoint)
        assert reply_timeseries.is_calculation_expression_result


@pytest.mark.database
@pytest.mark.parametrize('max_number_of_versions_to_get',
    [1, 2, 5])
def test_history_get_ts_historical_versions(max_number_of_versions_to_get):
    """
    Check that running history `get_ts_historical_versions`
    does not throw exception for any combination of parameters.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = session.history_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).get_ts_historical_versions(
                max_number_of_versions_to_get)
        assert isinstance(reply_timeseries, List) and len(reply_timeseries) == 0


@pytest.mark.database
def test_statistical_sum():
    """
    Check that running statistical `sum`
    does not throw exception for any combination of parameters.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        reply_timeseries = session.statistical_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).sum(search_query='some_query')
        assert reply_timeseries.is_calculation_expression_result


@pytest.mark.database
def test_statistical_sum_single_timeseries():
    """
    Check that running statistical `sum_single_timeseries` works correctly.
    """

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.ROOT_PEM_CERTIFICATE)

    with connection.create_session() as session:
        start_time = datetime(2016, 1, 1, 1, 0, 0)
        end_time = datetime(2016, 1, 1, 9, 0, 0)
        _, full_name = get_timeseries_attribute_2()

        result = session.statistical_functions(
            MeshObjectId(full_name=full_name), start_time, end_time).sum_single_timeseries()
        assert isinstance(result, float) and result == 41.0


if __name__ == '__main__':
    pytest.main()
