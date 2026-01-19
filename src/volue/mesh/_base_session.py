from __future__ import annotations

import abc
import asyncio
import threading
import typing
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple, Union

import dateutil
from google import protobuf

from volue.mesh.proto.calc.v1alpha import calc_pb2_grpc
from volue.mesh.proto.hydsim.v1alpha import hydsim_pb2, hydsim_pb2_grpc
from volue.mesh.proto.model.v1alpha import model_pb2, model_pb2_grpc
from volue.mesh.proto.model.v1alpha import resources_pb2 as model_resources_pb2
from volue.mesh.proto.model_definition.v1alpha import (
    model_definition_pb2,
    model_definition_pb2_grpc,
)
from volue.mesh.proto.session.v1alpha import session_pb2_grpc
from volue.mesh.proto.time_series.v1alpha import time_series_pb2, time_series_pb2_grpc
from volue.mesh.proto.type import resources_pb2

from ._attribute import (
    SIMPLE_TYPE,
    SIMPLE_TYPE_OR_COLLECTION,
    AttributeBase,
    TimeseriesAttribute,
)
from ._common import (
    AttributesFilter,
    LinkRelationVersion,
    RatingCurveSegment,
    RatingCurveVersion,
    XyCurve,
    XySet,
    _datetime_to_timestamp_pb2,
    _object_to_proto_field_mask,
    _read_proto_reply,
    _to_proto_attribute_field_mask,
    _to_proto_attribute_masks,
    _to_proto_curve_type,
    _to_proto_guid,
    _to_proto_timeseries,
    _to_proto_utcinterval,
)
from ._mesh_id import (
    _to_proto_attribute_definition_mesh_id,
    _to_proto_attribute_mesh_id,
    _to_proto_object_mesh_id,
    _to_proto_read_timeseries_mesh_id,
)
from ._object import Object
from ._timeseries import Timeseries
from ._timeseries_resource import TimeseriesResource
from .calc.forecast import ForecastFunctions
from .calc.history import HistoryFunctions
from .calc.statistical import StatisticalFunctions
from .calc.transform import TransformFunctions

EXTEND_SESSION_LIFETIME_INTERVAL_IN_SECS = 150


