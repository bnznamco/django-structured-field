import copy
import json
from typing import Any, Union, TYPE_CHECKING, Type, List

from django.db.models import JSONField
from django.core import exceptions
from django.db.models.query_utils import DeferredAttribute
from pydantic import (
    TypeAdapter,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from structured.utils.cast import cast_to_python, cast_to_model
from structured.utils.errors import map_pydantic_errors
from structured.widget.fields import StructuredJSONFormField
from pydantic import ValidationError as PydanticValidationError
from typing_extensions import Annotated
from pydantic.fields import Field
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from structured.pydantic.models import BaseModel


_INSTANCE_CACHE_ATTR = "_structured_instance_cache"


def _get_instance_cache(instance):
    """
    Return the per-instance ``Cache`` attached to a Django model
    instance, creating it lazily. Used to share one fetch pool across
    every ``StructuredJSONField`` on the same row.

    The cache lives as long as the instance does (typically a request)
    and is naturally GC'd alongside it.
    """
    from structured.cache.cache import Cache

    cache = getattr(instance, _INSTANCE_CACHE_ATTR, None)
    if cache is None:
        cache = Cache()
        try:
            object.__setattr__(instance, _INSTANCE_CACHE_ATTR, cache)
        except (AttributeError, TypeError):
            # Some objects (e.g. __slots__ without this attr) refuse
            # arbitrary attributes. Fall back to a per-call cache by
            # returning None — the cache engine handles that path.
            return None
    return cache


class StructuredDescriptior(DeferredAttribute):
    field: "StructuredJSONField"

    def __set__(self, instance, value):
        instance.__dict__[self.field.attname] = value
        # A new assignment invalidates any stashed pre-validation snapshot.
        instance.__dict__.pop(self.field.raw_attname, None)

    def __get__(self, instance, cls=None):
        from structured.cache.cache import CACHE_CONTEXT_KEY

        value = super().__get__(instance, cls)
        if not self.field.check_type(value):
            context = None
            raw_copy = None
            if instance is not None:
                # Snapshot the raw data BEFORE validation: the cache engine
                # mutates the input in place (ValueWithCache splicing), and
                # successful validation replaces it entirely.
                raw_copy = copy.deepcopy(value)
                parent_cache = _get_instance_cache(instance)
                if parent_cache is not None:
                    context = {CACHE_CONTEXT_KEY: parent_cache}
            try:
                value = self.field.schema.validate_python(value, context=context)
            except PydanticValidationError as e:
                logger.warning(
                    "Error validating field '%s' with value '%s': %s",
                    self.field.name,
                    value,
                    map_pydantic_errors(e),
                )
                if instance is not None:
                    instance.__dict__[self.field.raw_attname] = raw_copy
                return value
            self.__set__(instance, value)
            instance.__dict__[self.field.raw_attname] = raw_copy
        return value


class StructuredJSONField(JSONField):
    # TODO: share cache in querysets of models having this same field
    # TODO: write queries for prefetch related for models inside the field

    descriptor_class = StructuredDescriptior

    @property
    def raw_attname(self) -> str:
        """Instance __dict__ key holding the pre-validation raw snapshot."""
        return "_%s_raw" % self.attname

    def validate(self, value, model_instance):
        try:
            self.schema.validate_python(cast_to_python(value))
        except PydanticValidationError as e:
            logger.debug(
                "[StructuredJSONField] Validation error: %s",
                map_pydantic_errors(e, self.many),
            )
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={
                    "value": value,
                    "error_detail": map_pydantic_errors(e, self.many),
                },
            )

    @property
    def list_data_validator(self):
        from structured.cache.cache import CACHE_CONTEXT_KEY

        def list_data_validator(
            value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
        ) -> Any:
            parent_cache = None
            if info.context:
                parent_cache = info.context.get(CACHE_CONTEXT_KEY)
            if info.mode == "json" and isinstance(value, str):
                return self.schema.validate_python(
                    self.orig_schema._cache_engine.build_cache(
                        json.loads(value), parent_cache=parent_cache
                    ),
                    context=info.context,
                )
            return handler(
                self.orig_schema._cache_engine.build_cache(
                    value, parent_cache=parent_cache
                )
            )

        return list_data_validator

    def __init__(self, schema: Type["BaseModel"], *args: Any, **kwargs: Any) -> None:
        self.orig_schema = schema
        self.schema = schema
        default = kwargs.get("default", dict)
        self.file_handler = kwargs.pop("file_handler", "")
        self.many = kwargs.pop(
            "many", isinstance(default() if callable(default) else default, list)
        )
        if self.many:
            self.schema = TypeAdapter(
                Annotated[
                    List[self.schema],
                    Field(default_factory=list),
                    WrapValidator(self.list_data_validator),
                ]
            )
        return super().__init__(*args, **kwargs)

    def check_type(self, value: Any):
        if self.many:
            return isinstance(value, list) and all(
                isinstance(v, self.orig_schema) for v in value
            )
        return isinstance(value, self.orig_schema)

    def get_prep_value(
        self, value: Union[List[Type["BaseModel"]], Type["BaseModel"]]
    ) -> str:
        value = cast_to_model(value, self.orig_schema)
        if isinstance(value, list) and self.many:
            return self.schema.dump_json(value, exclude_unset=True).decode()
        return value.model_dump_json(exclude_unset=True)

    # This prevents some random errors in sqlite envs (to be investigated)
    def get_db_prep_value(
        self,
        value: Union[List[Type["BaseModel"]], Type["BaseModel"]],
        connection: Any,
        prepared: bool = False,
    ) -> str:
        return self.get_prep_value(value)

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> Any:
        data = super().from_db_value(value, expression, connection)
        if isinstance(data, str):
            data = json.loads(data)
        return data

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["schema"] = self.orig_schema
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": StructuredJSONFormField,
                "schema": self.schema,
                **kwargs,
            }
        )

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        if "%s_raw" % self.name not in cls.__dict__:
            setattr(
                cls,
                "%s_raw" % self.name,
                property(self.__get_raw_data, self.__set_raw_data, self.__del_raw_data),
            )

    def __get_raw_data(self, instance):
        """
        Return THIS instance's raw (pre-validation) JSON without triggering
        validation or relation queries. Precedence: the snapshot stashed by
        the descriptor before validation; else the not-yet-validated value
        sitting in ``instance.__dict__``; else a python-mode dump of an
        already-validated value (e.g. assigned directly as a schema instance).
        Deferred fields (``.only()``/``.defer()``) yield None.
        """
        if self.raw_attname in instance.__dict__:
            return instance.__dict__[self.raw_attname]
        value = instance.__dict__.get(self.attname)
        if value is None or not self.check_type(value):
            return value
        return cast_to_python(value)

    def __set_raw_data(self, instance, value):
        # Route through the descriptor so the stale snapshot is invalidated.
        setattr(instance, self.attname, value)

    def __del_raw_data(self, instance):
        del instance.__dict__[self.attname]
        instance.__dict__.pop(self.raw_attname, None)
