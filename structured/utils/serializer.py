from typing import Optional, Sequence, Union, Type, Tuple, TYPE_CHECKING, List
from django.db import models as django_models
from rest_framework import serializers
from rest_framework.utils import model_meta
from pydantic import TypeAdapter
from structured.settings import settings
from structured.utils.context import increase_context_depth


if TYPE_CHECKING:  # pragma: no cover
    from structured.pydantic.models import BaseModel


class JSONFieldInnerSerializer(serializers.JSONField):
    """
    This field allows to serialize structured data.
    """

    schema: Union["BaseModel", TypeAdapter] = None

    def __init__(self, **kwargs):
        self.schema = kwargs.pop("schema", None)
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        if self.schema is None and isinstance(parent, serializers.ModelSerializer):
            field = model_meta.get_field_info(parent.Meta.model).fields[field_name]
            self.schema = field.schema
            self.many = field.many
        super().bind(field_name, parent)

    def to_representation(self, instance: Union["BaseModel", List["BaseModel"]]):
        if isinstance(instance, list) and self.many:
            return super().to_representation(
                self.schema.dump_python(
                    instance, exclude_unset=True, context=self.context or {}
                )
            )
        return super().to_representation(
            instance.model_dump(exclude_unset=True, context=self.context)
        )


class BaseModelSerializer(serializers.Serializer):
    model = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs["context"] = increase_context_depth(kwargs.get("context", {}), 1)
        super().__init__(*args, **kwargs)

    def get_model(self, obj: django_models.Model) -> str:
        """Get the model name of the object."""
        return f"{obj._meta.app_label}.{obj._meta.model_name}"

    def get_default_field_names(self, declared_fields, info):
        original = super().get_default_field_names(declared_fields, info)
        if "model" not in original:
            original = ["model"] + original
        return original

    def to_representation(self, instance):
        context = self.context or {}
        mode = context.get("mode", "python")
        current_depth = context.get("__structured_depth", 1)
        max_depth = settings.STRUCTURED_SERIALIZATION_MAX_DEPTH
        if mode == "python" and current_depth <= max_depth:
            return super().to_representation(instance)
        return instance and {
            "id": instance.pk,
            "name": instance.__str__(),
            "model": f"{instance._meta.app_label}.{instance._meta.model_name}",
        }


def build_model_serializer(
    model: Type[django_models.Model],
    bases: Optional[Tuple[Type[serializers.Serializer]]] = None,
    fields: Union[str, Sequence[str]] = "__all__",
) -> Type[serializers.Serializer]:
    """Build a standard model serializer with the given parameters."""
    if bases is None:
        bases = ()
    bases = tuple(bases) + (BaseModelSerializer,)
    declaration = {}
    if model and issubclass(model, django_models.Model):
        from structured.fields import StructuredJSONField as DjangoStructuredJSONField

        bases += (serializers.ModelSerializer,)
        declaration["Meta"] = type(
            "Meta",
            (object,),
            {"model": model, "fields": fields, "depth": 0},
        )
        declaration["serializer_field_mapping"] = {
            **serializers.ModelSerializer.serializer_field_mapping,
            DjangoStructuredJSONField: JSONFieldInnerSerializer,
        }
    serializer_class_name = getattr(model, "__name__", "Unknown") + "StructuredSerializer"
    return type(serializer_class_name, bases, declaration)
