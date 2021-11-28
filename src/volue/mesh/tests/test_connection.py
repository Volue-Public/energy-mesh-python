import uuid

from volue.mesh import Connection, Timeseries, from_proto_guid, to_proto_curve_type
import volue.mesh.tests.test_utilities.server_config as sc
from volue.mesh.proto import mesh_pb2
from volue.mesh.tests.test_utilities.utilities import get_timeseries_entry_2, get_timeseries_entry_1, \
    get_timeseries_attribute_1, get_timeseries_attribute_2
import grpc
import pytest


@pytest.mark.database
def test_read_timeseries_points():
    """Check that timeseries points can be read"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)
    with connection.create_session() as session:
        ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_entry_2()
        try:
            test_case_1 = {"start_time": start_time, "end_time": end_time, "timskey": ts_entry.timeseries_key}
            test_case_2 = {"start_time": start_time, "end_time": end_time, "uuid_id": ts_entry.id}
            test_case_3 = {"start_time": start_time, "end_time": end_time, "full_name": full_name}
            test_cases = [test_case_1, test_case_2, test_case_3]
            for test_case in test_cases:
                timeseries = session.read_timeseries_points(**test_case)
                assert len(timeseries) == 1
                assert timeseries[0].number_of_points == 312
        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries points: {e}")


@pytest.mark.database
def test_write_timeseries_points():
    """Check that timeseries points can be written"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)
    with connection.create_session() as session:
        ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_entry_2()
        timeseries = Timeseries(table=modified_table, start_time=start_time, end_time=end_time, full_name=full_name)
        try:
            session.write_timeseries_points(timeseries)
            session.rollback()
            # TODO: Should we try to commit and read back the data also? Kind of don't want to change the db
            # We should have gotten an error if the write did not succeed, so I think this is ok.

        except grpc.RpcError as e:
            pytest.fail(f"Could not write timeseries points {e}")


@pytest.mark.database
def test_get_timeseries_entry():
    """Check that timeseries entry data can be retreived"""

    ts_entry, full_name = get_timeseries_entry_1()
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)

    with connection.create_session() as session:
        try:
            test_case_1 = {"path": full_name}
            test_case_2 = {"uuid_id": ts_entry.id}
            test_case_3 = {"timskey": ts_entry.timeseries_key}
            test_cases = [test_case_1, test_case_2, test_case_3]
            for test_case in test_cases:
                entry = session.get_timeseries_resource_info(**test_case)
                assert from_proto_guid(entry.id) == ts_entry.id
                assert entry.timeseries_key == ts_entry.timeseries_key
                assert entry.path == ts_entry.path
                assert not entry.temporary
                assert entry.curveType.type == mesh_pb2.Curve.STAIRCASESTARTOFSTEP
                assert entry.delta_t.type == mesh_pb2.Resolution.HOUR
                assert entry.unit_of_measurement == ts_entry.unit_of_measurement

        except grpc.RpcError as e:
            pytest.fail(f"Could not read timeseries entry: {e}")


