"""
Functionality for working with time series.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import pyarrow as pa


class Timeseries:
    """Represents a Mesh time series.

    Contains an arrow table with a schema of 3 fields (utc_time, flags, value.)
    Utc_time is the timestamps of the points (milliseconds since UNIX epoch 1970-01-01)
    Flags
    Value is the actual data for the given timestamp.

    See Also:
        :doc:`timeseries`
    """

    class Curve(Enum):
        """
        A curve type of a time series.
        It specifies how the values are laid out relative to each other.

        Args:
            UNKNOWN:
            STAIRCASESTARTOFSTEP:
            PIECEWISELINEAR:
            STAIRCASE:
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
            UNSPECIFIED:
            BREAKPOINT:
            MIN15:
            HOUR:
            DAY:
            WEEK:
            MONTH:
            YEAR:
        """

        UNSPECIFIED = 0
        BREAKPOINT = 1
        MIN15 = 2
        HOUR = 3
        DAY = 4
        WEEK = 5
        MONTH = 6
        YEAR = 7

    class PointFlags(Enum):
        """
        Information about certain action that has been performed on the values
        and the state. It is 32 bit flag setting the status for the point. Enum
        values could be used in combination (logical "OR"), e.g.:
        flag = MISSING | SUSPECT

        There are more options than the ones exposed here.

        Default is OK = 0.

        Args:
            OK: Default value, in most cases it should be used when writing
                new points with correct new values.
            NOT_OK:
            MISSING: Point value is missing, e.g: when reading physical time
                series in an interval where the time series has no values or
                reading calculation time series where all calculation
                components are missing values for the given interval.
            SUSPECT: Point value is suspected, e.g. when reading a calculation
                time series in an interval where at least one component (like
                physical time series points) is missing values. If all
                calculation components are missing values then a MISSING flag
                is set.
        """

        OK = 0
        NOT_OK = 0x40000000
        MISSING = 0x04000000
        SUSPECT = 0x02000000

    schema = pa.schema(
        [
            pa.field("utc_time", pa.timestamp("ms")),
            pa.field("flags", pa.uint32()),
            pa.field("value", pa.float64()),
        ]
    )  # The pyarrow schema used for time series points.

    def __init__(
        self,
        table: pa.Table = None,
        resolution: Optional[Resolution] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        timskey: Optional[int] = None,
        uuid_id: Optional[uuid.UUID] = None,
        full_name: Optional[str] = None,
    ):
        """A representation of a time series.
        If `start_time` and `end_time` are not provided explicitly they will be taken from PyArrow `table`.
        Providing broader time interval (`start_time` and `end_time`) could be used when writing new time series points,
        then all existing time series points within the time interval that are not covered by new time series points will be removed.
        E.g. `start_time` is set to May 1st, `end_time` is set to May 3rd and PyArrow table has points defined only for May 2nd,
        then all old points on May 1st and 3rd will be removed and new points will be set for May 2nd.

        For information about `datetime` arguments and time zones refer to :ref:`mesh_client:Date times and time zones`.

        Args:
            table: The arrow table containing the timestamps, flags and values.
            resolution: The resolution of the time series.
            start_time: The start date and time of the time series interval.
            end_time: The end date and time of the time series interval.
            timskey: Integer that only applies to a specific physical or virtual time series.
            uuid_id: Universal Unique Identifier for Mesh objects.
            full_name: Path in the :ref:`Mesh model <mesh_model>`.
              See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.

        Raises:
            TypeError: Error message raised if PyArrow table schema is invalid.
        """
        self.full_name = full_name
        self.uuid = uuid_id
        self.timskey = timskey
        self.arrow_table = table
        self.resolution = resolution

        if self.arrow_table and self.arrow_table.schema != Timeseries.schema:
            raise TypeError("invalid PyArrow table schema")

        # setting start and end time should only take effect when writing time series
        if start_time is None:
            if self.arrow_table and self.arrow_table.num_rows > 0:
                self.start_time = self.arrow_table["utc_time"][0].as_py()
        else:
            self.start_time = start_time

        if end_time is None:
            if self.arrow_table and self.arrow_table.num_rows > 0:
                # end time must be greater than last time point in PyArrow table
                self.end_time = self.arrow_table["utc_time"][-1].as_py() + timedelta(
                    seconds=1
                )
        else:
            self.end_time = end_time

    @property
    def number_of_points(self) -> int:
        """
        Number of points inside the time series.

        Returns:
            The number of points in the time series
        """
        return 0 if self.arrow_table is None else self.arrow_table.num_rows

    @property
    def is_calculation_expression_result(self) -> bool:
        """
        Checks if a time series is a calculated or a physical or virtual time series.

        Note:
            If time series does not have timskey, uuid and full_name set, then it is an ad-hoc calculation expression result (like e.g.: timeseries transformations). Refer to documentation 'Concepts' for more information.

        Returns:
            True if it is a calculated time series
        """
        return self.timskey is None and self.uuid is None and self.full_name is None
