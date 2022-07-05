import abc
import dateutil
import typing
from typing import List, Optional, Type, Tuple, Union
import uuid
from datetime import datetime

from google import protobuf

from ._attribute import AttributeBase, TimeseriesAttribute, SIMPLE_TYPE_OR_COLLECTION, SIMPLE_TYPE
from ._common import (AttributesFilter, MeshObjectId, XyCurve, XySet,
                      RatingCurveSegment, RatingCurveVersion,
                      _to_proto_attribute_masks, _to_proto_guid, _to_proto_mesh_id,
                      _to_proto_curve_type, _datetime_to_timestamp_pb2, _to_protobuf_utcinterval)
from ._object import Object
from ._timeseries import Timeseries
from ._timeseries_resource import TimeseriesResource

from .calc.forecast import ForecastFunctions
from.calc.history import HistoryFunctions
from.calc.statistical import StatisticalFunctions
from.calc.transform import TransformFunctions

from .proto.core.v1alpha import core_pb2, core_pb2_grpc


class Session(abc.ABC):
    """Represents a session to a Mesh server."""

    def __init__(
            self,
            mesh_service: core_pb2_grpc.MeshServiceStub,
            session_id: Optional[uuid.UUID] = None):
        """
        Initialize a session object for working with the Mesh server.

        Args:
            mesh_service: gRPC generated Mesh service to communicate with
                the :doc:`Mesh server <mesh_server>`.
            session_id: ID of the session you are (or want to be) connected to.
        """
        self.session_id: uuid = session_id
        self.mesh_service: core_pb2_grpc.MeshServiceStub = mesh_service


    @abc.abstractmethod
    def open(self) -> None:
        """
        Request to open a session on the Mesh server.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def close(self) -> None:
        """
        Request to close a session on the Mesh server.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed

        Note:
            This method does not wait for the Mesh server to finish closing
            the session on the Mesh server.
        """

    @abc.abstractmethod
    def rollback(self) -> None:
        """
        Discard changes in the :doc:`Mesh session <mesh_session>`.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def commit(self) -> None:
        """
        Commit changes made in the :doc:`Mesh session <mesh_session>` to the shared storage.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def read_timeseries_points(
            self,
            start_time: datetime,
            end_time: datetime,
            mesh_object_id: MeshObjectId) -> Timeseries:
        """
        Reads time series points for
        the specified time series in the given interval.
        For information about `datetime` arguments and time zones refer to
        :ref:`mesh_client:Date times and time zones`.

        Args:
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval
            mesh_object_id: unique way of identifying a Mesh object that contains a time series.
                Using either a  Universal Unique Identifier for Mesh objects, a path in the 
                :ref:`Mesh model <mesh_model>` or a integer that only applies
                to a specific physical or virtual time series.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
            RuntimeError: Error message raised if the input is not valid
            TypeError: Error message raised if the returned result from the request is not as expected
        """

    @abc.abstractmethod
    def write_timeseries_points(
            self,
            timeseries: Timeseries) -> None:
        """
        Writes time series points for the specified time series in the given interval.

        Args:
            time series (:class:`volue.mesh.Timeseries`): The modified time series

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def get_object(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path:  Optional[str] = None,
            full_attribute_info:  bool = False,
            attributes_filter: Optional[AttributesFilter] = None) -> Object:
        """
        Request information associated with a Mesh object from the Mesh model.
        Specify either `object_id` or `object_path` to a Mesh object.

        Args:
            object_id: Universal Unique Identifier of the Mesh object.
            object_path: Path in the :ref:`Mesh model <mesh_model>`
                of the Mesh object. See:
                :ref:`objects and attributes paths <mesh_object_attribute_path>`.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object will be returned, otherwise only name,
                path, ID and value(s).
            attributes_filter: Filtering criteria for what attributes owned by
                object(s) should be returned. By default all attributes are returned.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def search_for_objects(
            self,
            query: str,
            start_object_id: Optional[uuid.UUID] = None,
            start_object_path: Optional[str] = None,
            full_attribute_info: bool = False,
            attributes_filter: Optional[AttributesFilter] = None) -> List[Object]:
        """
        Use the :doc:`Mesh search language <mesh_search>` to find Mesh objects
        in the Mesh model. Specify either `start_object_id` or
        `start_object_path` to an object where the search query should start from.

        Args:
            query: A search formulated using the :doc:`Mesh search language <mesh_search>`.
            start_object_id: Start searching at the object with the 
                Universal Unique Identifier for Mesh objects.
            start_object_path: Start searching at the path in the
                :ref:`Mesh model <mesh_model>`.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object(s) will be returned, otherwise only name,
                path, ID and value(s).
            attributes_filter: Filtering criteria for what attributes owned by
                object(s) should be returned. By default all attributes are returned.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def create_object(
            self,
            name: str,
            owner_attribute_id: Optional[uuid.UUID] = None,
            owner_attribute_path: Optional[str] = None) -> Object:
        """
        Create new Mesh object in the Mesh model.
        Owner of the new object must be a relationship attribute of Object Collection type.
        E.g.: for `SomePowerPlant1` object with path:
        - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1

        Owner will be the `ThermalPowerToPlantRef` attribute.

        Args:
            name: Name for the new object to create.
            owner_attribute_id: Universal Unique Identifier of the owner which
                is a relationship attribute of Object Collection type.
            owner_attribute_path: Path in the :ref:`Mesh model <mesh_model>`
                of the owner which is a relationship attribute of Object Collection type
                (object value type = "ElementCollectionAttributeDefinition").
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.

        Returns:
            Created object with all attributes (no mask applied) and basic
            information: name, path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def update_object(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path: Optional[str] = None,
            new_name: Optional[str] = None,
            new_owner_attribute_id: Optional[uuid.UUID] = None,
            new_owner_attribute_path: Optional[str] = None) -> None:
        """
        Update an existing Mesh object in the Mesh model.
        New owner of the object must be a relationship attribute of Object Collection type.
        E.g.: for `SomePowerPlant1` object with path:
        - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1

        Args:
            object_id: Universal Unique Identifier of the Mesh object to be updated.
            object_path: Path in the :ref:`Mesh model <mesh_model>`
                of the Mesh object to be updated.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.
            new_name: New name for the object.
            new_owner_attribute_id: Universal Unique Identifier of the new owner which
                is a relationship attribute of Object Collection type.
            new_owner_attribute_path: Path in the :ref:`Mesh model <mesh_model>`
                of the new owner which is a relationship attribute of Object Collection type
                (object value type = "ElementCollectionAttributeDefinition").
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def delete_object(
            self,
            object_id: Optional[uuid.UUID] = None,
            object_path: Optional[str] = None,
            recursive_delete: bool = False) -> None:
        """
        Delete an existing Mesh object in the Mesh model.

        Args:
            object_id: Universal Unique Identifier of the object to be deleted.
            object_path: Path in the :ref:`Mesh model <mesh_model>`
                of the object to be deleted.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.
            recursive_delete: If set then all child objects
                (owned by the object to be deleted) in the model will also be deleted.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def get_attribute(
            self,
            attribute_id: Optional[uuid.UUID] = None,
            attribute_path: Optional[str] = None,
            full_attribute_info: bool = False) -> Type[AttributeBase]:
        """
        Request information associated with a Mesh :ref:`attribute <mesh_attribute>` from the Mesh model.
        Specify either `attribute_id` or `attribute_path` to a Mesh attribute.

        Args:
            attribute_id: Universal Unique Identifier of the attribute to be retrieved.
            attribute_path: Path in the :ref:`Mesh model <mesh_model>`
                of the attribute to be retrieved.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attribute will be returned, otherwise only name, path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def get_timeseries_attribute(
        self,
        attribute_id: uuid.UUID = None,
        attribute_path: str = None,
        full_attribute_info: bool = False) -> TimeseriesAttribute:
        """
        Request information associated with a Mesh :ref:`time series attribute <mesh_attribute>` from the Mesh model.
        Specify either `attribute_id` or `attribute_path` to a Mesh time series attribute.

        Args:
            attribute_id: Universal Unique Identifier of the attribute to be retrieved.
            attribute_path: Path in the :ref:`Mesh model <mesh_model>`
                of the attribute to be retrieved.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attribute will be returned, otherwise only name, path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
            ValueError: Raised if given attribute ID or path points to an attribute of
                different type than `TimeseriesAttribute`
        """

    @abc.abstractmethod
    def search_for_attributes(
            self,
            query: str,
            start_object_id: Optional[uuid.UUID] = None,
            start_object_path: Optional[str] = None,
            full_attribute_info: bool = False) -> List[Type[AttributeBase]]:
        """
        Use the :doc:`Mesh search language <mesh_search>` to find Mesh
        :ref:`attributes <mesh_attribute>` in the Mesh model.
        Specify either `start_object_id` or `start_object_path` to an object
        where the search query should start from.

        Args:
            query: A search formulated using the :doc:`Mesh search language <mesh_search>`.
            start_object_id: Start searching at the object with the 
                Universal Unique Identifier for Mesh objects.
            start_object_path: Start searching at the path in the
                :ref:`Mesh model <mesh_model>`.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object(s) will be returned, otherwise only name,
                path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def search_for_timeseries_attributes(
            self,
            query: str,
            start_object_id: Optional[uuid.UUID] = None,
            start_object_path: Optional[str] = None,
            full_attribute_info: bool = False) -> List[TimeseriesAttribute]:
        """
        Use the :doc:`Mesh search language <mesh_search>` to find Mesh
        :ref:`time series attributes <mesh_attribute>` in the Mesh model.
        Specify either `start_object_id` or `start_object_path` to an object
        where the search query should start from.

        Args:
            query: A search formulated using the :doc:`Mesh search language <mesh_search>`.
            start_object_id: Start searching at the object with the
                Universal Unique Identifier for Mesh objects.
            start_object_path: Start searching at the path in the
                :ref:`Mesh model <mesh_model>`.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object(s) will be returned, otherwise only name,
                path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def update_simple_attribute(
            self,
            value: SIMPLE_TYPE_OR_COLLECTION,
            attribute_id: Optional[uuid.UUID] = None,
            attribute_path: Optional[str] = None) -> None:
        """
        Update an existing Mesh simple attribute's value in the Mesh model.
        Simple attribute is a singular type or collection of the following types:
        - double (float in Python)
        - integer (int in Python)
        - boolean (bool in Python)
        - string (str in Python)
        - UTC time (datetime in Python)

        Args:
            value: New simple attribute value. It can be one of following simple types:
                bool, float, int, str, datetime or a list of simple types.
            attribute_id: Universal Unique Identifier of the Mesh attribute to be updated.
            attribute_path: Path in the :ref:`Mesh model <mesh_model>`
                of the Mesh attribute which value is to be updated.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def update_timeseries_attribute(
            self,
            new_local_expression: str = None,
            new_timeseries_resource_key: int = None,
            attribute_id: Optional[uuid.UUID] = None,
            attribute_path: Optional[str] = None) -> None:
        """
        Update meta data of an existing Mesh time series attribute's in the Mesh model.

        Args:
            new_local_expression: New local expression.
            new_timeseries_resource_key: time series key of a new time series resource
                (physical or virtual) to connect to the time series attribute. To disconnect
                time series attribute from already connected time series resource set this
                argument to 0.
            attribute_id: Universal Unique Identifier of the Mesh attribute to be updated.
            attribute_path: Path in the :ref:`Mesh model <mesh_model>`
                of the Mesh attribute which value is to be updated.
                See: :ref:`objects and attributes paths <mesh_object_attribute_path>`.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def get_timeseries_resource_info(
            self,
            timeseries_key: int) -> TimeseriesResource:
        """
        Request information (like curve type or resolution) associated with
        a physical or virtual time series.

        Args:
            timeseries_key: integer that only applies to a specific physical or
                virtual time series.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def update_timeseries_resource_info(
            self,
            timeseries_key: int,
            new_curve_type: Timeseries.Curve = None,
            new_unit_of_measurement: str = None) -> None:
        """
        Update information associated with a physical or virtual time series.

        Args:
            timeseries_key: integer that only applies to a specific physical or
                virtual time series.
            new_curve_type: set new  curve type.
            new_unit_of_measurement: set new  unit of measurement.

        Note:
            Specify which ever of the new_* fields you want to update.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    @abc.abstractmethod
    def forecast_functions(
            self,
            relative_to: MeshObjectId,
            start_time: datetime,
            end_time: datetime) -> ForecastFunctions:
        """Access to :ref:`mesh_functions:Forecast` functions.

        Args:
            relative_to: a Mesh object to perform actions relative to
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Returns:
            object containing all forecast functions
        """

    @abc.abstractmethod
    def history_functions(
            self,
            relative_to: MeshObjectId,
            start_time: datetime,
            end_time: datetime) -> HistoryFunctions:
        """Access to :ref:`mesh_functions:History` functions.

        Args:
            relative_to: a Mesh object to perform actions relative to
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Returns:
           object containing all history functions
        """

    @abc.abstractmethod
    def statistical_functions(
            self,
            relative_to: MeshObjectId,
            start_time: datetime,
            end_time: datetime) -> StatisticalFunctions:
        """Access to :ref:`mesh_functions:Statistical` functions.

        Args:
            relative_to: a Mesh object to perform actions relative to
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Returns:
            object containing all statistical functions
        """

    @abc.abstractmethod
    def transform_functions(
            self,
            relative_to: MeshObjectId,
            start_time: datetime,
            end_time: datetime) -> TransformFunctions:
        """Access to :ref:`mesh_functions:Transform` functions.

        Args:
            relative_to: a Mesh object to perform actions relative to
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Returns:
            object containing all transformation functions
        """

    @abc.abstractmethod
    def get_xy_sets(
            self, target: typing.Union[uuid.UUID, str],
            start_time: typing.Optional[datetime], end_time: typing.Optional[datetime],
            versions_only: bool
    ) -> typing.List[XySet]:
        """Get zero or more XY-sets from an XY-set attribute on the server.

        An XY-set attribute is either versioned, with a kind
        :code:`XYZSeriesAttribute`, or unversioned, with a kind
        :code:`XYSetAttribute`.

        Args:
            target: the GUID or the path of an XY-set attribute.

            start_time: the (inclusive) start of the interval to retrieve XY
                sets in for versioned XY-set attributes. Must be :code:`None`
                for unversioned attributes.

            end_time: the (exclusive) end of the interval to retrieve XY sets
                in for versioned XY-set attributes. Must be :code:`None` for
                unversioned attributes.

            versions_only: don't retrieve XY-set curves, only :code:`valid_from_time`.

        Returns:
            A list of :class:`XySet`. The list always contains one element for
            unversioned attributes, and zero or more elements for versioned
            attributes.

            For versioned attributes the method will return all XY sets that
            are valid in :code:`[start_time, end_time)`. This may include the
            last XY set that started its validity period before the interval.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
            TypeError: on invalid arguments (see above).

        See Also:
            :doc:`mesh_xy_sets`
        """

    @abc.abstractmethod
    def update_xy_sets(
            self, target: typing.Union[uuid.UUID, str],
            start_time: typing.Optional[datetime], end_time: typing.Optional[datetime],
            new_xy_sets: typing.List[XySet]
    ) -> None:
        """Replace XY sets on an XY-set attribute on the server.

        An XY-set attribute is either versioned, with a kind
        :code:`XYZSeriesAttribute`, or unversioned, with a kind
        :code:`XYSetAttribute`.

        When applied to an unversioned attribute the update_xy_sets operation
        removes the existing XY-set, and replaces it with the contents of
        :code:`xy_sets`, which must contain zero or one XY-set.

        When applied to a versioned attribute the operation deletes all
        versions in the interval :code:`[start_time, end_time)`, and inserts
        the new versions in :code:`xy_sets`.

        Args:
            target: the GUID or the path of an XY-set attribute.
            start_time: the (inclusive) start of the edit interval. Must be
                None for unversioned XY-set attributes.
            end_time: the (exclusive) end of the edit interval. Must be
                None for unversioned XY-set attributes.
            new_xy_sets: the list of XY-sets to insert. Must contain zero or
                one element for unversioned attributes. All elements must be
                within :code:`[start_time, end_time)` for versioned attributes.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
            TypeError: on invalid arguments (see above).

        See Also:
            :doc:`mesh_xy_sets`
        """

    @abc.abstractmethod
    def get_rating_curve_versions(
        self,
        target: Union[uuid.UUID, str],
        start_time: datetime,
        end_time: datetime,
        versions_only: bool = False
    ) -> List[RatingCurveVersion]:
        """Get rating curve versions from an rating curve attribute on the server.

        Args:
            target: the ID or the path of an rating curve attribute.
            start_time: the (inclusive) start of the interval to retrieve
                rating curve versions.
            end_time: the (exclusive) end of the interval to retrieve
                rating curve versions.
            versions_only: retrieve only `valid_from_time` timestamps for each
                version, no other data like segments will be retrieved.

        Returns:
            A list of :class:`RatingCurveVersion`.

            The method will return all rating curve versions that are valid in
            `[start_time, end_time)` interval. This may include the last rating
            curve version that started its validity period before the interval.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.

        See Also:
            :doc:`mesh_rating_curve`
        """

    @abc.abstractmethod
    def update_rating_curve_versions(
        self,
        target: Union[uuid.UUID, str],
        start_time: datetime,
        end_time: datetime,
        new_versions: List[RatingCurveVersion]
    ) -> None:
        """Replace rating curve versions on an rating curve attribute on the server.

        The update operation deletes all versions in the
        `[start_time, end_time)` interval, and inserts the new versions.

        Args:
            target: the ID or the path of an rating curve attribute.
            start_time: the (inclusive) start of the edit interval.
            end_time: the (exclusive) end of the edit interval.
            new_versions: the list of rating curve versions to insert.
                All versions must be within `[start_time, end_time)` interval.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.

        See Also:
            :doc:`mesh_rating_curve`
        """


    def _get_xy_sets_impl(
            self, target: typing.Union[uuid.UUID, str],
            start_time: datetime, end_time: datetime,
            versions_only: bool
    ) -> typing.Generator[typing.Any, core_pb2.GetXySetsResponse, None]:
        """Generator implementation of get_xy_sets.

        Yields the protobuf request, receives the protobuf response, and yields
        the final result.
        """

        if (start_time is None) != (end_time is None):
            raise TypeError("start_time and end_time must both be None or both have a value")

        # FIXME: add convenience function based on decision in https://github.com/PowelAS/sme-mesh-python/pull/241.
        if isinstance(target, uuid.UUID):
            target = core_pb2.MeshId(id=_to_proto_guid(target))
        elif isinstance(target, str):
            target = core_pb2.MeshId(path=target)
        else:
            raise TypeError("target must be a uuid.UUID or str")

        if start_time is None or end_time is None:
            interval = None
        else:
            interval = _to_protobuf_utcinterval(start_time, end_time)

        request = core_pb2.GetXySetsRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=target,
            interval=interval,
            versions_only=versions_only
        )

        response = yield request

        def get_valid_from_time(proto: core_pb2.XySet):
            if proto.HasField("valid_from_time"):
                return proto.valid_from_time.ToDatetime(dateutil.tz.UTC)
            else:
                return None

        yield [XySet(get_valid_from_time(proto_xy_set),
                     [XyCurve(proto_curve.reference_value,
                              list(zip(proto_curve.x_values, proto_curve.y_values)))
                      for proto_curve in proto_xy_set.xy_curves])
               for proto_xy_set in response.xy_sets]

    def _prepare_update_xy_sets_request(
            self, target: typing.Union[uuid.UUID, str],
            start_time: datetime, end_time: datetime,
            new_xy_sets: typing.List[XySet]
    ) -> core_pb2.UpdateXySetsRequest:
        if (start_time is None) != (end_time is None):
            raise TypeError("start_time and end_time must both be None or both have a value")

        # FIXME: add convenience function based on decision in https://github.com/PowelAS/sme-mesh-python/pull/241.
        if isinstance(target, uuid.UUID):
            target = core_pb2.MeshId(id=_to_proto_guid(target))
        elif isinstance(target, str):
            target = core_pb2.MeshId(path=target)
        else:
            raise TypeError("target must be a uuid.UUID or str")

        if start_time is None or end_time is None:
            interval = None
        else:
            interval = _to_protobuf_utcinterval(start_time, end_time)

        def to_proto_xy_curve(curve: XyCurve) -> core_pb2.XyCurve:
            return core_pb2.XyCurve(reference_value=curve.z,
                                    x_values=[x for (x, _) in curve.xy],
                                    y_values=[y for (_, y) in curve.xy])

        def to_proto_xy_set(xy_set: XySet) -> core_pb2.XySet:
            valid_from_time = (None if xy_set.valid_from_time is None
                               else _datetime_to_timestamp_pb2(xy_set.valid_from_time))
            xy_curves = [to_proto_xy_curve(curve) for curve in xy_set.xy_curves]
            return core_pb2.XySet(valid_from_time=valid_from_time,
                                  xy_curves=xy_curves)

        xy_sets = [to_proto_xy_set(xy_set) for xy_set in new_xy_sets]

        request = core_pb2.UpdateXySetsRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=target,
            interval=interval,
            xy_sets=xy_sets
        )

        return request

    def _prepare_get_object_request(
            self,
            object_id: uuid.UUID,
            object_path: str,
            full_attribute_info: bool,
            attributes_filter: AttributesFilter) -> core_pb2.GetObjectRequest:
        """Create a gRPC `GetObjectRequest`"""

        try:
            object_mesh_id = _to_proto_mesh_id(id=object_id, path=object_path)
        except ValueError as e:
            raise ValueError("invalid object") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.GetObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=object_mesh_id,
                    attributes_masks=_to_proto_attribute_masks(attributes_filter),
                    attribute_view=attribute_view,
                )
        return request

    def _prepare_search_for_objects_request(
            self,
            query: str,
            start_object_id: uuid.UUID,
            start_object_path: str,
            full_attribute_info: bool,
            attributes_filter: AttributesFilter) -> core_pb2.SearchObjectsRequest:
        """Create a gRPC `SearchObjectsRequest`"""

        try:
            start_object_mesh_id = _to_proto_mesh_id(id=start_object_id, path=start_object_path)
        except ValueError as e:
            raise ValueError("invalid start object") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.SearchObjectsRequest(
                    session_id=_to_proto_guid(self.session_id),
                    start_object_id=start_object_mesh_id,
                    attributes_masks=_to_proto_attribute_masks(attributes_filter),
                    attribute_view=attribute_view,
                    query=query
                )
        return request

    def _prepare_create_object_request(
            self,
            name: str,
            owner_attribute_id: uuid.UUID,
            owner_attribute_path: str) -> core_pb2.CreateObjectRequest:
        """Create a gRPC `CreateObjectRequest`"""

        try:
            owner_mesh_id = _to_proto_mesh_id(id=owner_attribute_id, path=owner_attribute_path)
        except ValueError as e:
            raise ValueError("invalid owner") from e

        request = core_pb2.CreateObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    owner_id=owner_mesh_id,
                    name=name
                )
        return request

    def _prepare_update_object_request(
            self,
            object_id: uuid.UUID,
            object_path: str,
            new_name: str,
            new_owner_attribute_id: uuid.UUID,
            new_owner_attribute_path:str) -> core_pb2.UpdateObjectRequest:
        """Create a gRPC `UpdateObjectRequest`"""

        try:
            object_mesh_id = _to_proto_mesh_id(id=object_id, path=object_path)
        except ValueError as e:
            raise ValueError("invalid object to update") from e

        request = core_pb2.UpdateObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=object_mesh_id
                )

        fields_to_update = []

        # providing new owner is optional
        if new_owner_attribute_id is not None or new_owner_attribute_path is not None:
            try:
                new_owner_mesh_id = _to_proto_mesh_id(
                    id=new_owner_attribute_id, path=new_owner_attribute_path)
            except ValueError as e:
                raise ValueError("invalid new owner") from e
            
            request.new_owner_id.CopyFrom(new_owner_mesh_id)
            fields_to_update.append("new_owner_id")

        # providing new name is optional
        if new_name is not None:
            request.new_name = new_name
            fields_to_update.append("new_name")

        request.field_mask.CopyFrom(protobuf.field_mask_pb2.FieldMask(paths=fields_to_update))
        return request

    def _prepare_delete_object_request(
            self,
            object_id: uuid.UUID,
            object_path: str,
            recursive_delete: bool) -> core_pb2.DeleteObjectRequest:
        """Create a gRPC `DeleteObjectRequest`"""

        try:
            object_mesh_id = _to_proto_mesh_id(id=object_id, path=object_path)
        except ValueError as e:
            raise ValueError("invalid object") from e

        request = core_pb2.DeleteObjectRequest(
                    session_id=_to_proto_guid(self.session_id),
                    object_id=object_mesh_id,
                    recursive_delete=recursive_delete
                )
        return request

    def _prepare_get_attribute_request(
        self,
        attribute_id: uuid.UUID,
        attribute_path: str,
        full_attribute_info: bool) -> core_pb2.GetAttributeRequest:

        try:
            attribute_mesh_id = _to_proto_mesh_id(id=attribute_id, path=attribute_path)
        except ValueError as e:
            raise ValueError("invalid attribute") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.GetAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_id=attribute_mesh_id,
            attribute_view=attribute_view
        )

        return request

    def _prepare_search_attributes_request(
        self,
        start_object_id: uuid.UUID,
        start_object_path: str,
        query: str,
        full_attribute_info: bool) -> core_pb2.SearchAttributesRequest:

        try:
            start_object_mesh_id = _to_proto_mesh_id(id=start_object_id, path=start_object_path)
        except ValueError as e:
            raise ValueError("invalid start object") from e

        attribute_view = core_pb2.AttributeView.FULL if full_attribute_info else core_pb2.AttributeView.BASIC

        request = core_pb2.SearchAttributesRequest(
            session_id=_to_proto_guid(self.session_id),
            start_object_id=start_object_mesh_id,
            query=query,
            attribute_view=attribute_view
        )

        return request

    def _prepare_update_simple_attribute_request(
        self,
        attribute_id: uuid.UUID,
        attribute_path: str,
        value: SIMPLE_TYPE_OR_COLLECTION
    ) -> core_pb2.UpdateSimpleAttributeRequest:

        try:
            attribute_mesh_id = _to_proto_mesh_id(id=attribute_id, path=attribute_path)
        except ValueError as e:
            raise ValueError("invalid attribute to update") from e

        request = core_pb2.UpdateSimpleAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_id=attribute_mesh_id
        )

        new_singular_value, new_collection_values = self._to_update_attribute_request_values(value=value)

        if new_singular_value is not None:
            request.new_singular_value.CopyFrom(new_singular_value)

        if new_collection_values is not None:
            for value in new_collection_values:
                request.new_collection_values.append(value)

        return request

    def _prepare_update_timeseries_attribute_request(
        self,
        attribute_id: uuid.UUID,
        attribute_path: str,
        new_local_expression: str,
        new_timeseries_resource_key: int
    ) -> core_pb2.UpdateTimeseriesAttributeRequest:

        try:
            attribute_mesh_id = _to_proto_mesh_id(id=attribute_id, path=attribute_path)
        except ValueError as e:
            raise ValueError("invalid attribute to update") from e

        request = core_pb2.UpdateTimeseriesAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_id=attribute_mesh_id
        )

        fields_to_update = []
        if new_local_expression is not None:
            fields_to_update.append("new_local_expression")
            request.new_local_expression = new_local_expression

        if new_timeseries_resource_key is not None:
            fields_to_update.append("new_timeseries_resource_key")
            request.new_timeseries_resource_key = new_timeseries_resource_key

        request.field_mask.CopyFrom(protobuf.field_mask_pb2.FieldMask(paths=fields_to_update))
        return request

    def _to_proto_singular_attribute_value(
        self,
        v: SIMPLE_TYPE
    ) -> core_pb2.AttributeValue:
    
        att_value = core_pb2.AttributeValue()
        if type(v) is int:
            att_value.int_value = v
        elif type(v) is float:
            att_value.double_value = v
        elif type(v) is bool:
            att_value.boolean_value = v
        elif type(v) is str:
            att_value.string_value = v
        elif type(v) is datetime:
            att_value.utc_time_value.CopyFrom(_datetime_to_timestamp_pb2(v))
        else:
            raise RuntimeError("Not supported value type. Supported simple types are: boolean, float, int, str, datetime.")

        return att_value


    def _to_update_attribute_request_values(
        self,
        value: SIMPLE_TYPE_OR_COLLECTION
    ) -> Tuple[core_pb2.AttributeValue, List[core_pb2.AttributeValue]]:
        """
            Convert value supplied by the user to singular value/collection values
            expected by the protobuf request.
        """
        new_singular_value = None
        new_collection_values = None
        if type(value) is list:
            new_collection_values = []
            for v in value:
                att_value = self._to_proto_singular_attribute_value(v)
                new_collection_values.append(att_value)
        else:
            new_singular_value = self._to_proto_singular_attribute_value(value)

        return (new_singular_value, new_collection_values)


    def _prepare_update_timeseries_resource_request(
        self,
        timeseries_key: int,
        new_curve_type: Timeseries.Curve,
        new_unit_of_measurement: str
    ) -> core_pb2.UpdateTimeseriesResourceRequest:

        request = core_pb2.UpdateTimeseriesResourceRequest(
            session_id=_to_proto_guid(self.session_id),
            timeseries_resource_key=timeseries_key
        )

        fields_to_update = []
        if new_curve_type is not None:
            fields_to_update.append("new_curve_type")
            request.new_curve_type.CopyFrom(_to_proto_curve_type(new_curve_type))

        if new_unit_of_measurement is not None:
            fields_to_update.append("new_unit_of_measurement")
            request.new_unit_of_measurement = new_unit_of_measurement

        request.field_mask.CopyFrom(protobuf.field_mask_pb2.FieldMask(paths=fields_to_update))
        return request

    def _get_rating_curve_versions_impl(
            self,
            target: Union[uuid.UUID, str],
            start_time: datetime,
            end_time: datetime,
            versions_only: bool
    ) -> typing.Generator[typing.Any, core_pb2.GetRatingCurveVersionsResponse, None]:
        """Generator implementation of get_rating_curve_versions.

        Yields the protobuf request, receives the protobuf response, and yields
        the final result.
        """

        if isinstance(target, uuid.UUID):
            target = core_pb2.MeshId(id=_to_proto_guid(target))
        elif isinstance(target, str):
            target = core_pb2.MeshId(path=target)
        else:
            raise TypeError("target must be a uuid.UUID or str")

        if start_time is None or end_time is None:
            raise TypeError("start_time and end_time must both have a value")

        interval = _to_protobuf_utcinterval(start_time, end_time)

        request = core_pb2.GetRatingCurveVersionsRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=target,
            interval=interval,
            versions_only=versions_only
        )

        response = yield request

        # name of the field in proto file is a Python keyword
        # need to use `getattr` to get its value, see:
        # https://developers.google.com/protocol-buffers/docs/reference/python-generated#keyword-conflicts
        yield [RatingCurveVersion(
            x_range_from=proto_version.x_range_from,
            valid_from_time=getattr(proto_version, "from").ToDatetime(dateutil.tz.UTC),
            x_value_segments=[RatingCurveSegment(
                proto_segment.x_range_until,
                proto_segment.factor_a,
                proto_segment.factor_b,
                proto_segment.factor_c)
                      for proto_segment in proto_version.x_value_segments])
               for proto_version in response.versions]

    def _prepare_update_rating_curve_versions_request(
        self,
        target: Union[uuid.UUID, str],
        start_time: datetime,
        end_time: datetime,
        new_versions: List[RatingCurveVersion]
    ) -> core_pb2.UpdateRatingCurveVersionsRequest:

        if isinstance(target, uuid.UUID):
            target = core_pb2.MeshId(id=_to_proto_guid(target))
        elif isinstance(target, str):
            target = core_pb2.MeshId(path=target)
        else:
            raise TypeError("target must be a uuid.UUID or str")

        if start_time is None or end_time is None:
            raise TypeError("start_time and end_time must both have a value")

        def to_proto_rating_curve_segment(segment: RatingCurveSegment) -> core_pb2.RatingCurveSegment:
            return core_pb2.RatingCurveSegment(
                x_range_until=segment.x_range_until,
                factor_a=segment.factor_a,
                factor_b=segment.factor_b,
                factor_c=segment.factor_c)

        def to_proto_rating_curve_version(version: RatingCurveVersion) -> core_pb2.RatingCurveVersion:
            proto_segments = [to_proto_rating_curve_segment(segment) for segment in version.x_value_segments]

            proto_version = core_pb2.RatingCurveVersion(
                x_range_from = version.x_range_from,
                x_value_segments=proto_segments)

            # name of the field in proto file is a Python keyword
            # need to use `setattr`, but because it is not a simple type
            # first we need to call `getattr` and then set its value via
            # CopyFrom or FromDatetime, see:
            # https://developers.google.com/protocol-buffers/docs/reference/python-generated#keyword-conflicts
            getattr(proto_version, "from").FromDatetime(version.valid_from_time)
            return proto_version

        proto_versions = [to_proto_rating_curve_version(version) for version in new_versions]

        request = core_pb2.UpdateRatingCurveVersionsRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=target,
            interval=_to_protobuf_utcinterval(start_time, end_time),
            versions=proto_versions
        )
        return request
