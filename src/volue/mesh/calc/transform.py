"""
Mesh calculation transformation functions.
The functions in this category are used to calculate time series with a different time resolution than the source.
"""

from dataclasses import dataclass
import datetime
from enum import Enum
import uuid

from volue.mesh import Timeseries
from volue.mesh._common import read_proto_reply, to_proto_guid, to_protobuf_utcinterval
from volue.mesh.calc.common import Timezone
from volue.mesh.proto.core.v1alpha import core_pb2

class Method(Enum):
    """
    Transformation method
    """
    SUM   = 0
    SUMI  = 1  # I -> weighted sum, only for breakpoint timeseries
    AVG   = 2  # equivalent to MEAN
    AVGI  = 3  # I -> weighted average, only for breakpoint timeseries
    FIRST = 5
    LAST  = 6
    MIN   = 7
    MAX   = 8


@dataclass
class Parameters:
    """
    Transformation parameters
    """
    resolution: Timeseries.Resolution
    method: Method
    timezone: Timezone = None


def _prepare_request(session_id: uuid,
                    start_time: datetime,
                    end_time: datetime,
                    relative_to: core_pb2.ObjectId,
                    params: Parameters) -> core_pb2.CalculationRequest:
    """
    Validates transformation specific input parameters, computes calculation expression and
    returns a gRPC calculation request to be sent to the Mesh server.

    Raises:
        ValueError:
    """
    if params.resolution is Timeseries.Resolution.BREAKPOINT:
        raise ValueError("'BREAKPOINT' resolution is unsupported for timeseries transformation")

    expression = f"## = @TRANSFORM(@t(), '{params.resolution.name}', '{params.method.name}'"
    if params.timezone is not None:
        expression = f"{expression}, '{params.timezone.name}'"
    expression = f"{expression})\n"

    request = core_pb2.CalculationRequest(
        session_id=to_proto_guid(session_id),
        expression=expression,
        interval=to_protobuf_utcinterval(start_time, end_time),
        relative_to=relative_to
        )

    return request


def _parse_response(response: core_pb2.CalculationResponse) -> Timeseries:
    """
    Parses a gRPC response from the Mesh server and validates the result.

    Raises:
        RuntimeError:
    """
    timeseries = read_proto_reply(response.timeseries_results)
    if len(timeseries) != 1:
        raise RuntimeError(
            f"invalid transformation result, expected 1 timeseries, bot got {len(timeseries)}")
    return timeseries[0]
