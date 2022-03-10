"""
Mesh calculation transformation functions.
The functions in this category are used to calculate time series with a different time resolution than the source.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from volue.mesh import Timeseries
from volue.mesh.calc.common import _Calculation, Timezone, _parse_single_timeseries_response

class Method(Enum):
    """
    Transformation method
    """
    SUM   = 0
    SUMI  = 1  # I -> weighted sum, only for breakpoint timeseries
    AVG   = 2  # equivalent to MEAN
    AVGI  = 3  # I -> weighted average, only for breakpoint timeseries
    FIRST = 5
    LAST  = 6
    MIN   = 7
    MAX   = 8

class _TransformFunctionsBase(_Calculation, ABC):

    def _transform_expression(self,
                              resolution: Timeseries.Resolution,
                              method: Method,
                              timezone: Timezone,
                              search_query: str) -> str:

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
                  timezone: Timezone = None,
                  search_query: str = None) -> Timeseries:
        """
        Transforms time series from one resolution to another resolution.
        Some of target resolutions have a time zone foundation.
        For example, `DAY` can be related to European Standard Time (UTC+1), which is different from the DAY scope in Finland (UTC+2).
        When the time zone argument to TRANSFORM is omitted, the configured standard time zone with no Daylight Saving Time enabled is used.

        You can use it to convert both ways, i.e. both from finer to coarser resolution, and the other way.
        The most common use is accumulation, i.e. transformation to coarser resolution.
        Most transformation methods are available for this latter use.

        Returns a time series.

        The resulting objects from the `search_query` will be used in the `transform` function,
        if `search_query` is not set the `relative_to` object will be used.
        """
        pass


class TransformFunctions(_TransformFunctionsBase):

    def transform(self,
                  resolution: Timeseries.Resolution,
                  method: Method,
                  timezone: Timezone = None,
                  search_query: str = None) -> Timeseries:
        expression = super()._transform_expression(resolution, method, timezone, search_query)
        response = super().run(expression)
        return _parse_single_timeseries_response(response)


class TransformFunctionsAsync(_TransformFunctionsBase):

    async def transform(self,
                  resolution: Timeseries.Resolution,
                  method: Method,
                  timezone: Timezone = None,
                  search_query: str = None) -> Timeseries:
        expression = super()._transform_expression(resolution, method, timezone, search_query)
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)
