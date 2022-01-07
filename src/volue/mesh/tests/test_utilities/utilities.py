from volue.mesh import Timeseries
import pyarrow as pa
from datetime import datetime, timezone
import uuid
import subprocess
import sys
import socket
from dataclasses import dataclass


@dataclass()
class TestOwnedObject:
    id: uuid.UUID


@dataclass()
class TestTimeseriesEntry(TestOwnedObject):
    """Class for containing timeseries data points"""


@dataclass()
class TestTimeseries(TestOwnedObject):
    """Class for representing a meta information about timeseries points in the resource layer of mesh.
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
    """Class for representing a meta information about timeseries points in a physical mesh model.
        Inside Mesh this is referred to as TimeseriesAttribute.
        A timeseries attribute has a definition and either a calculation or a reference.
        A calculation has expression(s) that calculates the timeseries data points.
        A reference is a pointer to a timeseries entry which contains the data points.

        Note: id's for the attribute are generated at model generation
    """
    path: str
    # if reference:
    timeseries: TestTimeseries  # timeseriesEntry_ in PDCTimeseriesDynamicSourceData->PDCTimeseriesSourceData->PDCAttributeElementData->PDCNamedElementData->PDCElementData->PDCOwnedObjectData
    # if calculation:
    local_expression: str  # source_ in PDCTimeseriesCalculationData->PDCTimeseriesDynamicSourceData->PDCTimeseriesSourceData->PDCAttributeElementData->PDCNamedElementData->PDCElementData->PDCOwnedObjectData
    template_expression: str
    model: str
    silo: str = "Model"
    kind = "TimeseriesAttribute"


def is_port_responding(host: str, port: int):
    """Helper function to check if a socket will respond to a connect."""
    args = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    for family, socktype, proto, canonname, sockaddr in args:
        s = socket.socket(family, socktype, proto)
        try:
            s.connect(sockaddr)
        except socket.error:
            return False
        else:
            s.close()
            return True


def run_example_script(path, address, port, secure_connection):
    """Helper function to run an example script."""
    p = subprocess.Popen(
        [sys.executable, path, address, str(port), str(secure_connection)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdoutdata, stderrdata = p.communicate()
    exit_code = p.returncode
    assert exit_code == 0, f"{stderrdata} {stdoutdata}"


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
        unit_of_measurement="",
        path='/SimpleThermalTestResourceCatalog/',
        name="plantTimeSeriesRaw",
        entries=[timeseries_entry_1]
    )

    full_name = timeseries.silo + timeseries.path + timeseries.name
    return timeseries, full_name


def get_timeseries_1():
    """
    Timeseries with timeseries key.
    StorageType: Classic
    Kind: Timeseries with 1 TimeseriesEntry
    """
    timeseries_entry_1 = TestTimeseriesEntry(
        id=uuid.UUID("00000004-0002-0000-0000-000000000000")
    )
    timeseries = TestTimeseries(
        id=uuid.UUID("00000003-0002-0000-0000-000000000000"),
        timeseries_key=2,
        temporary=False,
        curve=Timeseries.Curve.UNKNOWN,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement="SomeUnit1",
        path='/SimpleThermalTestResourceCatalog/',
        name="chimney1TimeSeriesRaw",
        entries=[timeseries_entry_1]
    )

    full_name = timeseries.silo + timeseries.path + timeseries.name
    return timeseries, full_name


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
    # utc_time - [pa.date64] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]
    arrays = [
        pa.array([int(datetime(2016, 1, 1, 2, 0, 0, tzinfo=timezone.utc).timestamp() * 1000),
                 int(datetime(2016, 1, 1, 3, 0, 0, tzinfo=timezone.utc).timestamp() * 1000),
                 int(datetime(2016, 1, 1, 4, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
                  ]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0])]
    modified_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    full_name = timeseries.silo + timeseries.path + timeseries.name
    start_time = datetime(2016, 1, 1, 1, 0, 0)
    end_time = datetime(2016, 1, 1, 9, 0, 0)
    return timeseries, start_time, end_time, modified_table, full_name


def get_timeseries_attribute_1():
    """
    Timeseries attribute with calculation expression but no timeseries entry.
    Attribute: TsCalcAtt (generated guid)
    Entry: None
    Kind: TimeseriesAttribute with a TimeseriesCalculation.
    """
    timeseries_attribute = TestTimeseriesAttribute(
        id=None,  # Unknown because it's generated when the test model is generated
        path="/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1.TsCalcAtt",
        timeseries=None,
        local_expression="",
        template_expression=r"""@PDLOG(12004, 'TEST') 
##= @d('.DblAtt') + @t('.TsRawAtt') + @SUM(@D('PlantToPlantRef.DblAtt'))

""",
        model='PowerSystem',
        silo="Model"
    )
    full_path = timeseries_attribute.silo + timeseries_attribute.path
    return timeseries_attribute, full_path


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


