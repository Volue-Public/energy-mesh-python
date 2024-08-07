import asyncio
from datetime import datetime

import grpc
import helpers

from volue.mesh.aio import Connection


async def process_timeseries_values(arrow_table):
    # the processing can also be an async IO call
    # to e.g. separate service
    await asyncio.sleep(8)
    print(f"Processing completed - {len(arrow_table)} points were processed")


async def read_timeseries_points(session, path):
    start_time = datetime(2016, 5, 1)
    end_time = datetime(2016, 5, 4)

    # read operation can be a long running operation
    # with asyncio API we can switch to do something else
    # while waiting for the read operation to complete
    # (e.g. doing processing for already returned time series)
    timeseries_read = await session.read_timeseries_points(
        target=path, start_time=start_time, end_time=end_time
    )

    return timeseries_read.arrow_table


async def handle_timeseries(session, path):
    arrow_table = await read_timeseries_points(session, path)
    await process_timeseries_values(arrow_table)


async def main(address, tls_root_pem_cert):
    """
    Showing how to use asynchronous connection in a real-world scenario.
    First multiple time series are returned that match a given query.
    Then each time series is read and some processing is applied.

    Note: Mesh does not yet handle parallel requests, every request is handled
          sequentially.

    This example works with `SimpleThermalTestModel` test model, where 2 time
    series are returned for the given query. Assume reading time series takes
    10 seconds and processing (or some different computation, e.g.
    neural network inference based on that input) takes 8 seconds.
    When waiting for the read operation to complete for the second time series
    we can already start processing the first time series. See:

    Tr = 10s (reading)
    Tp = 8s  (processing)

    Asynchronous code (with Mesh handling requests sequentially):
    |   Tr1  ||  Tp1 |
    ------------------
              |   Tr2  ||  Tp2 |
              ------------------
    ---------- 28s -------------

    Whereas for synchronous code:
    |   Tr1  ||  Tp1 |
    ------------------
                      |   Tr2  ||  Tp2 |
                      ------------------
    ---------------  36s ---------------

    For 2 time series we save ~22% time.
    For 10 time series it would be 40% time (108s instead of 180s).

    Note: the processing could be also done using async IO
          (e.g. requests send to different service).
    """

    query = "*.TsRawAtt"
    start_object_path = "Model/SimpleThermalTestModel/ThermalComponent"

    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)

    async with connection.create_session() as session:
        try:
            timeseries_attributes = await session.search_for_timeseries_attributes(
                target=start_object_path, query=query
            )
        except grpc.RpcError as e:
            print(f"Could not find timeseries attribute: {e}")
            return

        print(f"Number of found time series: {len(timeseries_attributes)}")
        await asyncio.gather(
            *(
                handle_timeseries(session, timeseries_attribute.path)
                for timeseries_attribute in timeseries_attributes
            )
        )


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    asyncio.run(main(address, tls_root_pem_cert))
