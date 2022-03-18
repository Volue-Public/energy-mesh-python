"""
Mesh calculation transformation functions.
*******************************************

For more information see :ref:`mesh_functions:transform`.

"""

from abc import ABC, abstractmethod
from enum import Enum

from volue.mesh import Timeseries
from volue.mesh.calc.common import _Calculation, Timezone, _parse_single_timeseries_response


class Method(Enum):
    """
    Methods used for transforming a time series from one resolution to another.

    Args:
        SUM: The sum of the values included in the base for this value. Does not consider how long the values are valid, i.e. a break point series with two values in the current interval that will give the sum of these two values.
        SUMI: Integral based sum with resolution second. Calculates the sum of value multiplied with number of seconds each value is valid. Value equal 1 at the start of the day will give 86400 as day value if the base is one break point series and 3600 if this is an hour series with only one value on first hour.
        AVG: For fixed interval series. Sum of all values in accumulation period divided by number of values in the accumulation period (24 for hour series that is transformed to day series). For break point series: Mean value of the values included in the base for this value. Does not consider how long the values are valid, i.e. a break point series with two values in the current interval that will give the mean value of these two values.
        AVGI: Integral based mean value, i.e. considers how much of the accumulation period that a given value is valid (to next value that can be NaN for a fixed interval series). This value is presented as mean value in the summary part of the presentation in Table.
        FIRST: First value in the accumulation period. For break point series this is the functional value at the start of the accumulation period, unless there exist an explicit value. Please note! For fixed interval series it is the first value not being NaN in the accumulation period.
        LAST: Last value in the accumulation period. For break point series this is the functional value at the end of the accumulation period, unless there exist an explicit value. Note! For fixed interval series it is the last value not being NaN in the accumulation period.
        MIN: Smallest value in the accumulation period.
        MAX: Largest value in the accumulation period.
    """
    SUM = 0
    SUMI = 1  # I -> weighted sum, only for breakpoint timeseries
    AVG = 2  # equivalent to MEAN
    AVGI = 3  # I -> weighted average, only for breakpoint timeseries
    FIRST = 5
    LAST = 6
    MIN = 7
    MAX = 8


class _TransformFunctionsBase(_Calculation, ABC):
    """Base class for all tranformation function classes"""

    def _transform_expression(self,
                              resolution: Timeseries.Resolution,
                              method: Method,
                              timezone: Timezone,
                              search_query: str) -> str:
        """
        Create an expression for `transform`.

        Args:
            resolution (Timeseries.Resolution): the resolution to transform to
            method (Method): what method to use for the transformation
            timezone (Timezone): timezone
            search_query (str): a search formulated using the :doc:`Mesh search language <mesh_search>`

        Returns:
            str: a `transformation` expression
        """

        if resolution is Timeseries.Resolution.BREAKPOINT:
            raise ValueError("'BREAKPOINT' resolution is unsupported for timeseries transformation")

        expression = f"## = @TRANSFORM(@t("
        if search_query:
            expression = f"{expression}'{search_query}'"
        expression = f"{expression}), '{resolution.name}', '{method.name}'"

        if timezone is not None:
            expression = f"{expression}, '{timezone.name}'"
        expression = f"{expression})\n"

        return expression

    # Interface
    # abstractmethod does not take into account if method is async or not

    @abstractmethod
    def transform(self,
                  resolution: Timeseries.Resolution,
                  method: Method,
                  timezone: Timezone = Timezone.UTC,
                  search_query: str = None) -> Timeseries:
        """
        Transforms time series from one resolution to another resolution.

        Some of target resolutions have a time zone foundation.
        Note: the `LOCAL` and `STANDARD` time zone refers to time zone of Mesh server, not the Python client.

        Example:
             `DAY` can be related to European Standard Time (UTC+1), which is different from the DAY scope in Finland (UTC+2).
             When the time zone argument to TRANSFORM is omitted, the configured standard time zone with no Daylight Saving Time enabled is used.
            You can use it to convert both ways, i.e. both from finer to coarser resolution, and the other way.
            The most common use is accumulation, i.e. transformation to coarser resolution.
            Most transformation methods are available for this latter use.

        Args:
            resolution (Timeseries.Resolution): the resolution to transform to
            method (Method): what method to use for the transformation
            timezone (Timezone): timezone
            search_query (str): a search formulated using the :doc:`Mesh search language <mesh_search>`

        Note:
            The resulting objects from the `search_query` will be used in the `transform` function, if `search_query` is not set the `relative_to` object will be used.

        Returns:
            Timeseries: a time series.
        """
        pass


class TransformFunctions(_TransformFunctionsBase):

    def transform(self,
                  resolution: Timeseries.Resolution,
                  method: Method,
                  timezone: Timezone = Timezone.UTC,
                  search_query: str = None) -> Timeseries:
        expression = super()._transform_expression(resolution, method, timezone, search_query)
        response = super().run(expression)
        return _parse_single_timeseries_response(response)


class TransformFunctionsAsync(_TransformFunctionsBase):

    async def transform(self,
                        resolution: Timeseries.Resolution,
                        method: Method,
                        timezone: Timezone = Timezone.UTC,
                        search_query: str = None) -> Timeseries:
        expression = super()._transform_expression(resolution, method, timezone, search_query)
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)
