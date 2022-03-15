"""
Common classes/enums/etc for Mesh calculation functions.
"""

import datetime
from dateutil import tz
from enum import Enum
from typing import List

from volue.mesh import MeshObjectId, Timeseries
from volue.mesh._common import read_proto_reply, read_proto_numeric_reply, to_proto_guid, to_protobuf_utcinterval
from volue.mesh.proto.core.v1alpha import core_pb2


class Timezone(Enum):
    """
    Timezone parameter
    """
    LOCAL = 0
    """Local time zone"""
    STANDARD = 1
    """Local time zone without Daylight Saving Time (DST)"""
    UTC = 2
    """Universal Time Coordinated (UTC)"""


def _convert_datetime_to_mesh_calc_format(input: datetime) -> str:
    """
    Converts input datetime to format expected by Mesh calculator, e.g. 'UTC20210917000000000'.
    Datetime is converted to UTC. If input datetime is time zone naive then it is already treated as UTC.
    """
    input_utc_datetime = input
    if input.tzinfo is not None:
        input_utc_datetime = input.astimezone(tz.UTC)

    converted_date_str = input_utc_datetime.strftime("%Y%m%d%H%M%S%f")[:-3]
    converted_date_str = f"UTC{converted_date_str}"
    return converted_date_str


def _parse_timeseries_list_response(response: core_pb2.CalculationResponse) -> List[Timeseries]:
    timeseries = read_proto_reply(response.timeseries_results)
    return timeseries


def _parse_single_timeseries_response(response: core_pb2.CalculationResponse) -> Timeseries:
    timeseries = read_proto_reply(response.timeseries_results)
    if len(timeseries) != 1:
        raise RuntimeError(
            f"invalid calculation result, expected 1 timeseries, but got {len(timeseries)}")
    return timeseries[0]


def _parse_single_float_response(response: core_pb2.CalculationResponse) -> float:
    result = read_proto_numeric_reply(response.numeric_results)
    if len(result) != 1:
        raise RuntimeError(
            f"invalid calculation result, expected 1 float value, but got {len(result)}")
    return result[0]


class _Calculation:

    def __init__(self,
                 session,
                 relative_to: MeshObjectId,
                 start_time: datetime,
                 end_time: datetime):
        self.session = session
        self.relative_to: MeshObjectId = relative_to
        self.start_time: datetime = start_time
        self.end_time: datetime = end_time

    def prepare_request(self, expression: str) -> core_pb2.CalculationRequest:
        relative_to = core_pb2.ObjectId()  # convert to gRPC object
        if self.relative_to.timskey is not None:
            relative_to.timskey = self.relative_to.timskey
        elif self.relative_to.uuid_id is not None:
            relative_to.guid.CopyFrom(to_proto_guid(self.relative_to.uuid_id))
        elif self.relative_to.full_name is not None:
            relative_to.full_name = self.relative_to.full_name
        else:
            raise TypeError("need to specify either timskey, uuid_id or full_name of 'relative_to' object")

        # TODO: potentially it is worth to check here if more than one property of 'self.relative_to' is set
        # it might indicate a misuse

        request = core_pb2.CalculationRequest(
            session_id=to_proto_guid(self.session.session_id),
            expression=expression,
            interval=to_protobuf_utcinterval(self.start_time, self.end_time),
            relative_to=relative_to
        )
        return request

    async def run_async(self, expression: str):
        from volue.mesh.aio import Connection as AsyncConnection
        if not isinstance(self.session, AsyncConnection.Session):
            raise TypeError('async connection session is required to run async calculations, but got sync session')

        request = self.prepare_request(expression)
        response = await self.session.mesh_service.RunCalculation(request)
        return response

    def run(self, expression: str):
        from volue.mesh import Connection
        if not isinstance(self.session, Connection.Session):
            raise TypeError('sync connection session is required to run sync calculations, but got async session')

        request = self.prepare_request(expression)
        response = self.session.mesh_service.RunCalculation(request)
        return response
