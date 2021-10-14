import pyarrow as pa
from datetime import datetime
from volue.mesh.proto.mesh_pb2 import Resolution as ProtoResolution
from volue.mesh.proto.mesh_pb2 import Timeseries as ProtoTimeseries
from volue.mesh.proto.mesh_pb2 import ReadTimeseriesResponse as ProtoReadTimeseriesResponse
from volue.mesh import datetime_to_protobuf_utcinterval

class Timeseries:
    """Represents a mesh timeserie.

    Contains a arrow table with a schema of 3 fields (utc_time, flags, value.)
    Utc_time is ??? <TODO>
    Flags are ??? <TODO>
    Value is the actual data for the given timestamp.
    """

    schema = pa.schema([
        pa.field('utc_time', pa.uint64()),
        pa.field('flags', pa.uint32()),
        pa.field('value', pa.float64()),
    ])  # The pyarrow schema used for timeseries points. TODO how to get this into documentation?

    def __init__(self, table=None, resolution=ProtoResolution(type=ProtoResolution.HOUR)):
        """ """
        self.arrow_table = table
        self.resolution = resolution

    @property
    def number_of_points(self):
        """Number of point inside the time series"""
        return 0 if self.arrow_table is None else self.arrow_table.num_rows

    def to_proto_timeseries(self, object_id, start_time: datetime, end_time: datetime) -> ProtoTimeseries:
        """
        Args:
            start_time:
            end_time:
        """
        stream = pa.BufferOutputStream()

        writer = pa.ipc.RecordBatchStreamWriter(
            sink=stream,
            schema=self.arrow_table.schema
        )
        writer.write_table(self.arrow_table)
        buffer = stream.getvalue()

        ts = ProtoTimeseries(
            object_id=object_id,
            resolution=self.resolution,
            interval=datetime_to_protobuf_utcinterval(start_time=start_time, end_time=end_time),
            data=buffer.to_pybytes()
        )

        return ts

    @staticmethod
    def _read_timeseries_reply(reply: ProtoReadTimeseriesResponse):
        """ """
        for timeserie in reply.timeseries:
            reader = pa.ipc.open_stream(timeserie.data)
            table = reader.read_all()
            yield Timeseries(table, timeserie.resolution)
