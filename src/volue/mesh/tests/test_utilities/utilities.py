"""
Utility functions used by tests
"""

from dataclasses import dataclass
from datetime import datetime
import math
import uuid

import pyarrow as pa

from volue.mesh import AttributeBase, Object, Timeseries, TimeseriesResource


class AttributeForTesting(AttributeBase):
    """
    Redefinition of AttributeBase class, we are NOT calling super().__init__(),
    but only define ID and path fields needed for unit tests.

    AttributeBase itself requires proto attribute to be initialized.
    """
    def __init__(self):
        self.id = uuid.uuid4()
        self.path = "test_attribute_path"


class ObjectForTesting(Object):
    """
    Redefinition of Object class, we are NOT calling super().__init__(),
    but only define ID and path fields needed for unit tests.

    Object itself requires to define complete list of fields, whereas we
    need only 2 of them in unit tests.
    """
    def __init__(self):
        self.id = uuid.uuid4()
        self.path = "test_object_path"


@dataclass()
class TestOwnedObject:
    """Class for containing a link to an owned object id"""
    id: uuid.UUID


@dataclass()
class TestTimeseriesEntry(TestOwnedObject):
    """Class for containing timeseries data points"""


@dataclass()
class TestTimeseries(TestOwnedObject):
    """Class for representing meta information about timeseries points in the resource layer of mesh.
    Inside Mesh this is referred to as Timeseries.
    """
    timeseries_key: int
    unit_of_measurement: str  # unitOfMeasurement_ in PDCTimeseriesAttributeDefinitionData
    path: str
    name: str
    temporary: bool
    curve: Timeseries.Curve
    resolution: Timeseries.Resolution
    entries: []
    silo: str = "Resource"
    kind = "Timeseries"


@dataclass()
class TestTimeseriesAttribute(TestOwnedObject):
    """Class for representing meta information about timeseries points in a physical mesh model.
        Inside Mesh this is referred to as TimeseriesAttribute.
        A timeseries attribute has a definition and either a calculation or a reference.
        A calculation has expression(s) that calculates the timeseries data points.
        A reference is a pointer to a timeseries entry which contains the data points.

        Note: id's for the attribute are generated at model generation
    """
    path: str
    # if reference:
    # timeseriesEntry_ in
    # PDCTimeseriesDynamicSourceData->PDCTimeseriesSourceData->PDCAttributeElementData->PDCNamedElementData->PDCElementData->PDCOwnedObjectData
    timeseries: TestTimeseries
    # if calculation:
    # source_ in
    # PDCTimeseriesCalculationData->PDCTimeseriesDynamicSourceData->PDCTimeseriesSourceData->PDCAttributeElementData->PDCNamedElementData->PDCElementData->PDCOwnedObjectData
    local_expression: str
    template_expression: str
    model: str
    silo: str = "Model"
    kind = "TimeseriesAttribute"


def get_timeseries_0():
    """
    Timeseries with timeseries key.
    StorageType: Mesh
    Kind: Timeseries with 1 TimeseriesEntry
    """
    timeseries_entry_1 = TestTimeseriesEntry(
        id=uuid.UUID("00000004-0001-0000-0000-000000000000")
    )
    timeseries = TestTimeseries(
        id=uuid.UUID("00000003-0001-0000-0000-000000000000"),
        timeseries_key=0,  # mesh timeseries does not have timeseries_key
        temporary=False,
        curve=Timeseries.Curve.PIECEWISELINEAR,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement="SomeUnit2",
        path='/SimpleThermalTestResourceCatalog/',
        name="plantTimeSeriesRaw",
        entries=[timeseries_entry_1]
    )

    full_name = timeseries.silo + timeseries.path + timeseries.name
    return timeseries, full_name


