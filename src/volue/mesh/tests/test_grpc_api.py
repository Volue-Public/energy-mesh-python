from volue.mesh.tests.test_utilities.utilities import get_timeseries_entry_2
from volue.mesh._common import *
from volue.mesh import Connection, to_proto_guid
from volue.mesh.proto import mesh_pb2
import volue.mesh.tests.test_utilities.server_config as sc
from google.protobuf.pyext._message import RepeatedCompositeContainer
import grpc
import pytest

@pytest.mark.database
def test_read_timeseries_response_is_valid():
    """Check that the read timeseries response is as expected."""

    connection = Connection(sc.DefaultServerConfig.ADDRESS, sc.DefaultServerConfig.PORT,
                            sc.DefaultServerConfig.SECURE_CONNECTION)

    with connection.create_session() as session:
        ts_entry, start_time, end_time, modified_table, full_name = get_timeseries_entry_2()
        try:
            reply = session.mesh_service.ReadTimeseries(
                mesh_pb2.ReadTimeseriesRequest(
                    session_id=to_proto_guid(session.session_id),
                    object_id=mesh_pb2.ObjectId(timskey=ts_entry.timeseries_key, guid=to_proto_guid(ts_entry.id), full_name=full_name),
                    interval=to_protobuf_utcinterval(start_time, end_time)
                )
            )
        except grpc.RpcError:
            pytest.fail("Could not read timeseries points.")
        finally:
            assert isinstance(reply, mesh_pb2.ReadTimeseriesResponse)
            assert isinstance(reply.timeseries, RepeatedCompositeContainer)
            assert len(reply.timeseries) == 1
            assert isinstance(reply.timeseries[0].data, bytes)
            assert len(reply.timeseries[0].data) == 6712

            reader = pa.ipc.open_stream(reply.timeseries[0].data)
            assert reader.schema == Timeseries.schema

            table = reader.read_all()
            assert len(table) == 312
            assert table[0][0].as_py() == start_time.date()  # utc_time
            assert table[1][0].as_py() == 0                  # flags
            assert table[2][0].as_py() == 0.0                # value


if __name__ == '__main__':
    pytest.main()
