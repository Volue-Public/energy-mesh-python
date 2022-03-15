"""
Mesh calculation history functions.
"""

from abc import ABC, abstractmethod
import datetime
from typing import List

from volue.mesh import Timeseries
from volue.mesh.calc.common import _Calculation, _convert_datetime_to_mesh_calc_format, \
    _parse_timeseries_list_response, _parse_single_timeseries_response


class _HistoryFunctionsBase(_Calculation, ABC):

    def _get_ts_as_of_time_expression(self,
                                      available_at_timepoint: datetime,
                                      search_query: str) -> str:
        converted_available_at_timepoint = _convert_datetime_to_mesh_calc_format(available_at_timepoint)
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
    def get_ts_as_of_time(self,
                          available_at_timepoint: datetime,
                          search_query: str = None) -> Timeseries:
        """
        Finds values and status for a timeseries at a given historical time `available_at_timepoint`.
        If `available_at_timepoint` is a time zone naive `datetime` object then it is treated as UTC.
        Returns a time series.

        The resulting objects from the `search_query` will be used in the `get_ts_as_of_time` function,
        if `search_query` is not set the `relative_to` object will be used.
        """
        pass

    @abstractmethod
    def get_ts_historical_versions(self,
                                   max_number_of_versions_to_get: int,
                                   search_query: str = None) -> List[Timeseries]:
        """
        Returns an array of a given number of versions of a time series.

        The resulting objects from the `search_query` will be used in the `get_ts_historical_versions` function,
        if `search_query` is not set the `relative_to` object will be used.
        """
        pass


class HistoryFunctions(_HistoryFunctionsBase):

    def get_ts_as_of_time(self,
                          available_at_timepoint: datetime,
                          search_query: str = None) -> Timeseries:
        expression = super()._get_ts_as_of_time_expression(available_at_timepoint, search_query)
        response = super().run(expression)
        return _parse_single_timeseries_response(response)

    def get_ts_historical_versions(self,
                                   max_number_of_versions_to_get: int,
                                   search_query: str = None) -> List[Timeseries]:
        expression = super()._get_ts_historical_versions_expression(max_number_of_versions_to_get, search_query)
        response = super().run(expression)
        return _parse_timeseries_list_response(response)


class HistoryFunctionsAsync(_HistoryFunctionsBase):

    async def get_ts_as_of_time(self,
                                available_at_timepoint: datetime,
                                search_query: str = None) -> Timeseries:
        expression = super()._get_ts_as_of_time_expression(available_at_timepoint, search_query)
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)

    async def get_ts_historical_versions(self,
                                         max_number_of_versions_to_get: int,
                                         search_query: str = None) -> List[Timeseries]:
        expression = super()._get_ts_historical_versions_expression(max_number_of_versions_to_get, search_query)
        response = await super().run_async(expression)
        return _parse_timeseries_list_response(response)
