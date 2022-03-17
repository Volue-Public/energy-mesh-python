"""
Mesh calculation statistical functions.
*****************************************

For more information see :ref:`mesh_functions:statistical`.

"""

from abc import ABC, abstractmethod

from volue.mesh import Timeseries
from volue.mesh.calc.common import _Calculation, \
    _parse_single_float_response, _parse_single_timeseries_response

_SINGLE_TIMESERIES_CALC_SYMBOL = 't'
_ARRAY_OF_TIMESERIES_CALC_SYMBOL = 'T'


class _StatisticalFunctionsBase(_Calculation, ABC):
    """Base class for all statistical function classes"""

    def _sum_expression(self, input_type_symbol: str, search_query: str) -> str:
        """
        Create an expression for `sum`.

        Args:
            input_type_symbol (str): either `t` (for returning a number) or `T` (for returning a time series)
            search_query (str): a search formulated using the :doc:`Mesh search language <mesh_search>`

        Returns:
            str: a `sum` expresssion
        """
        expression = f"## = @SUM(@{input_type_symbol}("
        if search_query:
            expression = f"{expression}'{search_query}'"
        expression = f"{expression}))\n"
        return expression

    # Interface
    # abstractmethod does not take into account if method is async or not

    @abstractmethod
    def sum(self, search_query: str = None) -> Timeseries:
        """
        Calculates the sum of all of the series in an array of time series.
        The resulting time series is equal to the sum of the values for each time interval in the expression.

        Args:
            search_query (str): a search formulated using the :doc:`Mesh search language <mesh_search>`

        Note:
            The resulting objects from the `search_query` will be used in the `sum` function, if `search_query` is not set the `relative_to` object will be used.

        Returns:
            Timeseries: a time series with the sum of the values for each time interval in the expression.
        """
        pass

    @abstractmethod
    def sum_single_timeseries(self, search_query: str = None) -> float:
        """
        Calculates the sum of the values of the time series for the required period.
        It returns a number.

        Note:
            The resulting object (single time series) from the `search_query` will be used in the `sum_single_timeseries` function, if `search_query` is not set the `relative_to` object will be used.

        Returns:
            float: the sum of the values of the time series for the required period
        """
        pass


class StatisticalFunctions(_StatisticalFunctionsBase):

    def sum(self, search_query: str = None):
        expression = super()._sum_expression(_ARRAY_OF_TIMESERIES_CALC_SYMBOL, search_query)
        response = super().run(expression)
        return _parse_single_timeseries_response(response)

    def sum_single_timeseries(self, search_query: str = None):
        expression = super()._sum_expression(_SINGLE_TIMESERIES_CALC_SYMBOL, search_query)
        response = super().run(expression)
        return _parse_single_float_response(response)


class StatisticalFunctionsAsync(_StatisticalFunctionsBase):

    async def sum(self, search_query: str = None):
        expression = super()._sum_expression(_ARRAY_OF_TIMESERIES_CALC_SYMBOL, search_query)
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)

    async def sum_single_timeseries(self, search_query: str = None):
        expression = super()._sum_expression(_SINGLE_TIMESERIES_CALC_SYMBOL, search_query)
        response = await super().run_async(expression)
        return _parse_single_float_response(response)
