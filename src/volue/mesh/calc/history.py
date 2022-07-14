"""
Mesh calculation history functions.
*************************************

For more information see :ref:`mesh_functions:history`.

"""

import datetime
from abc import ABC, abstractmethod
from typing import List

from volue.mesh import Timeseries
from volue.mesh.calc.common import (
    _Calculation,
    _convert_datetime_to_mesh_calc_format,
    _parse_single_timeseries_response,
    _parse_timeseries_list_response,
)


class _HistoryFunctionsBase(_Calculation, ABC):
    """Base class for all history function classes"""

    def _get_ts_as_of_time_expression(self,
                                      available_at_timepoint: datetime,
                                      search_query: str) -> str:
        """
        Create an expression for `get_ts_as_of_time`.

        Args:
            available_at_timepoint: Is valid at the given timestamp.
            search_query: A search formulated using the :doc:`Mesh search language <mesh_search>`.

        Returns:
            Mesh calculation expression.
        """
        converted_available_at_timepoint = _convert_datetime_to_mesh_calc_format(available_at_timepoint)
        expression = f"## = @GetTsAsOfTime(@t("
        if search_query:
            expression = f"{expression}'{search_query}'"
        expression = f"{expression}),'{converted_available_at_timepoint}')\n"
        return expression

    def _get_ts_historical_versions_expression(self,
                                               max_number_of_versions_to_get: int,
                                               search_query: str) -> str:
        """
        Creates an expression for `get_ts_historical_versions`.

        Args:
            max_number_of_versions_to_get: Maximum number of time series to return.
            search_query: A search formulated using the :doc:`Mesh search language <mesh_search>`.

        Returns:
            Mesh calculation expression.
        """
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
        Finds values and status for a time series at a given historical time `available_at_timepoint`.

        Note:
            * The resulting objects from the `search_query` will be used in the `get_ts_as_of_time` function, if `search_query` is not set the `relative_to` object will be used.
            * If the historical time is earlier than the first write to the series (in the relevant period) then the function returns NaN values.

        Args:
            available_at_timepoint: Is valid at the given timestamp.
            search_query: A search formulated using the :doc:`Mesh search language <mesh_search>`.

        For information about `datetime` arguments and time zones refer to :ref:`mesh_client:Date times and time zones`.

        Returns:
             A time series with historical values.
        """
        pass

    @abstractmethod
    def get_ts_historical_versions(self,
                                   max_number_of_versions_to_get: int,
                                   search_query: str = None) -> List[Timeseries]:
        """
        Requests an array of a given number of versions of a time series.

        Examples:

            GetTsHistoricalVersions(ts,1) returns the last change made, i.e. the latest historical version that is different from the current time series.

            GetTsHistoricalVersions(ts,3) returns the three last changes. The first series displays the state before the last change, the second displays the state before the second last change, etc.


        Args:
            max_number_of_versions_to_get: Maximum number of time series to return.
            search_query: A search formulated using the :doc:`Mesh search language <mesh_search>`.

        Note:
            The resulting objects from the `search_query` will be used in the `get_ts_historical_versions` function, if `search_query` is not set the `relative_to` object will be used.

        Returns:
            An array of time series with historical values.
        """
        pass


class HistoryFunctions(_HistoryFunctionsBase):
    """Class for history functions that should be run synchronously"""
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
    """Class for history functions that should be run asynchronously"""
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
