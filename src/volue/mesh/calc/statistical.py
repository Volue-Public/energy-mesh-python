"""
Mesh calculation statistical functions.
"""

from abc import ABC, abstractmethod

from volue.mesh import Timeseries
from volue.mesh.calc.common import _Calculation, _parse_single_timeseries_response


class _StatisticalFunctionsBase(_Calculation, ABC):

    def _sum_expression(self, search_query) -> str:
        return f"## = @SUM(@T('{search_query}'))\n"


    # Interface
    # abstractmethod does not take into account if method is async or not

    @abstractmethod
    def sum(self, search_query = None) -> Timeseries:
        """
        Empty `seach_query` means self-reference to `relative_to`.
        """
        pass

class StatisticalFunctions(_StatisticalFunctionsBase):
    def sum(self, search_query = None) -> Timeseries:
        expression = super()._sum_expression(search_query)
        response = super().run(expression)
        return _parse_single_timeseries_response(response)


class StatisticalFunctionsAsync(_StatisticalFunctionsBase):
    async def sum(self, search_query = None) -> Timeseries:
        expression = super()._sum_expression(search_query)
        response = await super().run_async(expression)
        return _parse_single_timeseries_response(response)
