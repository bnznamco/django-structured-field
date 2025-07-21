from pydantic import TypeAdapter, ValidationError as PydanticValidationError
from rest_framework import serializers
from rest_framework.utils import model_meta
from typing import TYPE_CHECKING, Union, List

from structured.fields import StructuredJSONField as DjangoStructuredJSONField
from structured.utils.dict import dict_merge
from structured.utils.errors import map_pydantic_errors


if TYPE_CHECKING:  # pragma: no cover
    from structured.pydantic.models import BaseModel


class StructuredJSONField(serializers.JSONField):
    """
    This field allows to serialize and deserialize structured data.
    """

    schema: Union["BaseModel", TypeAdapter] = None

    def __init__(self, **kwargs):
        self.schema = kwargs.pop("schema", None)
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        if self.schema is None and isinstance(parent, serializers.ModelSerializer):
            info = model_meta.get_field_info(parent.Meta.model)
            field = info.fields[field_name]
            self.schema = field.schema
            self.many = field.many
            self.json_schema = field.schema.json_schema()
        super().bind(field_name, parent)

    def to_representation(self, instance: Union["BaseModel", List["BaseModel"]]):
        if isinstance(instance, list) and self.many:
            return super().to_representation(
                self.schema.dump_python(instance, exclude_unset=True, context=self.context or {})
            )
        return super().to_representation(instance.model_dump(exclude_unset=True, context=self.context))

    def to_internal_value(self, data: Union[list, dict]):
        try:
            request = self.context.get('request')
            is_patch = request and request.method == 'PATCH'
            if is_patch and getattr(self.parent, "instance", None) and not isinstance(data, list):
                old_data = getattr(self.parent.instance, self.field_name, None) or {}
                data = dict_merge(old_data.model_dump(exclude_unset=True) if old_data else {}, data)
            return self.schema.validate_python(super().to_internal_value(data))
        except PydanticValidationError as e:
            raise serializers.ValidationError(map_pydantic_errors(e, self.many))


class FieldsOverrideMixin:
    """
    This mixin automatically includes the structured fields in the serializer
    """

    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        DjangoStructuredJSONField: StructuredJSONField,
    }


class StructuredModelSerializer(FieldsOverrideMixin, serializers.ModelSerializer):
    """
    This serializer allows to serialize and deserialize structured data.
    """
    pass
