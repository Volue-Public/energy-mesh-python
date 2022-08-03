from datetime import datetime

from volue.mesh import Connection, RatingCurveSegment, RatingCurveVersion
from volue.mesh.examples import _get_connection_info


def main(address, port, tls_root_cert):
    rating_curve_attribute_path = "Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.RatingCurveAtt"

    # Defining a time interval to read rating curve versions from.
    # If no time zone is provided then it will be treated as UTC.
    start_time = datetime(2008, 1, 1)
    end_time = datetime(2022, 1, 1)

    connection = Connection(address, port, tls_root_cert)
    with connection.create_session() as session:

        # First read the attribute using `get_attribute`.
        # We can get standard information like name, ID, tags, etc.
        rating_curve_attribute = session.get_attribute(
            rating_curve_attribute_path, full_attribute_info=True
        )
        print(
            f"Basic information about the rating curve attribute: {rating_curve_attribute}\n"
        )

        # Because the rating curve can potentially contain large amounts of data,
        # specialized methods exist to handle those values.
        versions = session.get_rating_curve_versions(
            target=rating_curve_attribute_path, start_time=start_time, end_time=end_time
        )

        print(
            (
                "Rating curve versions for time interval: "
                f"{start_time.strftime('%d.%m.%Y')} - {end_time.strftime('%d.%m.%Y')}:"
            )
        )
        for i, version in enumerate(versions):
            print(f"Version {i+1}:\n{version}")

        if len(versions) == 0 or len(versions[-1].x_value_segments) == 0:
            print("No rating curve versions found. Skip update.")
            return

        # Now for the last version update first segment and add a new one.
        versions[-1].x_value_segments[0].factor_b = -3.2
        versions[-1].x_value_segments.append(RatingCurveSegment(25, -1.1, 2.2, -3.3))
        session.update_rating_curve_versions(
            target=rating_curve_attribute_path,
            start_time=versions[
                0
            ].valid_from_time,  # use first version `valid_from_time` as start interval
            end_time=datetime.max,  # this is the last version
            new_versions=versions,
        )

        # Read once again.
        versions = session.get_rating_curve_versions(
            target=rating_curve_attribute_path, start_time=start_time, end_time=end_time
        )

        print("Updated rating curve versions:")
        for i, version in enumerate(versions):
            print(f"Version {i+1}:\n{version}")

        # Now lets replace last version with new one
        new_segments = [
            RatingCurveSegment(10, 1.1, 1.9, -3.5),
            RatingCurveSegment(21, 2.1, 1.8, -3.2),
        ]

        new_version = RatingCurveVersion(
            valid_from_time=datetime(2010, 6, 1),
            x_range_from=5.0,
            x_value_segments=new_segments,
        )

        session.update_rating_curve_versions(
            target=rating_curve_attribute_path,
            start_time=versions[
                -1
            ].valid_from_time,  # to replace old version use its `valid_from_time` as start interval
            end_time=datetime.max,  # this is the last version
            new_versions=[new_version],
        )

        # Read once again.
        versions = session.get_rating_curve_versions(
            target=rating_curve_attribute_path, start_time=start_time, end_time=end_time
        )

        print("Updated for the second time rating curve versions:")
        for i, version in enumerate(versions):
            print(f"Version {i+1}:\n{version}")

        # to commit your changes you need to call:
        # session.commit()


if __name__ == "__main__":
    args = _get_connection_info()
    main(*args)
