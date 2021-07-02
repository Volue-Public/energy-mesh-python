import pyarrow


def print_timeseries_points(reply, name, verbose=False):
    print(f"Reply contains {len(reply.timeseries)} timeseries")
    n = 0
    for timeserie in reply.timeseries:
        reader = pyarrow.ipc.open_stream(timeserie.data)
        pandas = reader.read_pandas()
        print(pandas)
        print(reader.schema)
        n += 1
    print(f"Received {len(pandas)} points for timeseries: {name}")

