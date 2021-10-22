import uuid

import pyarrow
import pyarrow as pa
from datetime import datetime
from volue.mesh.proto import mesh_pb2


class Timeseries:
    """Represents a mesh timeserie.

    Contains an arrow table with a schema of 3 fields (utc_time, flags, value.)
    Utc_time is the timestamps of the points.
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
                 uuid_id: uuid = None,
                 full_name: str = None
                 ):
        """

        Args:
            table:
            resolution:
            start_time:
            end_time:
            timskey:
            uuid_id:
            full_name:
        """
        self.full_name = full_name
        self.uuid = uuid_id
        self.timskey = timskey
        self.end_time = end_time
        self.start_time = start_time
        self.arrow_table = table
        self.resolution = resolution

    @property
    def number_of_points(self) -> int:
        """Number of points inside the timeseries"""
        return 0 if self.arrow_table is None else self.arrow_table.num_rows

