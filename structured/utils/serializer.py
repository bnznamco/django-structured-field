from typing import Optional, Sequence, Union
from rest_framework import serializers


def build_standard_model_serializer(
    model,
    depth,
    bases: Optional[tuple[type[serializers.Serializer]]] = None,
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
