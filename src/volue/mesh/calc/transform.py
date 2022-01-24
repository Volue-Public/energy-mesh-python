from dataclasses import dataclass
import datetime
from enum import Enum
import uuid

from volue.mesh import Timeseries
from volue.mesh._common import read_proto_reply, to_proto_guid, to_protobuf_utcinterval
from volue.mesh.proto import mesh_pb2


class Transform:
    """"
    Mesh calculation function: TRANSFORM
    """

    class Timezone(Enum):
        """
        Timezone parameter
        """
        LOCAL    = 0
        DATABASE = 1
        UTC      = 2
        UNKNOWN  = 3  # TODO: should we expose it? Is it used in some scenario?

    class Method(Enum):
        """
        Transformation method
        """
        SUM   = 0
        SUMI  = 1
        AVG   = 2  # equivalent to MEAN
        AVGI  = 3
        FIRST = 5
        LAST  = 6
        MIN   = 7
        MAX   = 8

    @dataclass
    class Parameters:
        """
        Transformation parameters
        """
        resolution: 'Timeseries.Resolution'
        method: 'Transform.Method'
        timezone: 'Transform.Timezone' = None

    @staticmethod
    def prepare_request(session_id: uuid,
                        start_time: datetime,
                        end_time: datetime,
                        relative_to: mesh_pb2.ObjectId,
                        params: Parameters) -> mesh_pb2.CalculationRequest:
        """
        Validates transformaton specific input parameters, computes calculation expression and
        returns gRPC calculation request to be send to Mesh server.

        Raises:
            TypeError:
        """
        if params.resolution is Timeseries.Resolution.BREAKPOINT:
            raise TypeError("unsupported resolution for transformation")

        expression = f"## = @TRANSFORM(@t(), '{params.resolution.name}', '{params.method.name}'"
        if params.timezone is not None:
            expression = f"{expression}, '{params.timezone.name}'"
        expression = f"{expression})\n"

        request = mesh_pb2.CalculationRequest(
            session_id=to_proto_guid(session_id),
            expression=expression,
            interval=to_protobuf_utcinterval(start_time, end_time),
            relative_to=relative_to
            )

        return request

    @staticmethod
    def parse_response(response: mesh_pb2.CalculationResponse) -> Timeseries:
        """
        Parses gRPC response from Mesh server and validates the result.

        Raises:
            RuntimeError:
        """
        transformed_timeseries = read_proto_reply(response.timeseries_results)
        if len(transformed_timeseries) != 1:
            raise RuntimeError(
                f"invalid transformation result, expected 1 timeseries, bot got {len(transformed_timeseries)}")
        return transformed_timeseries[0]
