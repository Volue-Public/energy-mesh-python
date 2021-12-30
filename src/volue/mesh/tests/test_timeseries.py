from volue.mesh._common import *
from volue.mesh import Timeseries, to_proto_guid
from volue.mesh.proto import mesh_pb2
from volue.mesh.proto.mesh_pb2 import WriteTimeseriesRequest
from datetime import datetime
import pyarrow as pa
import uuid
import pytest


@pytest.mark.unittest
def test_can_create_empty_timeserie():
    """Check that an empty timeserie can be created."""
    ts = Timeseries()
    assert ts is None


@pytest.mark.unittest
def test_can_create_timeserie_from_existing_data():
    """Check that a timeserie can be created from existing data."""
    arrays = [pa.array(['one', 'two', 'three', 'four', 'five']), pa.array([1, 2, 3, 4, 5]), pa.array([6, 7, 8, 9, 10])]
    table = pa.Table.from_arrays(arrays, names=["name", "first_list", "second_list"])
    ts = Timeseries(table)
    assert ts.number_of_points == 5


@pytest.mark.unittest
def test_can_serialize_and_deserialize_write_timeserie_request():
    """Check that timeseries can be de-/serialized."""

    start = datetime(year=2013, month=7, day=25, hour=0, minute=0, second=0)  # 25/07/2013 00:00:00
    end = datetime(year=2016, month=12, day=25, hour=0, minute=0, second=0)  # 25/12/2016 00:00:00

    arrays = [
        pa.array([1462060800000, 1462064400000, 1462068000000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 0.0, 0.0])]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)

    original_timeseries = Timeseries(table=table,
                                     resolution=mesh_pb2.Resolution(type=mesh_pb2.Resolution.HOUR),
                                     start_time=start, end_time=end,
                                     timskey=201503,
                                     uuid_id=uuid.UUID("3f1afdd7-5f7e-45f9-824f-a7adc09cff8e"),
                                     full_name="Resource/Wind Power/WindPower/WPModel/WindProdForec(0)")

    original_proto_timeserie = to_proto_timeseries(original_timeseries)
    session_id_original = to_proto_guid(uuid.UUID("3f1afdd7-1111-45f9-824f-a7adc09cff8e"))

    original_reply = WriteTimeseriesRequest(
        session_id=session_id_original,
        object_id=to_proto_object_id(original_timeseries),
        timeseries=original_proto_timeserie
    )

    binary_data = original_reply.SerializeToString()
    assert binary_data is not None

    reply = WriteTimeseriesRequest()
    reply.ParseFromString(binary_data)
    assert original_reply == reply
    assert session_id_original == reply.session_id
    assert to_proto_object_id(original_timeseries) == reply.object_id
    assert original_proto_timeserie == reply.timeseries

    reader = pa.ipc.open_stream(reply.timeseries.data)
    table = reader.read_all()
    assert original_timeseries.arrow_table == table
    assert original_timeseries.arrow_table[0] == table[0]
    assert original_timeseries.arrow_table[1] == table[1]
    assert original_timeseries.arrow_table[2] == table[2]

if __name__ == '__main__':
    pytest.main()