@pytest.mark.database
def test_update_timeseries_entry():
    """Check that timeseries entry data can be updated"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)

    # TODO: insert something here
    new_path = ""
    new_curve_type = ""
    new_unit_of_measurement = ""

    with connection.create_session() as session:
        try:
            ts_entry, full_name = get_timeseries_entry_1()

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
                # TODO: assert something

        except grpc.RpcError as e:
            pytest.fail(f"Could not update timeseries entry: {e}")


@pytest.mark.database
def test_read_timeseries_attribute():
    """Check that timeseries attribute data can be retreived"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)

    with connection.create_session() as session:
        try:
            # Testing attribute without an entry connected to it
            attribute_without_entry, full_path = get_timeseries_attribute_1()
            test_case_1 = {"model": attribute_without_entry.model,
                           "path": attribute_without_entry.silo + attribute_without_entry.path}
            test_case_2 = {"model": attribute_without_entry.model,
                           "uuid_id": attribute_without_entry.id}
            test_cases = [test_case_1, test_case_2]
            for test_case in test_cases:
                attribute_uuid = attribute_without_entry.id
                reply = session.get_timeseries_attribute(**test_case)
                assert reply is not None
                assert from_proto_guid(reply.id) == attribute_uuid
                assert reply.path == full_path
                assert not reply.HasField('entry')
                assert reply.local_expression == attribute_without_entry.local_expression
                assert reply.template_expression == attribute_without_entry.template_expression

            # Testing attribute with an entry connected to it
            attribute_with_entry, full_name = get_timeseries_attribute_2()
            test_case_1 = {"model": attribute_with_entry.model,
                           "path": attribute_with_entry.silo + attribute_with_entry.path}
            test_case_2 = {"model": attribute_with_entry.model,
                           "uuid_id": attribute_with_entry.id}
            test_cases = [test_case_1, test_case_2]
            for test_case in test_cases:
                reply = session.get_timeseries_attribute(**test_case)
                assert reply is not None
                assert from_proto_guid(reply.id) == attribute_with_entry.id
                assert reply.path == full_name
                assert reply.local_expression == attribute_with_entry.local_expression
                assert reply.template_expression == attribute_with_entry.template_expression
                assert reply.HasField('entry')
                reply_entry = reply.entry
                expected_entry = attribute_with_entry.entry
                assert from_proto_guid(reply_entry.id) == expected_entry.id
                assert reply_entry.timeseries_key == expected_entry.timeseries_key
                assert reply_entry.path == expected_entry.path
                assert reply_entry.temporary == expected_entry.temporary
                assert reply_entry.curveType.type == expected_entry.curve.value
                assert reply_entry.delta_t.type == expected_entry.resolution.value
                assert reply_entry.unit_of_measurement == expected_entry.unit_of_measurement
        except grpc.RpcError as e:
            pytest.fail(f"Could not get timeseries attribute {e}")


@pytest.mark.database
def test_update_timeseries_attribute():
    """Check that timeseries attribute data can be updated"""

    ts_attribute, full_name = get_timeseries_attribute_1()
    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)

    # TODO: insert something here
    new_local_expression = "something"
    ts_entry, _ = get_timeseries_entry_1()
    new_timeseries_entry_id = None  # mesh_pb2.TimeseriesEntryId(timeseries_key=ts_entry.timeseries_key)

    with connection.create_session() as session:
        try:
            test_ids = [{"path": full_name}, {"uuid_id": ts_attribute.id}]
            test_new_local_expression = {"new_local_expression": new_local_expression}
            test_new_timeseries_entry_id = {"new_timeseries_entry_id": new_timeseries_entry_id}
            test_cases = []
            for test_id in test_ids:
                test_cases.extend(
                    [{**test_id, **test_new_local_expression},
                     {**test_id, **test_new_timeseries_entry_id},
                     {**test_id, **test_new_local_expression, **test_new_timeseries_entry_id}]
                )
            for test_case in test_cases:
                session.update_timeseries_attribute(**test_case)
                # TODO: assert something

        except grpc.RpcError as e:
            pytest.fail(f"Could not update timeseries attribute: {e}")


@pytest.mark.database
def test_search_timeseries_attribute():
    """Check that timeseries attribute data can be searched for"""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)

    ts_attribute, full_name = get_timeseries_attribute_2()

    query = "{*}.LastAuctionAvailable"
    start_object_path = "Mesh.has_Market/Markets.has_EnergyMarkets/IT_ElSpot"
    start_object_guid = uuid.UUID("0e9ec8da-31b6-4aec-a369-1ccb95e56df2")

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
                assert len(reply) == 1
                for attribute in reply:
                    assert from_proto_guid(attribute.id) == ts_attribute.id
                    assert attribute.path == ts_attribute.silo+ts_attribute.path
                    assert attribute.local_expression == ts_attribute.local_expression
                    assert attribute.template_expression == ts_attribute.template_expression
                    assert attribute.HasField('entry')
                    entry = attribute.entry
                    assert from_proto_guid(entry.id) == ts_attribute.entry.id
                    assert entry.timeseries_key == ts_attribute.entry.timeseries_key
                    assert entry.path == ts_attribute.entry.path
                    assert entry.temporary == ts_attribute.entry.temporary
                    assert entry.curveType == to_proto_curve_type(ts_attribute.entry.curve)
                    assert entry.delta_t.type == ts_attribute.entry.resolution.value
                    assert entry.unit_of_measurement == ts_attribute.entry.unit_of_measurement
        except grpc.RpcError as e:
            pytest.fail(f"Could not update timeseries attribute: {e}")


if __name__ == '__main__':
    pytest.main()
