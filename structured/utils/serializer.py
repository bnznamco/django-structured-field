from typing import Optional, Sequence, Union, Type, Tuple, Dict, List
from rest_framework import serializers
from django.db import models as django_models


def build_standard_model_serializer(
    model,
    depth,
    bases: Optional[Tuple[Type[serializers.Serializer]]] = None,
    fields: Union[str, Sequence[str]] = "__all__",
):
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


def minimal_serialization(
    instance: Type[django_models.Model],
) -> Dict[str, Union[str, int]]:
    return (
        {
            "id": instance.pk,
            "name": instance.__str__(),
            "model": f"{instance._meta.app_label}.{instance._meta.model_name}",
        }
        if instance
        else None
    )


def minimal_list_serialization(
    instances: List[Type[django_models.Model]],
) -> List[Dict[str, Union[str, int]]]:
    return [minimal_serialization(instance) for instance in instances]
