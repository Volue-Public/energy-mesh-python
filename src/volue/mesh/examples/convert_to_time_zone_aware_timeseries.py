from volue.mesh import Connection, Timeseries
from datetime import datetime, timedelta

import helpers
import pyarrow as pa

# This file is an example of a transformation from time zone naive time
# series to time zone aware time series.  Several things to note: 
# 1. Only time series with resolution of DAY or coarser can be converted to
#    time zone aware time series 
# 2. Time series with edits can not be converted to time zone aware
#    time series
# 3. If the time series points in the database are misaligned to the
#    DB time zone, the conversion to time zone aware time series will fail
#
# To find all physical daily time zone naive time series in the database, one
# can use the following SQL query: `SELECT tims_key FROM timeser WHERE tsin_key
# = 111 AND time_zone is null AND rc_key is null;`
#
# Once we know all the time series we want to convert, let's find the ones with
# misaligned data that need fixing before the conversion.  Use this function:
# `validate_points_alignment(session, ts_key)` It will scan a range of points
# and stop on the first misaligned point.  The log will point to the misaligned
# timestamp.
#
# Now, the user needs to peek in the DB and assess how to fix the data. The fix
# depends on the way the data is broken and what was the intention of the data
# writer. There are several options:
# 1. Delete old points before conversion
#    Simple approach that works when the historical data is not important.
# 2. Create a new time series
#    Simple approach, but the old time series resource needs to be replaced
#    with a new one in the model. Additionally, if some calculation expressions
#    refer to the time series directly, they have to be updated.
# 3. Save-Remove-Adjust-Write
#    Save the old points to some storage (other time series, file, etc...).
#    Remove the points from the old time series. Once it's empty, set the time zone.
#    Adjust the saved points to the time zone and write them back.
# 4. Fix the points, commit, set the time zone
#    Create a script that fixes a specific time series case. 
#    The time zone can be set once the data is correct.See 2 fix examples below.

TS_KEYS = [
    # This daily time series (key: 254335) has 2 points per day in the interval
    # [2025-10-27; 2026-03-28) (DB time zone):
    # 2025-10-27 12:00
    # 2025-10-27 01:00
    # 2025-10-28 12:00
    # 2025-10-28 01:00
    # 2025-10-29 12:00
    # 2025-10-29 01:00
    # ...
    # The values and flags matchBefore adding a time zone to this time series,
    # remove the points at 01:00.
    254335,
    # This daily time series (key: 448438) data is unaligned to the DB time zone
    # midnight in the interval [2025-10-25; 2026-03-28) (DB time zone):
    # 2025-10-24 12:00
    # 2025-10-25 01:00
    # 2025-10-26 01:00
    # 2025-10-27 01:00
    # 2025-10-28 01:00
    # ...
    # Before adding a time zone to this time series, shift the timestamps one
    # hour back in that interval.
    448438
]


def fix_ts_254335(session: Connection.Session):
    target = 254335
    start = datetime(2025, 10, 24, 23, 0, 0)
    end = datetime(2026, 3, 27, 23, 0, 0)
    points = session.read_timeseries_points(
        target=target, start_time=start, end_time=end
    )

    utc_date = points.arrow_table[0]
    flags = points.arrow_table[1]
    values = points.arrow_table[2]

    new_utc_date = []
    new_flags = []
    new_values = []

    for point in zip(utc_date, flags, values):
        if point[0].as_py().hour == 23:
            new_utc_date.append(point[0])
            new_flags.append(point[1])
            new_values.append(point[2])

    arrays = [pa.array(new_utc_date), pa.array(new_flags), pa.array(new_values)]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    new_points = Timeseries(table=table, start_time=start, end_time=end)
    new_points.timskey = target

    session.write_timeseries_points(new_points)

    # Read the points again and visually confirm the data is correct.
    # points_not_saved = session.read_timeseries_points(target=target, start_time=start, end_time=end)
    # print(points_not_saved.arrow_table.to_pandas())
    # If the result is fine - commit.
    # session.commit()
    session.rollback()



def fix_ts_448438(session: Connection.Session):
    target = 448438
    start = datetime(2025, 10, 24, 23, 0, 0)
    end = datetime(2026, 3, 27, 23, 0, 0)
    points = session.read_timeseries_points(
        target=target, start_time=start, end_time=end
    )

    utc_date = points.arrow_table[0]
    flags = points.arrow_table[1]
    values = points.arrow_table[2]

    new_utc_date = []
    new_flags = []
    new_values = []

    for point in zip(utc_date, flags, values):
        if point[0].as_py().hour == 0:
            new_utc_date.append(point[0].as_py() + timedelta(hours=-1))
            new_flags.append(point[1])
            new_values.append(point[2])

    arrays = [pa.array(new_utc_date), pa.array(new_flags), pa.array(new_values)]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    new_points = Timeseries(table=table, start_time=start, end_time=end)
    new_points.timskey = target

    session.write_timeseries_points(new_points)

    # Read the points again and visually confirm the data is correct.
    # points_not_saved = session.read_timeseries_points(target=target, start_time=start, end_time=end)
    # print(points_not_saved.arrow_table.to_pandas())
    # If the result is fine - commit.
    # session.commit()
    session.rollback()



def validate_points_alignment(session: Connection.Session, ts_key: int):
    START = datetime(year=1900, month=12, day=31, hour=23)
    END = datetime(
        START.year + 200,
        START.month,
        START.day,
        START.hour,
        START.minute,
        START.second,
        START.microsecond,
        START.tzinfo,
    )

    points = session.read_timeseries_points(
        target=ts_key, start_time=START, end_time=END
    )
    if points.resolution is not Timeseries.Resolution.DAY:
        raise Exception(
            f"Time series (key {points.timskey}) resolution not equal to DAY: {points.resolution}"
        )

    utc_time = points.arrow_table[0]
    if len(utc_time) == 0:
        raise Exception("Unexpected empty segment")

    aligned = True
    for timestamp in utc_time:
        if timestamp.as_py().hour != 23:
            print(
                f"Time series key {ts_key}: the timestamp {timestamp.as_py()} is not aligned to the DB time zone midnight"
            )
            aligned = False
            break
    return aligned


def convert_to_time_zone_aware(session: Connection.Session, ts_key: int):
    session.update_timeseries_resource_info(
        timeseries_key=ts_key, new_time_zone="Europe/Warsaw"
    )
    session.commit()


def main(address, tls_root_pem_cert):
    connection = Connection.insecure(address)
    with connection.create_session() as session:
        if validate_points_alignment(session=session, ts_key=TS_KEYS[0]) == False:
            fix_ts_254335(session)
            convert_to_time_zone_aware(session, TS_KEYS[0])

        if validate_points_alignment(session=session, ts_key=TS_KEYS[1]) == False:
            fix_ts_448438(session)
            convert_to_time_zone_aware(session, TS_KEYS[1])


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
