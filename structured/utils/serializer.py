from typing import Optional, Sequence, Union, Type, Tuple, Dict, List
from rest_framework import serializers
from django.db import models as django_models


class BaseModelSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()

    def get_model(self, obj: django_models.Model) -> str:
        """Get the model name of the object."""
        return f"{obj._meta.app_label}.{obj._meta.model_name}"

    def get_default_field_names(self, declared_fields, info):
        original = super().get_default_field_names(declared_fields, info)
        if "model" not in original:
            original = ["model"] + original
        return original


def build_standard_model_serializer(
    model: Type[django_models.Model],
    depth: int,
    bases: Optional[Tuple[Type[serializers.Serializer]]] = None,
    fields: Union[str, Sequence[str]] = "__all__",
) -> Type[serializers.ModelSerializer]:
    """Build a standard model serializer with the given parameters."""
    if bases is None:
        bases = (serializers.ModelSerializer,)
    bases = (BaseModelSerializer,) + tuple(bases)
    return type(
        f"{model.__name__}StandardSerializer",
        bases,
        {
            "Meta": type(
                "Meta",
                (object,),
                {"model": model, "depth": depth, "fields": fields},
            )
        },
    )


def minimal_serialization(instance: django_models.Model) -> Optional[Dict[str, Union[str, int]]]:
    """Serialize a model instance minimally."""
    return (
        {
            "id": instance.pk,
            "name": instance.__str__(),
            "model": f"{instance._meta.app_label}.{instance._meta.model_name}",
        }
        if instance
        else None
    )


def minimal_list_serialization(instances: List[django_models.Model]) -> List[Dict[str, Union[str, int]]]:
    """Serialize a list of model instances minimally."""
    return [minimal_serialization(instance) for instance in instances]
