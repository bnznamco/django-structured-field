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
from structured.utils.errors import map_pydantic_errors
from structured.widget.fields import StructuredJSONFormField
from pydantic import ValidationError as PydanticValidationError
from typing_extensions import Annotated
from pydantic.fields import Field


if TYPE_CHECKING:
    from structured.pydantic.models import BaseModel


class StructuredDescriptior(DeferredAttribute):
    field: "StructuredJSONField"

    def __set__(self, instance, value):
        # TODO: check if it's better to validate here or in __get__ function (performance reasons)
        # if not self.field.check_type(value):
        #     value = self.field.schema.validate_python(value)
        instance.__dict__[self.field.attname] = value

    def __get__(self, instance, cls=None):
        value = super().__get__(instance, cls)
        if not self.field.check_type(value):
            value = self.field.schema.validate_python(value)
            self.__set__(instance, value)
        return value


class StructuredJSONField(JSONField):
    # TODO: share cache in querysets of models having this same field
    # TODO: write queries for prefetch related for models inside the field

    descriptor_class = StructuredDescriptior

    def validate(self, value, model_instance):
        try:
            self.schema.validate_python(value)
        except PydanticValidationError as e:
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
        def list_data_validator(
            value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
        ) -> Any:
            if info.mode == "json" and isinstance(value, str):
                return self.schema.validate_python(
                    self.orig_schema._cache_engine.build_cache(json.loads(value))
                )
            return handler(self.orig_schema._cache_engine.build_cache(value))

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
            return json.loads(data)
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
