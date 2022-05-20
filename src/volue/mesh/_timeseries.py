"""
Functionality for working with time series.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
import pyarrow as pa
from volue.mesh.proto.type import resources_pb2


class Timeseries:
    """Represents a mesh timeserie.

    Contains an arrow table with a schema of 3 fields (utc_time, flags, value.)
    Utc_time is the timestamps of the points (milliseconds since UNIX epoch 1970-01-01)
    Flags
    Value is the actual data for the given timestamp.
    """

    class Curve(Enum):
        """
        A curve type of a time series.
        It specifies how the values are laid out relative to each other.

        Args:
            UNKNOWN (enum):
            STAIRCASESTARTOFSTEP (enum):
            PIECEWISELINEAR (enum):
            STAIRCASE (enum):
        """
        UNKNOWN = 0
        STAIRCASESTARTOFSTEP = 1
        PIECEWISELINEAR = 2
        STAIRCASE = 3

    class Resolution(Enum):
        """
        The resolution of values in the time series.
        It specifies the time interval between each value.

        Args:
            UNSPECIFIED (enum):
            BREAKPOINT (enum):
            MIN15 (enum):
            HOUR (enum):
            DAY (enum):
            WEEK (enum):
            MONTH (enum):
            YEAR (enum):
        """
        UNSPECIFIED = 0
        BREAKPOINT  = 1
        MIN15       = 2
        HOUR        = 3
        DAY         = 4
        WEEK        = 5
        MONTH       = 6
        YEAR        = 7

    class PointFlags(Enum):
        """
        Information about certain action that has been performed on the values and the state.

        32 bit flag setting the status for the point. There are many more options than the ones exposed here.

        Default is OK = 0.

        Args:
            OK (enum):
            MISSING (enum):
            NOT_OK (enum):
        """
        OK = 0
        MISSING = 0x04000000
        NOT_OK = 0x40000000

    schema = pa.schema([
        pa.field('utc_time', pa.timestamp('ms')),
        pa.field('flags', pa.uint32()),
        pa.field('value', pa.float64()),
    ])  # The pyarrow schema used for timeseries points.

    def __init__(self,
                 table: pa.Table = None,
                 resolution: resources_pb2.Resolution = None,
                 start_time: datetime = None,
                 end_time: datetime = None,
                 timskey: int = None,
                 uuid_id: uuid = None,
                 full_name: str = None
                 ):
        """A representation of a time series.
        If `start_time` and `end_time` are not provided explicitly they will be taken from PyArrow `table`.
        Providing broader time interval (`start_time` and `end_time`) could be used when writing new time series points,
        then all existing time series points within the time interval that are not covered by new time series points will be removed.
        E.g. `start_time` is set to May 1st, `end_time` is set to May 3rd and PyArrow table has points defined only for May 2nd,
        then all old points on May 1st and 3rd will be removed and new points will be set for May 2nd.

        For information about `datetime` arguments and time zones refer to :ref:`mesh_client:Date times and time zones`.

        Args:
            table (pa.Table): the arrow table containing the timestamps, flags and values
            resolution (resources_pb2.Resolution): the resolution of the time series
            start_time (datetime): the start date and time of the time series interval
            end_time (datetime): the end date and time of the time series interval
            timskey (int): integer that only applies to a specific raw time series
            uuid_id:  Universal Unique Identifier for Mesh objects
            full_name: path in the :ref:`Mesh object model <mesh object model>`.
              See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.

        Raises:
            TypeError:  Error message raised if PyArrow table schema is invalid
        """
        self.full_name = full_name
        self.uuid = uuid_id
        self.timskey = timskey
        self.arrow_table = table
        self.resolution = resolution

        if self.arrow_table and self.arrow_table.schema != Timeseries.schema:
            raise TypeError('invalid PyArrow table schema')

        # setting start and end time should only take effect when writing time series
        if start_time is None:
            if self.arrow_table and self.arrow_table.num_rows > 0:
                self.start_time = self.arrow_table['utc_time'][0].as_py()
        else:
            self.start_time = start_time

        if end_time is None:
            if self.arrow_table and self.arrow_table.num_rows > 0:
                # end time must be greater than last time point in PyArrow table
                self.end_time = self.arrow_table['utc_time'][-1].as_py() + timedelta(seconds=1)
        else:
            self.end_time = end_time

    @property
    def number_of_points(self) -> int:
        """
        Number of points inside the time series.

        Returns:
            int: the number of points in the time series
        """
        return 0 if self.arrow_table is None else self.arrow_table.num_rows

    @property
    def is_calculation_expression_result(self) -> bool:
        """
        Checks if a time series is a calculated or raw time series.

        Note:
            If time series does not have timskey, uuid and full_name set, then it is an ad-hoc calculation expression result (like e.g.: timeseries transformations). Refer to documentation 'Concepts' for more information.

        Returns:
            bool: true if it is a calculated time series
        """
        return self.timskey is None and self.uuid is None and self.full_name is None
