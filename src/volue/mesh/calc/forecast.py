"""
Mesh calculation forecast functions
*************************************

For more information see :ref:`mesh_functions:forecast`.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from volue.mesh import Timeseries
from volue.mesh.calc.common import (
    _Calculation,
    _convert_datetime_to_mesh_calc_format,
    _parse_single_timeseries_response,
    _parse_timeseries_list_response,
)


class _ForecastFunctionsBase(_Calculation, ABC):
    """Base class for all forecast function classes."""

    def _get_all_forecasts_expression(self, search_query: Optional[str]) -> str:
        """
        Creates an expression for `get_all_forecasts` using a search query.

        Args:
            search_query: A search formulated using the :doc:`Mesh search language <mesh_search>`.

        Returns:
            Mesh calculation expression.
        """
        expression = "## = @GetAllForecasts(@t("
        if search_query:
            expression = f"{expression}'{search_query}'"
        expression = f"{expression}))\n"
        return expression

    def _get_forecast_expression(
        self,
        forecast_start_min: Optional[datetime],
        forecast_start_max: Optional[datetime],
        available_at_timepoint: Optional[datetime],
        search_query: Optional[str],
    ) -> str:
        """
        Creates an expression for `get_forecasts` using a search query.

        Args:
            forecast_start_min: Forecast must start after this time.
            forecast_start_max: Forecast must start before this time.
            available_at_timepoint: Forecast that is valid at the given timestamp.
            search_query: A search formulated using the :doc:`Mesh search language <mesh_search>`.

        Returns:
            Mesh calculation expression.
        """
        if forecast_start_min is not None and forecast_start_max is None:
            raise TypeError(
                "parameter `forecast_start_min` is provided, it requires providing also `forecast_start_max`"
            )

        if forecast_start_min is None and forecast_start_max is not None:
            raise TypeError(
                "parameter `forecast_start_max` is provided, it requires providing also `forecast_start_min`"
            )

        expression = "## = @GetForecast(@t("
        if search_query:
            expression = f"{expression}'{search_query}'"
        expression = f"{expression})"

        if forecast_start_min is not None:
            converted_forecast_start_min = _convert_datetime_to_mesh_calc_format(
                forecast_start_min
            )
            expression = f"{expression},'{converted_forecast_start_min}'"

        if forecast_start_max is not None:
            converted_forecast_start_max = _convert_datetime_to_mesh_calc_format(
                forecast_start_max
            )
            expression = f"{expression},'{converted_forecast_start_max}'"

        if available_at_timepoint is not None:
            converted_available_at_timepoint = _convert_datetime_to_mesh_calc_format(
                available_at_timepoint
            )
            expression = f"{expression},'{converted_available_at_timepoint}'"
        expression = f"{expression})\n"

        return expression

    # Interface
    # abstractmethod does not take into account if method is async or not

    @abstractmethod
    def get_all_forecasts(self, search_query: Optional[str] = None) -> List[Timeseries]:
        """
        Get all forecasts for a given Mesh object in a time interval.
        The `target` and the time interval (`start_time` and `end_time`) are set by :py:func:`volue.mesh.Connection.Session.forecast_functions`.

        Example:
            If interval 'P' is given for the Mesh object in the picture below, 10 forecasted time series will be returned.

            .. image:: images/calc_get_all_forecasts.png
               :width: 400

        Note:
            The resulting objects from the `search_query` will be used in the `get_all_forecasts` function, if `search_query` is not set the `target` will be used.

        Args:
            search_query: A search formulated using the :doc:`Mesh search language <mesh_search>`.

        Returns:
            An array of forecast time series with values within the relevant period. Values in forecast series outside the period are not included. The function returns an empty array if no forecast time series have values within the relevant period.
        """
        pass

    @abstractmethod
    def get_forecast(
        self,
        forecast_start_min: Optional[datetime] = None,
        forecast_start_max: Optional[datetime] = None,
        available_at_timepoint: Optional[datetime] = None,
        search_query: Optional[str] = None,
    ) -> Timeseries:
        r"""
        Get one forecast for a given Mesh object in a time interval.

        The `target`and the time interval (`start_time` and `end_time`) are set by :py:func:`volue.mesh.Connection.Session.forecast_functions`.

        Example 1:
            Use `available_at_timepoint` (t\ :sub:`c`) to get the forecast.

            .. code-block:: python

                forecast_funcs = session.forecast_functions(full_name, start_time, end_time)
                result = forecast_funcs.get_forecast(available_at_timepoint)

            .. image:: images/calc_get_forecast_writetime.png
               :width: 400

        Example 2:
            Use `forecast_start_min` (t\ :sub:`0min`) and `forecast_start_max` (t\ :sub:`0max`) to get the forecast that starts in that interval.

            Note: This will ignore `start_time` set by :py:func:`volue.mesh.Connection.Session.forecast_functions`

            .. code-block:: python

                forecast_funcs = session.forecast_functions(full_name, start_time, end_time)
                result = forecast_funcs.get_forecast(forecast_start_min, forecast_start_max)

            .. image:: images/calc_get_forecast_interval.png
               :width: 400


        Note:
            * The function can take `available_at_timepoint` without specifying `forecast_start_min` and `forecast_start_min`.
            * The function can take `forecast_start_min` and `forecast_start_min` with or without specifying `available_at_timepoint` to find the relevant forecast instead of using the start of the requested period (defined in `forecast_functions`). It requires that the forecast series' start is less than or equal to `forecast_start_max` and larger than `forecast_start_min`.
            * If no forecast series has its start time within the given interval, the function returns a time series with NaN.
            * The resulting objects from the `search_query` will be used in the `get_all_forecasts` function, if `search_query` is not set the `target` will be used.

        Args:
            forecast_start_min: Forecast must start after this time.
            forecast_start_max: Forecast must start before this time.
            available_at_timepoint: Forecast that is valid at the given timestamp.
            search_query: A search formulated using the :doc:`Mesh search language <mesh_search>`.

        See Also:
            :ref:`mesh_client:Date times and time zones`

        Returns:
            A time series forecast.
        """
        pass


class ForecastFunctions(_ForecastFunctionsBase):
    """Class for forecast functions that should be run synchronously"""

    def get_all_forecasts(self, search_query: Optional[str] = None) -> List[Timeseries]:
        expression = super()._get_all_forecasts_expression(search_query)
        response = super().run(expression)
        return _parse_timeseries_list_response(response)

    def get_forecast(
        self,
        forecast_start_min: Optional[datetime] = None,
        forecast_start_max: Optional[datetime] = None,
        available_at_timepoint: Optional[datetime] = None,
        search_query: Optional[str] = None,
    ) -> Timeseries:
        expression = super()._get_forecast_expression(
            forecast_start_min, forecast_start_max, available_at_timepoint, search_query
        )
        response = super().run(expression)
        return _parse_single_timeseries_response(response)


class ForecastFunctionsAsync(_ForecastFunctionsBase):
    """Class for forecast functions that should be run asynchronously"""

    async def get_all_forecasts(
        self, search_query: Optional[str] = None
    ) -> List[Timeseries]:
        expression = super()._get_all_forecasts_expression(search_query)
        response = await super().run_async(expression)
        return _parse_timeseries_list_response(response)

    async def get_forecast(
        self,
        forecast_start_min: Optional[datetime] = None,
        forecast_start_max: Optional[datetime] = None,
        available_at_timepoint: Optional[datetime] = None,
        search_query: Optional[str] = None,
    ) -> Timeseries:
        expression = super()._get_forecast_expression(
            forecast_start_min, forecast_start_max, available_at_timepoint, search_query
        )
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)
