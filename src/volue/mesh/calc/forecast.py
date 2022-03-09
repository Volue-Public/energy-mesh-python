"""
Mesh calculation forecast functions.
"""

from abc import ABC, abstractmethod
import datetime
from typing import List

from volue.mesh import Timeseries
from volue.mesh.calc.common import _Calculation, Timezone, _convert_datetime_to_mesh_calc_format, \
    _parse_timeseries_list_response, _parse_single_timeseries_response


class _ForecastFunctionsBase(_Calculation, ABC):

    def _get_all_forecasts_expression(self,
                                      search_query: str) -> str:
        expression = f"## = @GetAllForecasts(@t("
        if search_query:
            expression = f"{expression}'{search_query}'"
        expression = f"{expression}))\n"
        return expression

    def _get_forecast_expression(self,
                                 forecast_start_min: datetime,
                                 forecast_start_max: datetime,
                                 available_at_timepoint: datetime,
                                 timezone: Timezone,
                                 search_query: str) -> str:

        if forecast_start_min is not None and forecast_start_max is None:
            raise TypeError(
                "parameter `forecast_start_min` is provided, it requires providing also `forecast_start_max`")

        if forecast_start_min is None and forecast_start_max is not None:
            raise TypeError(
                "parameter `forecast_start_max` is provided, it requires providing also `forecast_start_min`")

        expression = f"## = @GetForecast(@t("
        if search_query:
            expression = f"{expression}'{search_query}'"
        expression = f"{expression})"

        if forecast_start_min is not None:
            converted_forecast_start_min = _convert_datetime_to_mesh_calc_format(forecast_start_min, timezone)
            expression = f"{expression},'{converted_forecast_start_min}'"

        if forecast_start_max is not None:
            converted_forecast_start_max = _convert_datetime_to_mesh_calc_format(forecast_start_max, timezone)
            expression = f"{expression},'{converted_forecast_start_max}'"

        if available_at_timepoint is not None:
            converted_available_at_timepoint = _convert_datetime_to_mesh_calc_format(available_at_timepoint, timezone)
            expression = f"{expression},'{converted_available_at_timepoint}'"
        expression = f"{expression})\n"

        return expression

    # Interface
    # abstractmethod does not take into account if method is async or not

    @abstractmethod
    def get_all_forecasts(self,
                          search_query: str = None) -> List[Timeseries]:
        """
        Returns an array of forecast time series with values within the relevant period.
        Values in forecast series outside the period are not included.
        The function returns an empty array if no forecast time series have values within the relevant period.

        The resulting objects from the `search_query` will be used in the `get_all_forecasts` function,
        if `search_query` is not set the `relative_to` object will be used.
        """
        pass

    @abstractmethod
    def get_forecast(self,
                     forecast_start_min: datetime = None,
                     forecast_start_max: datetime = None,
                     available_at_timepoint: datetime = None,
                     timezone: Timezone = None,
                     search_query: str = None) -> Timeseries:
        """
        The function can take `available_at_timepoint` without specifying `forecast_start_min` and `forecast_start_min` to find a forecast
        available at the timepoint defined in `available_at_timepoint` (y-axis) within the period requested in `forecast_functions`
        interval parameters (`start_time` and `end_time`).

        The function can take `forecast_start_min` and `forecast_start_min` with or without specifying `available_at_timepoint` to find
        the relevant forecast instead of using the start of the requested period (defined in `forecast_functions`).
        It requires that the forecast series' start is less than or equal to `forecast_start_max` and larger than `forecast_start_min`.
        If no forecast series has its start time within the given interval, the function returns a timeseries with NaN.

        The resulting objects from the `search_query` will be used in the `get_forecast` function,
        if `search_query` is not set the `relative_to` object will be used.
        """
        pass


class ForecastFunctions(_ForecastFunctionsBase):

    def get_all_forecasts(self,
                          search_query: str = None) -> List[Timeseries]:
        expression = super()._get_all_forecasts_expression(search_query)
        response = super().run(expression)
        return _parse_timeseries_list_response(response)

    def get_forecast(self,
                     forecast_start_min: datetime = None,
                     forecast_start_max: datetime = None,
                     available_at_timepoint: datetime = None,
                     timezone: Timezone = None,
                     search_query: str = None) -> Timeseries:
        expression = super()._get_forecast_expression(forecast_start_min, forecast_start_max, available_at_timepoint,
                                                      timezone, search_query)
        response = super().run(expression)
        return _parse_single_timeseries_response(response)


class ForecastFunctionsAsync(_ForecastFunctionsBase):

    async def get_all_forecasts(self,
                                search_query: str = None) -> List[Timeseries]:
        expression = super()._get_all_forecasts_expression(search_query)
        response = await super().run_async(expression)
        return _parse_timeseries_list_response(response)

    async def get_forecast(self,
                           forecast_start_min: datetime = None,
                           forecast_start_max: datetime = None,
                           available_at_timepoint: datetime = None,
                           timezone: Timezone = None,
                           search_query: str = None) -> Timeseries:
        expression = super()._get_forecast_expression(forecast_start_min, forecast_start_max, available_at_timepoint,
                                                      timezone, search_query)
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)
