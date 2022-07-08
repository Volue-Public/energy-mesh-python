"""
Common classes/enums/etc for Mesh calculation functions.
"""

import datetime
from dateutil import tz
from enum import Enum
from typing import List, Union
import uuid

from volue.mesh import Timeseries
from volue.mesh._common import _read_proto_reply, _read_proto_numeric_reply,\
    _to_proto_guid, _to_proto_mesh_id, _to_protobuf_utcinterval
from volue.mesh.proto.core.v1alpha import core_pb2


class Timezone(Enum):
    """
    Timezone specifier

    Args:
        LOCAL (enum): Local time zone
        STANDARD (enum): Local time zone without Daylight Saving Time (DST)
        UTC (enum): Universal Time Coordinated (UTC)
    """
    LOCAL = 0
    STANDARD = 1
    UTC = 2


def _convert_datetime_to_mesh_calc_format(input: datetime) -> str:
    """
    Converts input datetime to format expected by Mesh calculator.
    Datetime is converted to UTC. If input datetime is time zone naive then it is already treated as UTC.

    Example:
        'UTC20210917000000000'

    Args:
        input (datetime): the timestamp to be converted

    Returns:
        str:
    """
    input_utc_datetime = input
    if input.tzinfo is not None:
        input_utc_datetime = input.astimezone(tz.UTC)

    converted_date_str = input_utc_datetime.strftime("%Y%m%d%H%M%S%f")[:-3]
    converted_date_str = f"UTC{converted_date_str}"
    return converted_date_str


def _parse_timeseries_list_response(response: core_pb2.CalculationResponse) -> List[Timeseries]:
    """
    Helper function for parsing a calculator respons.

    Args:
        response (core_pb2.CalculationResponse): the gRPC response received from the Mesh server

    Returns:
        List[Timeseries]: a list of time series
    """
    timeseries = _read_proto_reply(response.timeseries_results)
    return timeseries


def _parse_single_timeseries_response(response: core_pb2.CalculationResponse) -> Timeseries:
    """
    Helper function for parsing a calculator respons.

    Args:
        response (core_pb2.CalculationResponse): the gRPC response received from the Mesh server

    Raises:
        RuntimeError:  Error message raised if the input is not valid

    Returns:
        List[Timeseries]: a single time series
    """
    timeseries = _read_proto_reply(response.timeseries_results)
    if len(timeseries) != 1:
        raise RuntimeError(
            f"invalid calculation result, expected 1 timeseries, but got {len(timeseries)}")
    return timeseries[0]


def _parse_single_float_response(response: core_pb2.CalculationResponse) -> float:
    """
    Helper function for parsing a calculator respons.

    Args:
        response (core_pb2.CalculationResponse): the gRPC response received from the Mesh server

    Raises:
        RuntimeError:  Error message raised if the input is not valid

    Returns:
        float: the value of the calculation respons
    """
    result = _read_proto_numeric_reply(response.numeric_results)
    if len(result) != 1:
        raise RuntimeError(
            f"invalid calculation result, expected 1 float value, but got {len(result)}")
    return result[0]


class _Calculation:
    """
    Base class for all calculations
    """
    def __init__(self,
                 session,
                 target: Union[uuid.UUID, str, int],
                 start_time: datetime,
                 end_time: datetime):
        """

        Args:
            session: active Mesh session
            target: Mesh object, virtual or physical time series the
                calculation expression will be evaluated relative to.
                It could be a time series key, Universal Unique Identifier or
                a path in the :ref:`Mesh model <mesh_model>`.
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval
        """
        self.session = session
        self.target: Union[uuid.UUID, str, int] = target
        self.start_time: datetime = start_time
        self.end_time: datetime = end_time

    def prepare_request(self, expression: str) -> core_pb2.CalculationRequest:
        """
        Checks that the requirements for a calculation request are met,
        and constructs a calculation request object

        Args:
            expression (str): expression which consists of one or more functions to call. See :ref:`expressions <mesh expression>`

        Raises:
            TypeError:  Error message raised if the returned result from the request is not as expected

        Returns:
            core_pb2.CalculationRequest:
        """
        request = core_pb2.CalculationRequest(
            session_id=_to_proto_guid(self.session.session_id),
            expression=expression,
            interval=_to_protobuf_utcinterval(self.start_time, self.end_time),
            relative_to=_to_proto_mesh_id(self.target)
        )
        return request

    async def run_async(self, expression: str) -> core_pb2.CalculationResponse:
        """Run a function using an asynchronous connection.

        Args:
            expression (str): expression which consists of one or more functions to call. See :ref:`expressions <mesh expression>`

        Returns:
            core_pb2.CalculationResponse:
        """
        from volue.mesh.aio import Connection as AsyncConnection
        if not isinstance(self.session, AsyncConnection.Session):
            raise TypeError('async connection session is required to run async calculations, but got sync session')

        request = self.prepare_request(expression)
        response = await self.session.mesh_service.RunCalculation(request)
        return response

    def run(self, expression: str):
        """Run a function using a synchronous connection.

        Args:
            expression (str): expression which consists of one or more functions to call. See :ref:`expressions <mesh expression>`

        Returns:
            core_pb2.CalculationResponse:
        """
        from volue.mesh import Connection
        if not isinstance(self.session, Connection.Session):
            raise TypeError('sync connection session is required to run sync calculations, but got async session')

        request = self.prepare_request(expression)
        response = self.session.mesh_service.RunCalculation(request)
        return response