class Session(abc.ABC):
    class WorkerThread(threading.Thread):
        def __init__(
            self,
            session: Session,
            event_loop: asyncio.AbstractEventLoop | None = None,
        ):
            super().__init__()
            # no resources are acquired, no need to do explicit clean-up
            self.daemon = True
            self.session: Session = session
            self.event_loop: asyncio.AbstractEventLoop | None = event_loop

        def run(self):
            if self.event_loop is not None:
                asyncio.set_event_loop(self.event_loop)

            while not self.session.stop_worker_thread.wait(
                EXTEND_SESSION_LIFETIME_INTERVAL_IN_SECS
            ):
                try:
                    if self.event_loop is not None:
                        extend_lifetime_coroutine: typing.Coroutine[
                            typing.Any, typing.Any, None
                        ] = self.session._extend_lifetime()
                        asyncio.run_coroutine_threadsafe(
                            extend_lifetime_coroutine, self.event_loop
                        ).result()
                    else:
                        self.session._extend_lifetime()
                except Exception as e:
                    # In case of an exception just add more descriptive
                    # message and exit the worker thread.
                    raise RuntimeError(
                        f"session {self.session.session_id} worker thread exception"
                    ) from e

    """Represents a session to a Mesh server."""

    def _extend_lifetime(self) -> None:
        """
        Request to extend session lifetime on the Mesh server.
        This is used internally by the Mesh Python SDK and the user does not
        need to call it explicitly.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
        """

    def __init__(
        self,
        calc_service: calc_pb2_grpc.CalculationServiceStub,
        hydsim_service: hydsim_pb2_grpc.HydsimServiceStub,
        model_service: model_pb2_grpc.ModelServiceStub,
        model_definition_service: model_definition_pb2_grpc.ModelDefinitionServiceStub,
        session_service: session_pb2_grpc.SessionServiceStub,
        time_series_service: time_series_pb2_grpc.TimeseriesServiceStub,
        session_id: uuid.UUID | None = None,
    ):
        """
        Initialize a session object for working with the Mesh server.

        Args:
            calc_service: gRPC generated Mesh calculation service.
            hydsim_service: gRPC generated Mesh HydSim service.
            model_service: gRPC generated Mesh model service.
            model_definition_service: gRPC generated Mesh model definition service.
            session_service: gRPC generated Mesh session service.
            time_series_service: gRPC generated Mesh time series service.
            session_id: ID of the session you are (or want to be) connected to.
        """
        self.session_id: uuid.UUID | None = session_id
        self.calc_service: calc_pb2_grpc.CalculationServiceStub = calc_service
        self.hydsim_service: hydsim_pb2_grpc.HydsimServiceStub = hydsim_service
        self.model_service: model_pb2_grpc.ModelServiceStub = model_service
        self.model_definition_service: (
            model_definition_pb2_grpc.ModelDefinitionServiceStub
        ) = model_definition_service
        self.session_service: session_pb2_grpc.SessionServiceStub = session_service
        self.time_series_service: time_series_pb2_grpc.TimeseriesServiceStub = (
            time_series_service
        )

        self.stop_worker_thread: threading.Event = threading.Event()
        self.worker_thread: Session.WorkerThread | None = None

    @abc.abstractmethod
    def open(self) -> None:
        """
        Request to open a session on the Mesh server.
        An opened session must be closed using the same `Session` object.

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
        target: Union[uuid.UUID, str, int, AttributeBase],
        start_time: datetime,
        end_time: datetime,
    ) -> Timeseries:
        """
        Reads time series points for the specified time series in the given
        interval.

        If there are too many points in the response you might get
        a `StatusCode.RESOURCE_EXHAUSTED` error.
        See: :ref:`mesh_client:gRPC communication`.

        For information about `datetime` arguments and time zones refer to
        :ref:`mesh_client:Date times and time zones`.

        Args:
            target: Mesh attribute, virtual or physical time series. It could
                be a time series key, Universal Unique Identifier or a path in
                the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed
            RuntimeError: Error message raised if the input is not valid
            TypeError: Error message raised if the returned result from the request is not as expected
        """

    @abc.abstractmethod
    def write_timeseries_points(self, timeseries: Timeseries) -> None:
        """
        Writes time series points for the specified time series in the given interval.
        Resolution of the time series does not need to be set when writing time series.

        If there are too many points in the request you will the Mesh server
        will discard it and return `StatusCode.RESOURCE_EXHAUSTED`.
        See: :ref:`mesh_client:gRPC communication`.

        Args:
            timeseries: The modified time series.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def list_models(
        self,
    ) -> List[Object]:
        """
        List all `Mesh models <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
        Model is a root object that does not have an owner.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def get_object(
        self,
        target: Union[uuid.UUID, str, Object],
        full_attribute_info: bool = False,
        attributes_filter: AttributesFilter | None = None,
    ) -> Object:
        """
        Request information associated with a Mesh object from the Mesh model.
        Specify either `object_id` or `object_path` to a Mesh object.

        Args:
            target: Mesh object to be read. It could be a Universal Unique Identifier
                or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object will be returned, otherwise only name,
                path, ID and value(s).
            attributes_filter: Filtering criteria for what attributes owned by
                object should be returned. By default all attributes are returned.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def search_for_objects(
        self,
        target: Union[uuid.UUID, str, Object],
        query: str,
        full_attribute_info: bool = False,
        attributes_filter: AttributesFilter | None = None,
    ) -> List[Object]:
        """
        Use the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__
        to find Mesh objects in the Mesh model.

        Args:
            target: Start searching at the target object. It could be a Universal Unique Identifier
                or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            query: A search formulated using the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object(s) will be returned, otherwise only name,
                path, ID and value(s).
            attributes_filter: Filtering criteria for what attributes owned by
                object(s) should be returned. By default all attributes are returned.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def create_object(
        self, target: Union[uuid.UUID, str, AttributeBase], name: str
    ) -> Object:
        """
        Create new Mesh object in the Mesh model.
        Owner of the new object must be a one-to-one or one-to-many ownership
        relation attribute. E.g.: for `SomePowerPlant1` object with path:
        - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1

        Owner will be the `ThermalPowerToPlantRef` attribute.

        Args:
            target: Owner of the new object to be created. It must be a
                one-to-one (object value type = "ElementAttributeDefinition")
                or one-to-many (object value type = "ElementCollectionAttributeDefinition")
                ownership relation attribute.
                It could be a Universal Unique Identifier or a path in the
                `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
            name: Name for the new object to create.

        Returns:
            Created object with all attributes (no mask applied) and basic
            information: name, path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def update_object(
        self,
        target: Union[uuid.UUID, str, Object],
        new_name: str | None = None,
        new_owner_attribute: uuid.UUID | str | AttributeBase | None = None,
    ) -> None:
        """
        Update an existing Mesh object in the Mesh model.
        New owner of the object must be a one-to-one or one-to-many ownership
        relation attribute. E.g.: for `SomePowerPlant1` object with path:
        - Model/SimpleThermalTestModel/ThermalComponent.ThermalPowerToPlantRef/SomePowerPlant1

        Args:
            target: Mesh object to be updated. It could be a Universal Unique Identifier
                or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            new_name: New name for the object.
            new_owner_attribute: New owner of the object. It must be a
                one-to-one (object value type = "ElementAttributeDefinition")
                or one-to-many (object value type = "ElementCollectionAttributeDefinition")
                ownership relation attribute.
                It could be a Universal Unique Identifier or a path in the
                `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def delete_object(
        self, target: Union[uuid.UUID, str, Object], recursive_delete: bool = False
    ) -> None:
        """
        Delete an existing Mesh object in the Mesh model.

        Args:
            target: Mesh object to be deleted. It could be a Universal Unique Identifier
                or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            recursive_delete: If set then all child objects
                (owned by the object to be deleted) in the model will also be deleted.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def get_attribute(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        full_attribute_info: bool = False,
    ) -> AttributeBase:
        """
        Request information associated with a Mesh attribute from the
        Mesh `model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`_.

        Args:
            target: Mesh attribute to be read. It could be a Universal Unique Identifier
                or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attribute will be returned, otherwise only name, path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def get_timeseries_attribute(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        full_attribute_info: bool = False,
    ) -> TimeseriesAttribute:
        """
        Request information associated with a Mesh attribute from the
        Mesh `model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`_.

        Args:
            target: Mesh time series attribute to be read. It could be a Universal Unique
                Identifier or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attribute will be returned, otherwise only name, path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
            ValueError: Raised if given attribute ID or path points to an attribute of
                different type than `TimeseriesAttribute`.
        """

    @abc.abstractmethod
    def search_for_attributes(
        self,
        target: Union[uuid.UUID, str, Object],
        query: str,
        full_attribute_info: bool = False,
    ) -> List[AttributeBase]:
        """
        Use the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__
        to find Mesh attributes in the Mesh
        `model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`_.

        Args:
            target: Start searching at the target object. It could be a Universal Unique Identifier
                or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            query: A search formulated using the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object(s) will be returned, otherwise only name,
                path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def search_for_timeseries_attributes(
        self,
        target: Union[uuid.UUID, str, Object],
        query: str,
        full_attribute_info: bool = False,
    ) -> List[TimeseriesAttribute]:
        """
        Use the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__
        to find Mesh time series attributes in the Mesh
        `model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`_.

        Args:
            target: Start searching at the target object. It could be a Universal Unique Identifier
                or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            query: A search formulated using the `Mesh search language <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/search-language/>`__.
            full_attribute_info: If set then all information (e.g. description, value type, etc.)
                of attributes owned by the object(s) will be returned, otherwise only name,
                path, ID and value(s).

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def update_simple_attribute(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        value: SIMPLE_TYPE_OR_COLLECTION,
    ) -> None:
        """
        Update an existing Mesh simple attribute's value in the Mesh model.
        Simple attribute is a singular type or collection of the following types:
        - double (float in Python)
        - integer (int in Python)
        - boolean (bool in Python)
        - string (str in Python)
        - UTC time (datetime in Python)

        Args:
            target: Mesh attribute to be updated. It could be a Universal Unique Identifier
                or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            value: New simple attribute value. It can be one of following simple types:
                bool, float, int, str, datetime or a list of simple types.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def update_timeseries_attribute(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        new_local_expression: str | None = None,
        new_timeseries_resource_key: int | None = None,
    ) -> None:
        """
        Update meta data of an existing Mesh time series attribute's in the Mesh model.

        Args:
            target: Mesh time series attribute to be updated. It could be a Universal Unique
                Identifier or a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            new_local_expression: New local expression. It is not validated during this operation.
                Invalid local expressions will be accepted but will cause failures when reading
                time series points later.
            new_timeseries_resource_key: Time series key of a new time series resource
                (physical or virtual) to connect to the time series attribute. To disconnect
                time series attribute from already connected time series resource set this
                argument to 0.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def update_timeseries_attribute_definition(
        self,
        target: Union[uuid.UUID, str, AttributeBase.AttributeBaseDefinition],
        new_template_expression: str | None = None,
        new_description: str | None = None,
    ) -> None:
        """
        Update an existing Mesh time series attribute definition.

        Args:
            target: Mesh time series attribute definition to be updated. It could be a Universal
                Unique Identifier, a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__,
                or an AttributeBaseDefinition instance.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            new_template_expression: New template expression for the attribute definition.
                This will be used by all attribute instances that use this definition and don't
                have a local expression. The template expression is not validated during this
                operation. Invalid template expressions will be accepted but will cause failures
                when reading time series points later.
            new_description: New description for the attribute definition.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.

        Note:
            At least one of `new_template_expression` or `new_description` must be provided.
        """

    @abc.abstractmethod
    def update_link_relation_attribute(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        new_target_object_ids: List[uuid.UUID],
        append: bool,
    ) -> None:
        """
        Update an existing Mesh link relation (non-versioned) attribute in the Mesh model.

        Args:
            target: Mesh one-to-one or one-to-many link relation (non-versioned) attribute
                to be updated. It could be a Universal Unique Identifier or a path in the
                `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            new_target_object_ids: List of objects the link relation will point to. For
                one-to-one link relation this must contain zero or one `new_target_object_ids`.
                If there is no `new_target_object_ids` provided then currently existing target
                object will be removed. If updating a one-to-many link relation attribute
                this may contain zero, one or more `new_target_object_ids`s. If there is no
                `new_target_object_ids` provided and `append` is set to `False` then all
                currently existing target objects will be removed.
            append: If set to `True` for a one-to-many link relation attribute this will
                append `target_object_ids` to already existing ones. If set to `False` then
                all currently existing target objects will be replaced by `target_object_ids`.
                For one-to-one link relation attribute this must set to `False`.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.

        See Also:
            `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/relations/>`__
        """

    @abc.abstractmethod
    def update_versioned_one_to_one_link_relation_attribute(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        start_time: datetime,
        end_time: datetime,
        new_versions: List[LinkRelationVersion],
    ) -> None:
        """
        Update an existing Mesh versioned one-to-one link relation attribute in
        the Mesh model.

        Args:
            target: Mesh one-to-one versioned link relation attribute to be updated.
                It could be a Universal Unique Identifier or a path in the
                `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            start_time: the (inclusive) start of the edit interval.
            end_time: the (exclusive) end of the edit interval.
            new_versions: the list of link relation versions to insert.
                All versions must be within `[start_time, end_time)` interval.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.

        See Also:
            `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/relations/>`__
        """

    @abc.abstractmethod
    def update_versioned_one_to_many_link_relation_attribute(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        new_entries: List[List[LinkRelationVersion]],
    ) -> None:
        """
        Update an existing Mesh versioned one-to-many link relation attribute in
        the Mesh model.

        Args:
            target: Mesh one-to-many versioned link relation attribute to be updated.
                It could be a Universal Unique Identifier or a path in the
                `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
                See: `objects and attributes paths <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#objects-and-attributes-paths>`__.
            new_entries: the list of lists of link relation versions to insert.
                The first level list represents entries. Each entry can have multiple
                link relation versions.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.

        See Also:
            `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/relations/>`__
        """

    @abc.abstractmethod
    def get_timeseries_resource_info(self, timeseries_key: int) -> TimeseriesResource:
        """
        Request information (like curve type or resolution) associated with
        a physical or virtual time series.

        Args:
            timeseries_key: integer that only applies to a specific physical or
                virtual time series.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def update_timeseries_resource_info(
        self,
        timeseries_key: int,
        new_curve_type: Timeseries.Curve | None = None,
        new_unit_of_measurement: str | None = None,
    ) -> None:
        """
        Update information associated with a physical or virtual time series.

        Args:
            timeseries_key: integer that only applies to a specific physical or
                virtual time series.
            new_curve_type: set new curve type.
            new_unit_of_measurement: set new unit of measurement.

        Note:
            Specify which ever of the new_* fields you want to update.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def create_physical_timeseries(
        self,
        path: str,
        name: str,
        curve_type: Timeseries.Curve,
        resolution: Timeseries.Resolution,
        unit_of_measurement: str,
    ) -> TimeseriesResource:
        """
        Create a new physical time series.

        Any missing components of the requested time series path will be created in
        the catalog as well. For example, if we set the 'path' to "/Path/To/Timeseries/",
        and its 'name' field to "Test_Timeseries", the entire  "Path/To/Timeseries/Test_Timeseries"
        sequence of catalog entries will be created if it doesn't exist already.

        Note that the 'path' field on the returned TimeseriesResource won't
        have the same as the value as the 'path' argument in this request;
        namely, the returned 'path' will have a "Resource/" prefix, and will be
        suffixed with the contents of the 'name' field from this request. That is:
        ReturnedTimeseriesResource.path == "Resource/" + request.path + "/" + request.name

        Continuing with the previous example, in this case the 'path' field in the
        response will be "Resource/Path/To/Timeseries/Test_Timeseries".

        Args:
            path: path of the new physical time series.
                Must begin and end with forward slashes.
            name: name of the new physical time series.
            curve_type: curve type of the new physical time series
            resolution: resolution of the new physical time series
            unit_of_measurement: unit of measurement of the new physical time series.
                It must match an existing unit in Mesh.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.
        """

    @abc.abstractmethod
    def forecast_functions(
        self,
        target: Union[uuid.UUID, str, int],
        start_time: datetime,
        end_time: datetime,
    ) -> ForecastFunctions:
        """Access to forecast functions.

        Args:
            target: Mesh object, attribute, virtual or physical time series the
                calculation expression will be evaluated relative to.
                It could be a time series key, Universal Unique Identifier or
                a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Returns:
            Object containing all forecast functions.
        """

    @abc.abstractmethod
    def history_functions(
        self,
        target: Union[uuid.UUID, str, int],
        start_time: datetime,
        end_time: datetime,
    ) -> HistoryFunctions:
        """Access to history functions.

        Args:
            target: Mesh object, attribute, virtual or physical time series the
                calculation expression will be evaluated relative to.
                It could be a time series key, Universal Unique Identifier or
                a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Returns:
           Object containing all history functions.
        """

    @abc.abstractmethod
    def statistical_functions(
        self,
        target: Union[uuid.UUID, str, int],
        start_time: datetime,
        end_time: datetime,
    ) -> StatisticalFunctions:
        """Access to statistical functions.

        Args:
            target: Mesh object, attribute, virtual or physical time series the
                calculation expression will be evaluated relative to.
                It could be a time series key, Universal Unique Identifier or
                a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Returns:
            Object containing all statistical functions.
        """

    @abc.abstractmethod
    def transform_functions(
        self,
        target: Union[uuid.UUID, str, int],
        start_time: datetime,
        end_time: datetime,
    ) -> TransformFunctions:
        """Access to transform functions.

        Args:
            target: Mesh object, attribute, virtual or physical time series the
                calculation expression will be evaluated relative to.
                It could be a time series key, Universal Unique Identifier or
                a path in the `Mesh model <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/general/#model>`__.
            start_time: the start date and time of the time series interval
            end_time: the end date and time of the time series interval

        Returns:
            Object containing all transformation functions.
        """

    @abc.abstractmethod
    def get_xy_sets(
        self,
        target: typing.Union[uuid.UUID, str, AttributeBase],
        start_time: datetime | None,
        end_time: datetime | None,
        versions_only: bool,
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
            `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/xy-sets/>`__
        """

    @abc.abstractmethod
    def update_xy_sets(
        self,
        target: typing.Union[uuid.UUID, str, AttributeBase],
        start_time: datetime | None,
        end_time: datetime | None,
        new_xy_sets: typing.List[XySet],
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
            `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/xy-sets/>`__
        """

    @abc.abstractmethod
    def get_rating_curve_versions(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        start_time: datetime,
        end_time: datetime,
        versions_only: bool = False,
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
            `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/rating-curves/>`__
        """

    @abc.abstractmethod
    def update_rating_curve_versions(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        start_time: datetime,
        end_time: datetime,
        new_versions: List[RatingCurveVersion],
    ) -> None:
        """Replace rating curve versions on an rating curve attribute on the server.

        The update operation deletes all versions in the
        `[start_time, end_time)` interval, and inserts the new versions.

        Args:
            target: the ID or the path of an rating curve attribute.
            start_time: the (inclusive) start of the edit interval.
            end_time: the (exclusive) end of the edit interval.
            new_versions: the list of rating curve versions to insert.
                All versions must be within `[start_time, end_time)` interval
                and sorted by `valid_from_time`.

        Raises:
            grpc.RpcError: Error message raised if the gRPC request could not be completed.

        See Also:
            `Mesh documentation <https://volue-public.github.io/energy-smp-docs/latest/mesh/concepts/modelling/rating-curves/>`__
        """

    @abc.abstractmethod
    def run_simulation(
        self,
        model: str,
        case: str,
        start_time: datetime,
        end_time: datetime,
        *,
        resolution: timedelta = None,
        scenario: int = None,
        return_datasets: bool = False,
    ) -> Union[typing.Iterator[None], typing.AsyncIterator[None]]:
        """Run a hydro simulation using HydSim on the Mesh server.

        In case of running a simulation on longer interval and with
        `return_datasets` enabled you might get a `StatusCode.RESOURCE_EXHAUSTED`
        error. See: :ref:`mesh_client:gRPC communication`.

        This function is experimental and subject to larger changes.

        Args:
            model: The name of the Mesh model in which the simulation case exists.
            case: The names of the case group and simulation case in the form
                'CaseGroup/CaseName'.
            start_time: The (inclusive) start of the simulation interval.
            end_time: The (exclusive) end of the simulation interval.
            resolution: The resolution of the simulation. The default resolution
                of the simulation case is used if this is left as `None`.
                Officially supported resolutions are 5, 10, 15, and 60 minutes.
            scenario: The scenario(s) to run. All scenarios are run if left as
                `None`, no scenarios are run if set as -1, and a specific
                numbered scenario is run if set as the number of that scenario.
            return_datasets: Generate and return HydSim datasets that can be used
                by Volue to diagnose issues with hydro simulations. For performance
                reasons this should be false when not trying to diagnose an issue.

        Returns:
            An iterator of `None`. In future versions this iterator will yield
            log messages, datasets, and potentially more. The simulation is
            done when the iterator is exhausted.

            Exhausting the iterator without an exception does not guarantee
            that the simulation completed successfully. To determine that
            you must analyze the simulation's result time series and the
            log messages from the server.

        Raises:
            TypeError
            grpc.RpcError
        """

    @abc.abstractmethod
    def run_inflow_calculation(
        self,
        model: str,
        area: str,
        water_course: str,
        start_time: datetime,
        end_time: datetime,
        *,
        resolution: timedelta = None,
        return_datasets: bool = False,
    ) -> Union[typing.Iterator[None], typing.AsyncIterator[None]]:
        """Run an inflow calculation using HydSim on the Mesh server.

        In case of running an inflow calculation on longer interval and with
        `return_datasets` enabled you might get a `StatusCode.RESOURCE_EXHAUSTED`
        error. See: :ref:`mesh_client:gRPC communication`.

        Args:
            model: The name of the Mesh model in which the inflow calculation
                exists.
            area: The area of the water course to calculate.
            water_course: The water course to calculate.
            start_time: The (inclusive) start of the calculation interval.
            end_time: The (exclusive) end of the calculation interval.
            resolution: The resolution of the simulation. The default resolution
                of the inflow calculation case is used if this is left as `None`.
                Officially supported resolutions are 5, 10, 15, and 60 minutes.
            return_datasets: Generate and return HydSim datasets that can be used
                by Volue to diagnose issues with inflow calculations. For performance
                reasons this should be false when not trying to diagnose an issue.

        Returns:
            An iterator of `None`. In future versions this iterator will yield
            log messages, datasets, and potentially more. The calculation is
            done when the iterator is exhausted.

            Exhausting the iterator without an exception does not guarantee
            that the calculation completed successfully. To determine that
            you must analyze the calculation's result time series and the
            log messages from the server.

        Raises:
            TypeError
            grpc.RpcError
        """

    @abc.abstractmethod
    def get_mc_file(
        self,
        model: str,
        case: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Union[typing.Iterator[None], typing.AsyncIterator[None]]:
        """Generate Marginal Cost input using HydSim on the Mesh server.

        Args:
            model: The name of the Mesh model in which the simulation case exists.
            case: The names of the case group and simulation case in the form
                'CaseGroup/CaseName'.
            start_time: The (inclusive) start of the simulation interval.
            end_time: The (exclusive) end of the simulation interval.

        Returns:
            An iterator of `LogMessage`s followed by a single `str`. The final
            string is the Marginal Cost input.

        Raises:
            TypeError
            grpc.RpcError
        """

    def _get_xy_sets_impl(
        self,
        target: typing.Union[uuid.UUID, str, AttributeBase],
        start_time: datetime | None,
        end_time: datetime | None,
        versions_only: bool,
    ) -> typing.Generator[typing.Any, model_pb2.GetXySetsResponse, None]:
        """Generator implementation of get_xy_sets.

        Yields the protobuf request, receives the protobuf response, and yields
        the final result.
        """

        if (start_time is None) != (end_time is None):
            raise TypeError(
                "start_time and end_time must both be None or both have a value"
            )

        if start_time is None or end_time is None:
            interval = None
        else:
            interval = _to_proto_utcinterval(start_time, end_time)

        request = model_pb2.GetXySetsRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=_to_proto_attribute_mesh_id(target),
            interval=interval,
            versions_only=versions_only,
        )

        response = yield request

        def get_valid_from_time(proto: model_resources_pb2.XySet):
            if proto.HasField("valid_from_time"):
                return proto.valid_from_time.ToDatetime(dateutil.tz.UTC)
            else:
                return None

        yield [
            XySet(
                get_valid_from_time(proto_xy_set),
                [
                    XyCurve(
                        proto_curve.reference_value,
                        list(zip(proto_curve.x_values, proto_curve.y_values)),
                    )
                    for proto_curve in proto_xy_set.xy_curves
                ],
            )
            for proto_xy_set in response.xy_sets
        ]

    def _prepare_update_xy_sets_request(
        self,
        target: typing.Union[uuid.UUID, str, AttributeBase],
        start_time: datetime | None,
        end_time: datetime | None,
        new_xy_sets: typing.List[XySet],
    ) -> model_pb2.UpdateXySetsRequest:
        if (start_time is None) != (end_time is None):
            raise TypeError(
                "start_time and end_time must both be None or both have a value"
            )

        if start_time is None or end_time is None:
            interval = None
        else:
            interval = _to_proto_utcinterval(start_time, end_time)

        def to_proto_xy_curve(curve: XyCurve) -> model_resources_pb2.XyCurve:
            return model_resources_pb2.XyCurve(
                reference_value=curve.z,
                x_values=[x for (x, _) in curve.xy],
                y_values=[y for (_, y) in curve.xy],
            )

        def to_proto_xy_set(xy_set: XySet) -> model_resources_pb2.XySet:
            valid_from_time = (
                None
                if xy_set.valid_from_time is None
                else _datetime_to_timestamp_pb2(xy_set.valid_from_time)
            )
            xy_curves = [to_proto_xy_curve(curve) for curve in xy_set.xy_curves]
            return model_resources_pb2.XySet(
                valid_from_time=valid_from_time, xy_curves=xy_curves
            )

        xy_sets = [to_proto_xy_set(xy_set) for xy_set in new_xy_sets]

        request = model_pb2.UpdateXySetsRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=_to_proto_attribute_mesh_id(target),
            interval=interval,
            xy_sets=xy_sets,
        )

        return request

    def _read_timeseries_impl(
        self,
        target: Union[uuid.UUID, str, int, AttributeBase],
        start_time: datetime,
        end_time: datetime,
    ) -> typing.Generator[typing.Any, time_series_pb2.ReadTimeseriesResponse, None]:
        """Generator implementation of read_timeseries.

        Yields the protobuf request, receives the protobuf response, and yields
        the final result.
        """

        request = time_series_pb2.ReadTimeseriesRequest(
            session_id=_to_proto_guid(self.session_id),
            timeseries_id=_to_proto_read_timeseries_mesh_id(target),
            interval=_to_proto_utcinterval(start_time, end_time),
        )

        response = yield request

        timeseries = _read_proto_reply(response)
        if len(timeseries) != 1:
            raise RuntimeError(
                f"invalid result from 'read_timeseries_points', "
                f"expected 1 time series, but got {len(timeseries)}"
            )

        yield timeseries[0]

    def _prepare_write_timeseries_points_request(
        self, timeseries: Timeseries
    ) -> time_series_pb2.WriteTimeseriesRequest:
        """Check that time series is correct to be written, e.g.: has start and end time."""
        if timeseries.start_time is None or timeseries.end_time is None:
            raise TypeError(
                "time series start_time and end_time must both have a value"
            )
        request = time_series_pb2.WriteTimeseriesRequest(
            session_id=_to_proto_guid(self.session_id),
            timeseries=_to_proto_timeseries(timeseries),
        )
        return request

    def _list_models_impl(
        self,
    ) -> typing.Generator[typing.Any, model_pb2.ListModelsResponse, None]:
        """Generator implementation of list_models.

        Yields the protobuf request, receives the protobuf response, and yields
        the final result.
        """

        request = model_pb2.ListModelsRequest(
            session_id=_to_proto_guid(self.session_id),
        )

        response = yield request

        yield [
            Object._from_proto_object(proto_object) for proto_object in response.models
        ]

    def _prepare_get_object_request(
        self,
        target: Union[uuid.UUID, str, Object],
        full_attribute_info: bool,
        attributes_filter: AttributesFilter | None,
    ) -> model_pb2.GetObjectRequest:
        """Create a gRPC `GetObjectRequest`"""

        request = model_pb2.GetObjectRequest(
            session_id=_to_proto_guid(self.session_id),
            object_id=_to_proto_object_mesh_id(target),
            attributes_masks=_to_proto_attribute_masks(attributes_filter),
            attribute_field_mask=_to_proto_attribute_field_mask(
                full_attribute_info, attributes_filter
            ),
            object_field_mask=_object_to_proto_field_mask(attributes_filter),
        )
        return request

    def _prepare_search_for_objects_request(
        self,
        target: Union[uuid.UUID, str, Object],
        query: str,
        full_attribute_info: bool,
        attributes_filter: AttributesFilter | None,
    ) -> model_pb2.SearchObjectsRequest:
        """Create a gRPC `SearchObjectsRequest`"""

        request = model_pb2.SearchObjectsRequest(
            session_id=_to_proto_guid(self.session_id),
            start_object_id=_to_proto_object_mesh_id(target),
            attributes_masks=_to_proto_attribute_masks(attributes_filter),
            attribute_field_mask=_to_proto_attribute_field_mask(
                full_attribute_info, attributes_filter
            ),
            object_field_mask=_object_to_proto_field_mask(attributes_filter),
            query=query,
        )
        return request

    def _prepare_create_object_request(
        self, target: Union[uuid.UUID, str, AttributeBase], name: str
    ) -> model_pb2.CreateObjectRequest:
        """Create a gRPC `CreateObjectRequest`"""

        request = model_pb2.CreateObjectRequest(
            session_id=_to_proto_guid(self.session_id),
            owner_id=_to_proto_attribute_mesh_id(target),
            name=name,
        )
        return request

    def _prepare_update_object_request(
        self,
        target: Union[uuid.UUID, str, Object],
        new_name: str | None,
        new_owner_attribute: uuid.UUID | str | AttributeBase | None,
    ) -> model_pb2.UpdateObjectRequest:
        """Create a gRPC `UpdateObjectRequest`"""

        request = model_pb2.UpdateObjectRequest(
            session_id=_to_proto_guid(self.session_id),
            object_id=_to_proto_object_mesh_id(target),
        )

        fields_to_update = []

        # providing new owner is optional
        if new_owner_attribute is not None:
            try:
                new_owner_mesh_id = _to_proto_attribute_mesh_id(new_owner_attribute)
            except TypeError as e:
                # Wrap the error so that the user can distinguish what
                # MeshId is wrong: target or new_owner_attribute.
                raise TypeError("invalid new owner attribute") from e

            request.new_owner_id.CopyFrom(new_owner_mesh_id)
            fields_to_update.append("new_owner_id")

        # providing new name is optional
        if new_name is not None:
            request.new_name = new_name
            fields_to_update.append("new_name")

        request.field_mask.CopyFrom(
            protobuf.field_mask_pb2.FieldMask(paths=fields_to_update)
        )
        return request

    def _prepare_delete_object_request(
        self, target: Union[uuid.UUID, str, Object], recursive_delete: bool
    ) -> model_pb2.DeleteObjectRequest:
        """Create a gRPC `DeleteObjectRequest`"""

        request = model_pb2.DeleteObjectRequest(
            session_id=_to_proto_guid(self.session_id),
            object_id=_to_proto_object_mesh_id(target),
            recursive_delete=recursive_delete,
        )
        return request

    def _prepare_get_attribute_request(
        self, target: Union[uuid.UUID, str, AttributeBase], full_attribute_info: bool
    ) -> model_pb2.GetAttributeRequest:
        request = model_pb2.GetAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_id=_to_proto_attribute_mesh_id(target),
            field_mask=_to_proto_attribute_field_mask(full_attribute_info),
        )
        return request

    def _prepare_search_attributes_request(
        self,
        target: Union[uuid.UUID, str, Object],
        query: str,
        full_attribute_info: bool,
    ) -> model_pb2.SearchAttributesRequest:
        request = model_pb2.SearchAttributesRequest(
            session_id=_to_proto_guid(self.session_id),
            start_object_id=_to_proto_object_mesh_id(target),
            query=query,
            field_mask=_to_proto_attribute_field_mask(full_attribute_info),
        )
        return request

    def _prepare_update_simple_attribute_request(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        value: SIMPLE_TYPE_OR_COLLECTION,
    ) -> model_pb2.UpdateSimpleAttributeRequest:
        request = model_pb2.UpdateSimpleAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_id=_to_proto_attribute_mesh_id(target),
        )

        (
            new_singular_value,
            new_collection_values,
        ) = self._to_update_attribute_request_values(value=value)

        if new_singular_value is not None:
            request.new_singular_value.CopyFrom(new_singular_value)

        if new_collection_values is not None:
            for value in new_collection_values:
                request.new_collection_values.append(value)

        return request

    def _prepare_update_timeseries_attribute_request(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        new_local_expression: str | None,
        new_timeseries_resource_key: int | None,
    ) -> model_pb2.UpdateTimeseriesAttributeRequest:
        request = model_pb2.UpdateTimeseriesAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_id=_to_proto_attribute_mesh_id(target),
        )

        fields_to_update = []
        if new_local_expression is not None:
            fields_to_update.append("new_local_expression")
            request.new_local_expression = new_local_expression

        if new_timeseries_resource_key is not None:
            fields_to_update.append("new_timeseries_resource_key")
            request.new_timeseries_resource_key = new_timeseries_resource_key

        request.field_mask.CopyFrom(
            protobuf.field_mask_pb2.FieldMask(paths=fields_to_update)
        )
        return request

    def _prepare_update_timeseries_attribute_definition_request(
        self,
        target: Union[uuid.UUID, str, AttributeBase.AttributeBaseDefinition],
        new_template_expression: str | None,
        new_description: str | None,
    ) -> model_definition_pb2.UpdateTimeseriesAttributeDefinitionRequest:
        request = model_definition_pb2.UpdateTimeseriesAttributeDefinitionRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute_definition_id=_to_proto_attribute_definition_mesh_id(target),
        )

        fields_to_update = []
        if new_template_expression is not None:
            fields_to_update.append("new_template_expression")
            request.new_template_expression = new_template_expression

        if new_description is not None:
            fields_to_update.append("new_description")
            request.new_description = new_description

        request.field_mask.CopyFrom(
            protobuf.field_mask_pb2.FieldMask(paths=fields_to_update)
        )
        return request

    def _prepare_update_link_relation_attribute_request(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        new_target_object_ids: List[uuid.UUID],
        append: bool,
    ) -> model_pb2.UpdateLinkRelationAttributeRequest:
        proto_target_object_ids = [
            _to_proto_guid(target_object_id)
            for target_object_id in new_target_object_ids
        ]

        request = model_pb2.UpdateLinkRelationAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=_to_proto_attribute_mesh_id(target),
            append=append,
            target_object_ids=proto_target_object_ids,
        )
        return request

    def _prepare_versioned_link_relation_attribute_request(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        entries: List[List[LinkRelationVersion]],
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> model_pb2.UpdateVersionedLinkRelationAttributeRequest:
        if (start_time is None) != (end_time is None):
            raise TypeError(
                "start_time and end_time must both be None or both have a value"
            )

        if start_time is None or end_time is None:
            proto_interval = None
        else:
            proto_interval = _to_proto_utcinterval(start_time, end_time)

        def to_proto_link_relation_version(
            version: LinkRelationVersion,
        ) -> model_resources_pb2.LinkRelationVersion:
            return model_resources_pb2.LinkRelationVersion(
                target_object_id=_to_proto_guid(version.target_object_id),
                valid_from_time=(
                    None
                    if version.valid_from_time is None
                    else _datetime_to_timestamp_pb2(version.valid_from_time)
                ),
            )

        def to_proto_link_relation_entry(
            versions: List[LinkRelationVersion],
        ) -> model_resources_pb2.VersionedLinkRelationAttributeValue:

            return model_resources_pb2.VersionedLinkRelationAttributeValue(
                versions=[
                    to_proto_link_relation_version(version) for version in versions
                ]
            )

        proto_entries = [to_proto_link_relation_entry(entry) for entry in entries]

        request = model_pb2.UpdateVersionedLinkRelationAttributeRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=_to_proto_attribute_mesh_id(target),
            interval=proto_interval,
            entries=proto_entries,
        )
        return request

    def _to_proto_singular_attribute_value(
        self, v: SIMPLE_TYPE
    ) -> model_resources_pb2.AttributeValue:
        att_value = model_resources_pb2.AttributeValue()
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
            raise RuntimeError(
                "Not supported value type. Supported simple types are: boolean, float, int, str, datetime."
            )

        return att_value

    def _to_update_attribute_request_values(
        self, value: SIMPLE_TYPE_OR_COLLECTION
    ) -> Tuple[
        model_resources_pb2.AttributeValue | None,
        List[model_resources_pb2.AttributeValue] | None,
    ]:
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
        new_curve_type: Timeseries.Curve | None,
        new_unit_of_measurement_id: resources_pb2.Guid | None,
    ) -> time_series_pb2.UpdateTimeseriesResourceRequest:
        request = time_series_pb2.UpdateTimeseriesResourceRequest(
            session_id=_to_proto_guid(self.session_id),
            timeseries_resource_key=timeseries_key,
        )

        fields_to_update = []
        if new_curve_type is not None:
            fields_to_update.append("new_curve_type")
            request.new_curve_type.CopyFrom(_to_proto_curve_type(new_curve_type))

        if new_unit_of_measurement_id is not None:
            fields_to_update.append("new_unit_of_measurement_id")
            request.new_unit_of_measurement_id.CopyFrom(new_unit_of_measurement_id)

        request.field_mask.CopyFrom(
            protobuf.field_mask_pb2.FieldMask(paths=fields_to_update)
        )
        return request

    def _get_rating_curve_versions_impl(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        start_time: datetime,
        end_time: datetime,
        versions_only: bool,
    ) -> typing.Generator[typing.Any, model_pb2.GetRatingCurveVersionsResponse, None]:
        """Generator implementation of get_rating_curve_versions.

        Yields the protobuf request, receives the protobuf response, and yields
        the final result.
        """

        if start_time is None or end_time is None:
            raise TypeError("start_time and end_time must both have a value")

        interval = _to_proto_utcinterval(start_time, end_time)

        request = model_pb2.GetRatingCurveVersionsRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=_to_proto_attribute_mesh_id(target),
            interval=interval,
            versions_only=versions_only,
        )

        response = yield request

        # name of the field in proto file is a Python keyword
        # need to use `getattr` to get its value, see:
        # https://developers.google.com/protocol-buffers/docs/reference/python-generated#keyword-conflicts
        yield [
            RatingCurveVersion(
                x_range_from=proto_version.x_range_from,
                valid_from_time=getattr(proto_version, "from").ToDatetime(
                    dateutil.tz.UTC
                ),
                x_value_segments=[
                    RatingCurveSegment(
                        proto_segment.x_range_until,
                        proto_segment.factor_a,
                        proto_segment.factor_b,
                        proto_segment.factor_c,
                    )
                    for proto_segment in proto_version.x_value_segments
                ],
            )
            for proto_version in response.versions
        ]

    def _prepare_update_rating_curve_versions_request(
        self,
        target: Union[uuid.UUID, str, AttributeBase],
        start_time: datetime,
        end_time: datetime,
        new_versions: List[RatingCurveVersion],
    ) -> model_pb2.UpdateRatingCurveVersionsRequest:
        if start_time is None or end_time is None:
            raise TypeError("start_time and end_time must both have a value")

        def to_proto_rating_curve_segment(
            segment: RatingCurveSegment,
        ) -> model_resources_pb2.RatingCurveSegment:
            return model_resources_pb2.RatingCurveSegment(
                x_range_until=segment.x_range_until,
                factor_a=segment.factor_a,
                factor_b=segment.factor_b,
                factor_c=segment.factor_c,
            )

        def to_proto_rating_curve_version(
            version: RatingCurveVersion,
        ) -> model_resources_pb2.RatingCurveVersion:
            proto_segments = [
                to_proto_rating_curve_segment(segment)
                for segment in version.x_value_segments
            ]

            proto_version = model_resources_pb2.RatingCurveVersion(
                x_range_from=version.x_range_from, x_value_segments=proto_segments
            )

            # name of the field in proto file is a Python keyword
            # need to use `setattr`, but because it is not a simple type
            # first we need to call `getattr` and then set its value via
            # CopyFrom or FromDatetime, see:
            # https://developers.google.com/protocol-buffers/docs/reference/python-generated#keyword-conflicts
            getattr(proto_version, "from").FromDatetime(version.valid_from_time)
            return proto_version

        proto_versions = [
            to_proto_rating_curve_version(version) for version in new_versions
        ]

        request = model_pb2.UpdateRatingCurveVersionsRequest(
            session_id=_to_proto_guid(self.session_id),
            attribute=_to_proto_attribute_mesh_id(target),
            interval=_to_proto_utcinterval(start_time, end_time),
            versions=proto_versions,
        )
        return request

    def _prepare_run_simulation_request(
        self,
        model: str,
        case: str,
        start_time: datetime,
        end_time: datetime,
        resolution: timedelta,
        scenario: int,
        return_datasets: bool,
    ) -> hydsim_pb2.RunHydroSimulationRequest:
        if start_time is None or end_time is None:
            raise TypeError("start_time and end_time must both have a value")

        case_group, case_name = case.split("/", maxsplit=1)
        simulation = f"Model/{model}/{case_group}.has_OptimisationCases/{case_name}.has_OptimisationParameters/Optimal.has_HydroSimulation/HydroSimulation"

        proto_resolution = None
        if resolution is not None:
            proto_resolution = protobuf.duration_pb2.Duration()
            proto_resolution.FromTimedelta(resolution)

        return hydsim_pb2.RunHydroSimulationRequest(
            session_id=_to_proto_guid(self.session_id),
            simulation=_to_proto_object_mesh_id(simulation),
            interval=_to_proto_utcinterval(start_time, end_time),
            scenario=scenario,
            resolution=proto_resolution,
            return_datasets=return_datasets,
        )

    def _prepare_run_inflow_calculation_request(
        self,
        targets: List[Object],
        start_time: datetime,
        end_time: datetime,
        resolution: timedelta,
        return_datasets: bool,
    ) -> hydsim_pb2.RunInflowCalculationRequest:
        if start_time is None or end_time is None:
            raise TypeError("start_time and end_time must both have a value")

        if len(targets) != 1:
            raise ValueError(f"expected one water course, found {len(targets)}")

        proto_resolution = None
        if resolution is not None:
            proto_resolution = protobuf.duration_pb2.Duration()
            proto_resolution.FromTimedelta(resolution)

        return hydsim_pb2.RunInflowCalculationRequest(
            session_id=_to_proto_guid(self.session_id),
            watercourse=_to_proto_object_mesh_id(targets[0].id),
            interval=_to_proto_utcinterval(start_time, end_time),
            resolution=proto_resolution,
            return_datasets=return_datasets,
        )

    def _prepare_get_mc_file_request(
        self,
        model: str,
        case: str,
        start_time: datetime,
        end_time: datetime,
    ):
        if start_time is None or end_time is None:
            raise TypeError("start_time and end_time must both have a value")

        case_group, case_name = case.split("/", maxsplit=1)
        optimisation_case = (
            f"Model/{model}/{case_group}.has_OptimisationCases/{case_name}"
        )

        return hydsim_pb2.GetMcFileRequest(
            session_id=_to_proto_guid(self.session_id),
            optimisation_case=_to_proto_object_mesh_id(optimisation_case),
            interval=_to_proto_utcinterval(start_time, end_time),
        )

    def _get_unit_of_measurement_id_by_name(
        self,
        unit_of_measurement: str,
        list_response: model_definition_pb2.ListUnitsOfMeasurementResponse,
    ) -> resources_pb2.Guid:
        new_unit_of_measurement_id = None

        for proto_unit in list_response.units_of_measurement:
            if proto_unit.name == unit_of_measurement:
                new_unit_of_measurement_id = proto_unit.id
                break

        if new_unit_of_measurement_id is None:
            raise ValueError("invalid unit of measurement provided")

        return new_unit_of_measurement_id
