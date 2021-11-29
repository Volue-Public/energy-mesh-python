from volue.mesh import Timeseries
import pyarrow as pa
from datetime import datetime
import uuid
import subprocess
import sys
import socket
from dataclasses import dataclass


@dataclass()
class TestOwnedObject:
    id: uuid.UUID


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
    silo: str = "Resource"
    kind = "Timeseries"


@dataclass()
class TestTimeseriesAttribute(TestOwnedObject):
    """Class for representing a meta information about timeseries points in a physical mesh model.
        Inside Mesh this is referred to as TimeseriesAttribute.
    """
    path: str
    entry: TestTimeseries  # timeseriesEntry_ in PDCTimeseriesDynamicSourceData->PDCTimeseriesSourceData->PDCAttributeElementData->PDCNamedElementData->PDCElementData->PDCOwnedObjectData
    local_expression: str  # source_ in PDCTimeseriesCalculationData->PDCTimeseriesDynamicSourceData->PDCTimeseriesSourceData->PDCAttributeElementData->PDCNamedElementData->PDCElementData->PDCOwnedObjectData
    template_expression: str
    model: str
    silo: str = "Model"
    kind = "TimeseriesAttribute"


# ------------------------------------------------------------------------------

# TODO convert this into  get_timeseries_data_2()
class TestTimeseriesEntry:
    """
    A resource.
    Kind: TimeseriesEntry
    Database: Eagle
    """

    def __init__(self, full_name, guid, timskey, start_time, end_time, database):
        self.full_name = full_name
        self.guid = guid
        self.timskey = timskey
        self.start_time = start_time
        self.end_time = end_time
        self.database = database


test_timeseries_entry = TestTimeseriesEntry(
    "Resource/Wind Power/WindPower/WPModel/WindProdForec(0)",
    "3f1afdd7-5f7e-45f9-824f-a7adc09cff8e",
    201503,
    datetime(year=2016, month=5, day=1, hour=0, minute=0),
    datetime(year=2016, month=5, day=14, hour=0, minute=0),
    "eagle"
)


# ------------------------------------------------------------------------------


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


def get_timeseries_entry_1():
    """
    A resource.
    Kind: Timeseries
    Database: Eagle
    """
    timeseries_entry = TestTimeseries(
        id=uuid.UUID("5a261b5a-b4ef-4820-bead-b11577562e37"),
        timeseries_key=377702,
        temporary=False,
        curve=Timeseries.Curve.STAIRCASESTARTOFSTEP,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement="euro per mega watt hours",
        path='/Customer_case/A2A/Market/IT_ElSpot/',
        name="LastAuctionAvailable"
    )

    full_name = timeseries_entry.silo + timeseries_entry.path + timeseries_entry.name
    return timeseries_entry, full_name


def get_timeseries_entry_2():
    """
    A resource.
    Kind: Timeseries
    Database: Eagle
    """
    timeseries_entry = TestTimeseries(
        id=uuid.UUID("c34cbee8-ff43-43e8-86ae-170786a30eec"),
        timeseries_key=201503,
        temporary=False,
        curve=Timeseries.Curve.STAIRCASESTARTOFSTEP,
        resolution=Timeseries.Resolution.HOUR,
        unit_of_measurement="mega watt hours per hour",
        path="/Wind Power/WindPower/WPModel/",
        name="WindProdForec"
    )

    # Mesh data is organized as an Arrow table with the following schema:
    # utc_time - [pa.date64] as a UTC Unix timestamp expressed in milliseconds
    # flags - [pa.uint32]
    # value - [pa.float64]
    arrays = [
        pa.array([1462060800000, 1462064400000, 1462068000000]),
        pa.array([0, 0, 0]),
        pa.array([0.0, 10.0, 1000.0])]
    modified_table = pa.Table.from_arrays(arrays, schema=Timeseries.schema)
    full_name = timeseries_entry.silo + timeseries_entry.path + timeseries_entry.name
    start_time = datetime(2016, 5, 1)
    end_time = datetime(2016, 5, 14)
    return timeseries_entry, start_time, end_time, modified_table, full_name


def get_timeseries_attribute_1():
    """Timeseries attribute with calculation expression but no timeseries entry"""
    timeseries_attribute = TestTimeseriesAttribute(
        id=uuid.UUID("6671cc8b-df4b-4b20-912e-103cce1bc3cf"),
        path="/PowerSystem/Mesh.MeshCountry/Norway.Income",
        entry=None,
        local_expression="",
        template_expression="##=@t('CountryHydroPower.Income')\n",
        model='PowerSystem',
        silo="Model"
    )
    full_path = timeseries_attribute.silo + timeseries_attribute.path
    return timeseries_attribute, full_path


def get_timeseries_attribute_2():
    """Timeseries attribute with calculation expression and a timeseries entry"""
    timeseries_entry, _ = get_timeseries_entry_1()
    timeseries_attribute = TestTimeseriesAttribute(
        id=uuid.UUID("4001d450-61ec-4789-85cd-3d6d17d8f845"),
        path="/POMAtest01/Mesh.has_Market/Markets.has_EnergyMarkets/IT_ElSpot.LastAuctionAvailable",
        entry=timeseries_entry,
        local_expression="",
        template_expression="",
        model='POMAtest01',
        silo="Model"
    )
    full_path = timeseries_attribute.silo + timeseries_attribute.path
    return timeseries_attribute, full_path

