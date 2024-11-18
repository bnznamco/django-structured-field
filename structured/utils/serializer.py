from typing import Optional, Sequence, Union, Type, Tuple, Dict, List
from rest_framework import serializers
from django.db import models as django_models


def build_standard_model_serializer(
    model: Type[django_models.Model],
    depth: int,
    bases: Optional[Tuple[Type[serializers.Serializer]]] = None,
    fields: Union[str, Sequence[str]] = "__all__",
) -> Type[serializers.ModelSerializer]:
    """Build a standard model serializer with the given parameters."""
    if bases is None:
        bases = (serializers.ModelSerializer,)
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
