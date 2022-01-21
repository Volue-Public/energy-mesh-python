import uuid

import pyarrow
import pyarrow as pa
from datetime import datetime
from volue.mesh.proto import mesh_pb2
from enum import Enum


# TODO: Add wrapper structure for TimeseriesEntry info
# TODO: Add wrapper structure for TimeseriesAttribute info
# TODO: Add wrapper for grpc.RpcError -> _error.py with defined errors???
# TODO: clean up interface to not expose grpc or protobuf structures

class Timeseries:

    class Curve(Enum):
        UNKNOWN = 0
        STAIRCASESTARTOFSTEP = 1
        PIECEWISELINEAR = 2
        STAIRCASE = 3

    class Resolution(Enum):
        BREAKPOINT = 0
        MIN15 = 1
        HOUR = 2
        DAY = 3
        WEEK = 4
        MONTH = 5
        YEAR = 6

    class PointFlags(Enum):
        OK = 0
        MISSING = 0x04000000
        NOT_OK = 0x40000000

    """Represents a mesh timeserie.

    Contains an arrow table with a schema of 3 fields (utc_time, flags, value.)
    Utc_time is the timestamps of the points (milliseconds since UNIX epoch 1970-01-01)
    Flags
    Value is the actual data for the given timestamp.
    """

    schema = pa.schema([
        pa.field('utc_time', pa.timestamp('ms')),
        pa.field('flags', pa.uint32()),
        pa.field('value', pa.float64()),
    ])  # The pyarrow schema used for timeseries points.

    def __init__(self,
                 table: pyarrow.Table = None,
                 # TODO change this to: Timeseries.Resolution
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

    @property
    def is_calculation_expression_result(self) -> bool:
        """
        If timeseries does not have timskey, uuid or full_name set then it is a
        calculation expression result (like e.g.: timeseries transformations).
        Refer to documentation 'Concepts' for more information.
        """
        return self.timskey is None and self.uuid is None and self.full_name is None
