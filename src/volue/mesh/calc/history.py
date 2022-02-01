""""
Mesh calculation history functions
"""

from dataclasses import dataclass
import datetime
from enum import Enum
import uuid

from volue.mesh import Timeseries
from volue.mesh._common import read_proto_reply, to_proto_guid, to_protobuf_utcinterval
from volue.mesh.calc.common import Timezone
from volue.mesh.proto import mesh_pb2

class Function(Enum):
    """
    History function
    """
    FORECAST   = 'GetForecast'
    AS_OF_TIME = 'GetTsAsOfTime'

@dataclass
class Parameters:
    """
    Timeseries history parameters
    """
    function: Function
    available_at_timepoint: datetime
    timezone: Timezone = None

def prepare_request(session_id: uuid,
                    start_time: datetime,
                    end_time: datetime,
                    start_object: mesh_pb2.ObjectId,
                    params: Parameters) -> mesh_pb2.CalculationRequest:
    """
    Validates timeseries history specific input parameters, computes calculation expression and
    returns a gRPC calculation request to be sent to the Mesh server.
    """

    # convert to format '20210917000000000'
    # %f returns microseconds, we need milliseconds so remove last 3 digits
    available_at_timepoint_str = params.available_at_timepoint.strftime("%Y%m%d%H%M%S%f")[:-3]

    expression = f"## = @{params.function.value}(@t(), '"
    if params.timezone is not None:
        expression = f"{expression}{params.timezone.name}"
    expression = f"{expression}{available_at_timepoint_str}')\n"

    request = mesh_pb2.CalculationRequest(
        session_id=to_proto_guid(session_id),
        expression=expression,
        interval=to_protobuf_utcinterval(start_time, end_time),
        relative_to=start_object
        )

    return request

def parse_response(response: mesh_pb2.CalculationResponse) -> Timeseries:
    """
    Parses a gRPC response from the Mesh server and validates the result.

    Raises:
        RuntimeError:
    """
    timeseries = read_proto_reply(response.timeseries_results)
    if len(timeseries) != 1:
        raise RuntimeError(
            f"invalid history result, expected 1 timeseries, bot got {len(timeseries)}")
    return timeseries[0]
