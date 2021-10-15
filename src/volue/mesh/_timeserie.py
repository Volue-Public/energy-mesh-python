import uuid

import pyarrow
import pyarrow as pa
from datetime import datetime

from volue.mesh.proto import mesh_pb2
from volue.mesh import datetime_to_protobuf_utcinterval, uuid_to_guid


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

    def __init__(self,
                 table: pyarrow.Table = None,
                 resolution: mesh_pb2.Resolution = None,
                 start_time: datetime = None,
                 end_time: datetime = None,
                 timskey: int = None,
                 the_uuid: uuid = None,
                 full_name: str = None
                 ):
        """ """
        self.full_name = full_name
        self.uuid = the_uuid
        self.timskey = timskey
        self.end_time = end_time
        self.start_time = start_time
        self.arrow_table = table
        self.resolution = resolution

    @property
    def number_of_points(self) -> int:
        """Number of point inside the timeseries"""
        return 0 if self.arrow_table is None else self.arrow_table.num_rows

    def to_proto_object_id(self) -> mesh_pb2.ObjectId:
        """ """
        return mesh_pb2.ObjectId(
            timskey=self.timskey,
            guid=uuid_to_guid(self.uuid),
            full_name=self.full_name
        )

    def to_proto_timeseries(self) -> mesh_pb2.Timeseries:
        """ """
        stream = pa.BufferOutputStream()

        writer = pa.ipc.RecordBatchStreamWriter(
            sink=stream,
            schema=self.arrow_table.schema
        )

        writer.write_table(self.arrow_table)
        buffer = stream.getvalue()

        proto_timeserie = mesh_pb2.Timeseries(
            object_id=self.to_proto_object_id(),
            resolution=self.resolution,
            interval=datetime_to_protobuf_utcinterval(start_time=self.start_time, end_time=self.end_time),
            data=buffer.to_pybytes()
        )

        return proto_timeserie

    @staticmethod
    def _read_timeseries_reply(reply: mesh_pb2.ReadTimeseriesResponse):
        """Converts a timeseries reply into a Timeseries """
        timeseries = []
        for timeserie in reply.timeseries:
            resolution = timeserie.resolution
            object_id = timeserie.object_id
            interval = timeserie.interval
            reader = pa.ipc.open_stream(timeserie.data)
            table = reader.read_all()
            ts = Timeseries(table, resolution,
                          interval.start_time, interval.end_time,
                          object_id.timskey, object_id.guid, object_id.full_name)
            timeseries.append(ts)
        return timeseries
