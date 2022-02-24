""""
Mesh calculation miscellaneous functions
"""

from volue.mesh import Timeseries
from volue.mesh._common import read_proto_reply
from volue.mesh.calc.common import Calculation
from volue.mesh.proto.core.v1alpha import core_pb2


class __MiscBase(Calculation):

    def _sum_expression(self, search_query) -> str:
        return f"## = @SUM(@T('{search_query}'))\n"

#TODO: abstract class with pure misc functions for Misc and MiscAsync to override?

class Misc(__MiscBase):
    def sum(self, search_query = None) -> Timeseries:
        """
        Empty `seach_query` means self-reference to `relative_to`.
        """
        expression = super()._sum_expression(search_query)
        response = super().run(expression)
        return super().parse_single_timeseries_response(response)


class MiscAsync(__MiscBase):
    async def sum(self, search_query = None) -> Timeseries:
        """
        Empty `seach_query` means self-reference to `relative_to`.
        """
        expression = super()._sum_expression(search_query)
        response = await super().run_async(expression)
        return super().parse_single_timeseries_response(response)