def get_physical_timeseries():
    """
    Physical time series from SimpleThermalModel test model.
    """
    ts_name = "chimney2TimeSeriesRaw"
    test_timeseries = TimeseriesResource(
        timeseries_key=3,
        temporary=False,
        curve_type=Timeseries.Curve.PIECEWISELINEAR,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement="Unit2",
        path=f"Resource/SimpleThermalTestResourceCatalog/{ts_name}",
        name=ts_name,
        virtual_timeseries_expression=""
    )
    return test_timeseries


def get_virtual_timeseries():
    """
    Virtual time series from SimpleThermalModel test model.
    """
    ts_name = "simpleVtsTimeseries"
    test_timeseries = TimeseriesResource(
        timeseries_key=4,
        temporary=False,
        curve_type=Timeseries.Curve.PIECEWISELINEAR,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement="",
        path=f"Resource/SimpleThermalTestResourceCatalog/{ts_name}",
        name=ts_name,
        virtual_timeseries_expression="## = 5\n"
    )
    return test_timeseries


def get_timeseries_2():
    """
    Timeseries with timeseries key.
    StorageType: Classic
    Kind: Timeseries with 1 TimeseriesEntry
    # TODO: make this one have 2 entries?
    """
    timeseries_entry_1 = TestTimeseriesEntry(
        id=uuid.UUID("00000004-0003-0000-0000-000000000000")
    )
    timeseries = TestTimeseries(
        id=uuid.UUID("00000003-0003-0000-0000-000000000000"),
        timeseries_key=3,
        temporary=False,
        curve=Timeseries.Curve.PIECEWISELINEAR,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement="SomeUnit1",
        path='/SimpleThermalTestResourceCatalog/',
        name="chimney2TimeSeriesRaw",
        entries=[timeseries_entry_1]
    )

    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.timestamp('ms')] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]
    arrays = [pa.array([datetime(2016, 1, 1, 1, 0, 0), datetime(2016, 1, 1, 2, 0, 0), datetime(2016, 1, 1, 3, 0, 0)]),
              pa.array([0, 0, 0]),
              pa.array([0.0, 10.0, 1000.0])]
    modified_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    full_name = timeseries.silo + timeseries.path + timeseries.name
    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    return timeseries, start_time, end_time, modified_table, full_name


def verify_timeseries_2(reply_timeseries: Timeseries):
    """
    Verify if all time series properties and data have expected values.
    """
    assert type(reply_timeseries) is Timeseries
    assert reply_timeseries.number_of_points == 9
    # check timestamps
    utc_date = reply_timeseries.arrow_table[0]
    for count, item in enumerate(utc_date):
        assert item.as_py() == datetime(2016, 1, 1, count+1, 0)
    # check flags
    flags = reply_timeseries.arrow_table[1]
    assert flags[3].as_py() == Timeseries.PointFlags.NOT_OK.value | Timeseries.PointFlags.MISSING.value
    for number in [0, 1, 2, 4, 5, 6, 7, 8]:
        assert flags[number].as_py() == Timeseries.PointFlags.OK.value
    # check values
    values = reply_timeseries.arrow_table[2]
    values[3].as_py()
    assert math.isnan(values[3].as_py())
    for number in [0, 1, 2, 4, 5, 6, 7, 8]:
        assert values[number].as_py() == (number + 1) * 100


def get_timeseries_attribute_2():
    """
    Timeseries attribute with timeseries entry.
    Attribute: TsRawAtt (generated guid)
    Timeseries: plantTimeseriesRaw (00000003-0001-0000-0000-000000000000)
    Entry: planTimeseriesRaw(0) (00000004-0001-0000-0000-000000000000)
    Kind: TimeseriesAttribute with a TimeseriesReference.
    """
    timeseries, _ = get_timeseries_0()
    timeseries_attribute = TestTimeseriesAttribute(
        id=None,  # Unknown because it's generated when the test model is generated
        path='/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.TsRawAtt',
        timeseries=timeseries,
        local_expression="",
        template_expression="",
        model='SimpleThermalTestModel',
        silo="Model"
    )
    full_path = timeseries_attribute.silo + timeseries_attribute.path
    return timeseries_attribute, full_path
