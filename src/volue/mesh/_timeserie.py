import pyarrow as pa
from volue.mesh.proto import mesh_pb2


class Timeseries:
    """Represents a mesh timeserie.

    Contains a arrow table with a schema of 3 fields (utc_time, flags, value.)
    Utc_time is ??? <TODO>
    Flags are ??? <TODO>
    Value is the actual data for the given timestamp.
    """

    def __init__(self, table=None, resolution=mesh_pb2.Resolution(type=mesh_pb2.Resolution.HOUR)):
        """ """
        fields = [
            pa.field('utc_time', pa.uint64()),
            pa.field('flags', pa.uint32()),
            pa.field('value', pa.float64()),  # aka double
        ]
        schema = pa.schema(fields)
        if table is None:
            self.arrow_table = schema.empty_table()
        else:
            self.arrow_table = table
        self.resolution = resolution

    @property
    def number_of_points(self):
        """Number of point inside the time series"""
        return 0 if self.arrow_table is None else self.arrow_table.num_rows

    def to_proto_timeseries(self, object_id, interval) -> mesh_pb2.Timeseries:
        """ """
        stream = pa.BufferOutputStream()

        writer = pa.ipc.RecordBatchStreamWriter(
            sink=stream,
            schema=self.arrow_table.schema
        )
        writer.write_table(self.arrow_table)
        buffer = stream.getvalue()

        ts = mesh_pb2.Timeseries(
            object_id=object_id,
            resolution=self.resolution,
            interval=interval,
            data=buffer.to_pybytes()
        )

        return ts

    @staticmethod
    def _read_timeseries_reply(reply: mesh_pb2.ReadTimeseriesResponse):
        """ """
        timeseries = []
        for timeserie in reply.timeseries:
            reader = pa.ipc.open_stream(timeserie.data)
            table = reader.read_all()
            yield Timeseries(table, timeserie.resolution)
