"""
Mesh calculation statistical functions.
"""

from abc import ABC, abstractmethod

from volue.mesh import Timeseries
from volue.mesh.calc.common import _Calculation, _parse_single_timeseries_response


class _StatisticalFunctionsBase(_Calculation, ABC):

    def _sum_expression(self, search_query: str) -> str:
        expression = f"## = @SUM(@T("
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

        The resulting objects from the `search_query` will be used in the `sum` function,
        if `search_query` is not set the `relative_to` object will be used.
        """
        pass


class StatisticalFunctions(_StatisticalFunctionsBase):

    def sum(self, search_query: str = None) -> Timeseries:
        expression = super()._sum_expression(search_query)
        response = super().run(expression)
        return _parse_single_timeseries_response(response)


class StatisticalFunctionsAsync(_StatisticalFunctionsBase):

    async def sum(self, search_query: str = None) -> Timeseries:
        expression = super()._sum_expression(search_query)
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)
