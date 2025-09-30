"""
Mesh calculation statistical functions.
*****************************************

For more information see
`Mesh functions <https://volue-public.github.io/energy-smp-docs/latest/mesh/calculations/functions/>`__.

"""

from abc import ABC, abstractmethod
from typing import Optional

from volue.mesh import Timeseries
from volue.mesh.calc.common import (
    _Calculation,
    _parse_single_float_response,
    _parse_single_timeseries_response,
)

_SINGLE_TIMESERIES_CALC_SYMBOL = "t"
_ARRAY_OF_TIMESERIES_CALC_SYMBOL = "T"


class _StatisticalFunctionsBase(_Calculation, ABC):
    """Base class for all statistical function classes."""

    def _sum_expression(
        self, input_type_symbol: str, search_query: Optional[str]
    ) -> str:
        """
        Create an expression for `sum`.

        Args:
            input_type_symbol: Either `t` (for returning a number) or `T` (for returning a time series).
            search_query: A search formulated using the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__.

        Returns:
            Mesh calculation expression.
        """
        expression = f"## = @SUM(@{input_type_symbol}("
        if search_query:
            expression = f"{expression}'{search_query}'"
        expression = f"{expression}))\n"
        return expression

    # Interface
    # abstractmethod does not take into account if method is async or not

    @abstractmethod
    def sum(self, search_query: Optional[str] = None) -> Timeseries:
        """
        Calculates the sum of all of the series in an array of time series.
        The resulting time series is equal to the sum of the values for each time interval in the expression.

        Args:
            search_query: A search formulated using the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__.

        Note:
            The resulting objects from the `search_query` will be used in the `sum` function, if `search_query` is not set the `target` will be used.

        Returns:
            A time series with the sum of the values for each time interval in the expression.
        """
        pass

    @abstractmethod
    def sum_single_timeseries(self, search_query: Optional[str] = None) -> float:
        """
        Calculates the sum of the values of the time series for the required period.
        It returns a number.

        Args:
            search_query: A search formulated using the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__.

        Note:
            The resulting object (single time series) from the `search_query` will be used in the `sum_single_timeseries` function, if `search_query` is not set the `target` will be used.

        Returns:
            The sum of the values of the time series for the required period.
        """
        pass


class StatisticalFunctions(_StatisticalFunctionsBase):
    """Class for statistical functions that should be run synchronously"""

    def sum(self, search_query: Optional[str] = None):
        expression = super()._sum_expression(
            _ARRAY_OF_TIMESERIES_CALC_SYMBOL, search_query
        )
        response = super().run(expression)
        return _parse_single_timeseries_response(response)

    def sum_single_timeseries(self, search_query: Optional[str] = None):
        expression = super()._sum_expression(
            _SINGLE_TIMESERIES_CALC_SYMBOL, search_query
        )
        response = super().run(expression)
        return _parse_single_float_response(response)


class StatisticalFunctionsAsync(_StatisticalFunctionsBase):
    """Class for statistical functions that should be run asynchronously"""

    async def sum(self, search_query: Optional[str] = None):
        expression = super()._sum_expression(
            _ARRAY_OF_TIMESERIES_CALC_SYMBOL, search_query
        )
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)

    async def sum_single_timeseries(self, search_query: Optional[str] = None):
        expression = super()._sum_expression(
            _SINGLE_TIMESERIES_CALC_SYMBOL, search_query
        )
        response = await super().run_async(expression)
        return _parse_single_float_response(response)
