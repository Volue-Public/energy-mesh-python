""""
Mesh calculation history functions
"""

from abc import ABC, abstractmethod
import datetime
from typing import List

from volue.mesh import Timeseries
from volue.mesh.calc.common import Calculation, Timezone


class _HistoryFunctionsBase(Calculation, ABC):

    def _get_all_forecasts_expression(self,
                                      search_query: str) -> str:
        expression = f"## = @GetAllForecasts(@t("
        if search_query:
             expression = f"{expression}'{search_query}'"
        expression = f"{expression}))\n"
        return expression

    def _get_forecast_expression(self,
                                 t0_min: datetime,
                                 t0_max: datetime,
                                 available_at_timepoint: datetime,
                                 timezone: Timezone,
                                 search_query: str) -> str:

        if t0_min is None or t0_max is None:
            raise TypeError("parameters t0_min and t0_max are required")

        expression = f"## = @GetForecast(@t("
        if search_query:
             expression = f"{expression}'{search_query}'"
        expression = f"{expression})"

        converted_t0_min = super().convert_datetime_to_mesh_calc_format(t0_min, timezone)
        expression = f"{expression},'{converted_t0_min}'"

        converted_t0_max = super().convert_datetime_to_mesh_calc_format(t0_max, timezone)
        expression = f"{expression},'{converted_t0_max}'"

        if available_at_timepoint is not None:
            converted_available_at_timepoint = super().convert_datetime_to_mesh_calc_format(available_at_timepoint, timezone)
            expression = f"{expression},'{converted_available_at_timepoint}'"
        expression = f"{expression})\n"

        return expression

    def _get_ts_as_of_time(self,
                           available_at_timepoint: datetime,
                           timezone: Timezone,
                           search_query: str) -> str:
        converted_available_at_timepoint = super().convert_datetime_to_mesh_calc_format(available_at_timepoint, timezone)
        expression = f"## = @GetTsAsOfTime(@t("
        if search_query:
             expression = f"{expression}'{search_query}'"
        expression = f"{expression}),'{converted_available_at_timepoint}')\n"
        return expression

    def _get_ts_historical_versions_expression(self,
                                               max_number_of_versions_to_get: int,
                                               search_query: str) -> str:
        expression = f"## = @GetTsHistoricalVersions(@t("
        if search_query:
             expression = f"{expression}'{search_query}'"
        expression = f"{expression}),{max_number_of_versions_to_get})\n"
        return expression


    # Interface
    # abstractmethod does not take into account if method is async or not

    @abstractmethod
    def get_all_forecasts(self,
                          search_query: str = None) -> List[Timeseries]:
        """
        Empty `seach_query` means self-reference to `relative_to`.
        """
        pass

    @abstractmethod
    def get_forecast(self,
                     t0_min: datetime,
                     t0_max: datetime,
                     available_at_timepoint: datetime = None,
                     timezone: Timezone = None,
                     search_query: str = None) -> Timeseries:
        """
        Empty `seach_query` means self-reference to `relative_to`.
        """
        pass

    @abstractmethod
    def get_ts_as_of_time(self,
                          available_at_timepoint: datetime,
                          timezone: Timezone = None,
                          search_query: str = None) -> Timeseries:
        """
        Empty `seach_query` means self-reference to `relative_to`.
        """
        pass

    @abstractmethod
    def get_ts_historical_versions(self,
                                   max_number_of_versions_to_get: int,
                                   search_query: str = None) -> List[Timeseries]:
        """
        Empty `seach_query` means self-reference to `relative_to`.
        """
        pass


class HistoryFunctions(_HistoryFunctionsBase):

    def get_all_forecasts(self,
                          search_query: str = None) -> List[Timeseries]:
        expression = super()._get_all_forecasts_expression(search_query)
        response = super().run(expression)
        return super().parse_timeseries_list_response(response)

    def get_forecast(self,
                     t0_min: datetime,
                     t0_max: datetime,
                     available_at_timepoint: datetime = None,
                     timezone: Timezone = None,
                     search_query: str = None) -> Timeseries:
        expression = super()._get_forecast_expression( t0_min, t0_max, available_at_timepoint, timezone, search_query)
        response = super().run(expression)
        return super().parse_single_timeseries_response(response)

    def get_ts_as_of_time(self,
                          available_at_timepoint: datetime,
                          timezone: Timezone = None,
                          search_query: str = None) -> Timeseries:
        expression = super()._get_ts_as_of_time(available_at_timepoint, timezone, search_query)
        response = super().run(expression)
        return super().parse_single_timeseries_response(response)

    def get_ts_historical_versions(self,
                                   max_number_of_versions_to_get: int,
                                   search_query: str = None) -> List[Timeseries]:
        expression = super()._get_ts_historical_versions_expression(max_number_of_versions_to_get, search_query)
        response = super().run(expression)
        return super().parse_timeseries_list_response(response)

class HistoryFunctionsAsync(_HistoryFunctionsBase):

    async def get_all_forecasts(self,
                                search_query: str = None) -> List[Timeseries]:
        expression = super()._get_all_forecasts_expression(search_query)
        response = await super().run_async(expression)
        return super().parse_timeseries_list_response(response)

    async def get_forecast(self,
                           t0_min: datetime,
                           t0_max: datetime,
                           available_at_timepoint: datetime = None,
                           timezone: Timezone = None,
                           search_query: str = None) -> Timeseries:
        expression = super()._get_forecast_expression(t0_min, t0_max, available_at_timepoint, timezone, search_query)
        response = await super().run_async(expression)
        return super().parse_single_timeseries_response(response)

    async def get_ts_as_of_time(self,
                                available_at_timepoint: datetime,
                                timezone: Timezone = None,
                                search_query: str = None) -> Timeseries:
        expression = super()._get_ts_as_of_time( available_at_timepoint, timezone, search_query)
        response = await super().run_async(expression)
        return super().parse_single_timeseries_response(response)

    async def get_ts_historical_versions(self,
                                         max_number_of_versions_to_get: int,
                                         search_query: str = None) -> List[Timeseries]:
        expression = super()._get_ts_historical_versions_expression(max_number_of_versions_to_get, search_query)
        response = await super().run_async(expression)
        return super().parse_timeseries_list_response(response)
