from datetime import datetime, timedelta

import helpers
import pyarrow as pa

from volue.mesh import Connection, Timeseries

# This example shows how to convert two daily time series from time zone-naive to time zone-aware
# and back.
#
# Assuming we want to convert the time series with keys 1111 and 2222, we first use the
# `validate_points_alignment` function to scan a range of points on each series and verify whether
# their points are correctly aligned. In this case, both of these time series have points that need
# to be adjusted before we can perform the conversion:
#
# The first time series (key 1111) has 2 points per day in the interval [2025-10-27; 2026-03-28) (DB time zone):
# 2025-10-27 00:00
# 2025-10-27 01:00
# 2025-10-28 00:00
# 2025-10-28 01:00
# 2025-10-29 00:00
# 2025-10-29 01:00
# ...
# The values at midnight and 1AM are the same. If the values were different,
# the user would need to make a decision which value should stay and adjust the script.
# For this simple case, before adding a time zone to this time series,
# we must remove the points at 01:00.
#
# The second time series (key: 2222) has its data unaligned to the midnight in the interval
# [2025-10-25; 2026-03-28) (DB time zone):
# 2025-10-24 00:00
# 2025-10-25 01:00
# 2025-10-26 01:00
# 2025-10-27 01:00
# 2025-10-28 01:00
# ...
#
# Before adding a time zone to this time series, we must shift the timestamps one hour back in that interval.
#
# We now need to decide on how to fix the time series for conversion. The method we choose for this
# will depend on how the points are misaligned, and the intention of the user who originally wrote
# them:
#
# 1. Delete the old points before conversion
#    Simple approach that works when the historical data is not important.
# 2. Create a new time zone-aware time series
#    Simple approach, but the old time series resource needs to be replaced
#    with a new one in the model. Additionally, if some calculation expressions
#    refer to the time series directly, they have to be updated.
# 3. Save-Remove-Adjust-Write
#    Save the old points to some storage (other time series, file, etc...).
#    Remove the points from the old time series. Once it's empty, set the time zone and commit.
#    Adjust the saved points to the time zone and write them back.
# 4. Fix the points, commit, set the time zone
#    Create a script that fixes a specific time series case.
#    The time zone can be set once the data is correct.
#
# For this example, we will use the last method.

TS_KEYS = [
    1111,
    2222,
]

DB_ZONE_MIDNIGHT_IN_UTC = 23
DB_ZONE_1AM_IN_UTC = 0


def fix_ts_1111(session: Connection.Session, points: Timeseries):
    start = datetime(2025, 10, 26, 23, 0, 0)
    end = datetime(2026, 3, 27, 23, 0, 0)

    utc_date = points.arrow_table[0]
    flags = points.arrow_table[1]
    values = points.arrow_table[2]

    new_utc_date = []
    new_flags = []
    new_values = []

    for point in zip(utc_date, flags, values):
        # Keep the points at DB time midnight.
        timestamp = point[0].as_py()
        if (
            timestamp >= start
            and timestamp < end
            and timestamp.hour == DB_ZONE_MIDNIGHT_IN_UTC
        ):
            new_utc_date.append(timestamp)
            new_flags.append(point[1])
            new_values.append(point[2])

    arrays = [pa.array(new_utc_date), pa.array(new_flags), pa.array(new_values)]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    new_points = Timeseries(table=table, start_time=start, end_time=end)
    new_points.timskey = points.timskey

    session.write_timeseries_points(new_points)

    # Read the points again and visually confirm the data is correct.
    # points_not_saved = session.read_timeseries_points(target=target, start_time=start, end_time=end)
    # print(points_not_saved.arrow_table.to_pandas())
    # If the result is fine - commit.
    # session.commit()
    session.rollback()


def fix_ts_2222(session: Connection.Session, points: Timeseries):
    start = datetime(2025, 10, 24, 23, 0, 0)
    end = datetime(2026, 3, 27, 23, 0, 0)

    utc_date = points.arrow_table[0]
    flags = points.arrow_table[1]
    values = points.arrow_table[2]

    new_utc_date = []
    new_flags = []
    new_values = []

    for point in zip(utc_date, flags, values):
        # Move the points from 01:00 to 00:00 (DB time).
        timestamp = point[0].as_py()
        if (
            timestamp >= start
            and timestamp < end
            and timestamp.hour == DB_ZONE_1AM_IN_UTC
        ):
            new_utc_date.append(timestamp - timedelta(hours=1))
            new_flags.append(point[1])
            new_values.append(point[2])

    arrays = [pa.array(new_utc_date), pa.array(new_flags), pa.array(new_values)]

    table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    new_points = Timeseries(table=table, start_time=start, end_time=end)
    new_points.timskey = points.timskey

    session.write_timeseries_points(new_points)

    # Read the points again and visually confirm the data is correct.
    # points_not_saved = session.read_timeseries_points(target=target, start_time=start, end_time=end)
    # print(points_not_saved.arrow_table.to_pandas())
    # If the result is fine - commit.
    # session.commit()
    session.rollback()


def validate_points_alignment(points: Timeseries):
    if points.resolution is not Timeseries.Resolution.DAY:
        raise Exception(
            f"Time series (key {points.timskey}) resolution not equal to DAY: {points.resolution}"
        )

    utc_time = points.arrow_table[0]
    if len(utc_time) == 0:
        raise Exception("Unexpected empty segment")

    aligned = True
    for timestamp in utc_time:
        if timestamp.as_py().hour != DB_ZONE_MIDNIGHT_IN_UTC:
            print(
                f"Time series key {points.timskey}: the timestamp {timestamp.as_py()} is not aligned to the DB time zone midnight"
            )
            aligned = False
            break
    return aligned


def convert_to_time_zone_aware(session: Connection.Session, ts_key: int):
    session.update_timeseries_resource_info(
        timeseries_key=ts_key, new_time_zone="Europe/Warsaw"
    )
    session.commit()


def convert_to_time_zone_naive(session: Connection.Session, ts_key: int):
    session.update_timeseries_resource_info(timeseries_key=ts_key, new_time_zone="")
    session.commit()


def main(address, tls_root_pem_cert):
    # For production environments create connection using: with_tls, with_kerberos, or with_external_access_token, e.g.:
    # connection = Connection.with_tls(address, tls_root_pem_cert)
    connection = Connection.insecure(address)
    with connection.create_session() as session:
        # In perfect case all points of the time series to be converted to time zone-aware are correctly aligned.
        # In such case, we can set the time zone and commit changes successfully. However, it may happen that the
        # points are unaligned, especially around DST transitions. In this example we show 2 potential unalignment scenarios.
        try:
            START = datetime(year=1900, month=12, day=31, hour=23)
            END = datetime(year=2100, month=12, day=31, hour=23)

            points = session.read_timeseries_points(
                target=TS_KEYS[0], start_time=START, end_time=END
            )

            if not validate_points_alignment(points):
                fix_ts_1111(session, points)
            convert_to_time_zone_aware(session, TS_KEYS[0])
            convert_to_time_zone_naive(session, TS_KEYS[0])

            points = session.read_timeseries_points(
                target=TS_KEYS[1], start_time=START, end_time=END
            )

            if not validate_points_alignment(points):
                fix_ts_2222(session, points)
            convert_to_time_zone_aware(session, TS_KEYS[1])
            convert_to_time_zone_naive(session, TS_KEYS[1])
        except Exception as e:
            print(f"Failed to convert the time series: {e}")


if __name__ == "__main__":
    address, tls_root_pem_cert = helpers.get_connection_info()
    main(address, tls_root_pem_cert)
