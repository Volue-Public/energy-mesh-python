import pyarrow as pa
from volue.mesh.proto import mesh_pb2

class Timeserie:

    def __init__(self, table = None, resolution = mesh_pb2.Resolution(type = mesh_pb2.Resolution.HOUR)):
        fields = [
            pa.field('ticks', pa.uint64()),
            pa.field('flags', pa.uint32()),
            pa.field('value', pa.float64()),
        ]
        schema = pa.schema(fields)
        if table == None:
            self.arrow_table = schema.empty_table()
        else:
            self.arrow_table = table
        self.resolution = resolution

    def add_point(self, ticks, flags, value) -> None:
        table = pa.Table.from_arrays(([ticks], [flags], [value]),
            schema=self.arrow_table.schema
        )
        self.arrow_table = pa.concat_tables([self.arrow_table, table])

    @property
    def number_of_points(self):
        return 0 if self.arrow_table == None else self.arrow_table.num_rows

    def to_proto_timeseries(self, object_id, interval) -> mesh_pb2.Timeseries:
        stream = pa.BufferOutputStream()

        writer = pa.ipc.RecordBatchStreamWriter(
            sink=stream,
            schema=self.arrow_table.schema
        )
        writer.write_table(self.arrow_table)
        buffer = stream.getvalue()

        ts = mesh_pb2.Timeseries(
            object_id = object_id,
            resolution = self.resolution,
            interval = interval,
            data = buffer.to_pybytes()
        )

        return ts

    @staticmethod
    def read_timeseries_reply(reply: mesh_pb2.ReadTimeseriesResponse):
        timeseries = []
        for timeserie in reply.timeseries:
            reader = pa.ipc.open_stream(timeserie.data)
            table = reader.read_all()
            yield Timeserie(table, timeserie.resolution)

