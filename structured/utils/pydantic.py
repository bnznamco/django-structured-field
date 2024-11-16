from typing import Any, Dict, List, ForwardRef, get_origin, get_args
from structured.pydantic.fields import ForeignKey, QuerySet
from django.db.models import Model as DjangoModel
from django.db.models.query import QuerySet as DjangoQuerySet
from pydantic._internal._typing_extra import eval_type_lenient
from inspect import isclass
from structured.utils.typing import get_type
from pydantic import Field
from typing_extensions import Annotated


def patch_annotation(annotation: Any, cls_namespace: Dict[str, Any]) -> Any:
    if isinstance(annotation, str):
        annotation = eval_type_lenient(annotation, cls_namespace)
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin == ForwardRef:
        return patch_annotation(eval_type_lenient(annotation, cls_namespace), cls_namespace)
    elif isclass(origin) and issubclass(origin, ForeignKey):
        return annotation
    elif isclass(origin) and issubclass(origin, QuerySet):
        model = get_type(annotation)
        default_manager = getattr(model, "_default_manager", DjangoQuerySet[model]) or DjangoQuerySet[model]
        return Annotated[
            annotation,
            Field(default_factory=default_manager.none),
        ]
    elif isclass(annotation) and issubclass(annotation, DjangoModel):
        return ForeignKey[annotation]
    elif len(args) > 0 and origin is not None and origin != type:
        new_args = set()
        for arg in args:
            new_args.add(patch_annotation(arg, cls_namespace))
        args = tuple(new_args)
        if origin is list:
            origin = List
        elif origin is dict:
            origin = Dict
        return origin[args]
    return annotation


def map_method_aliases(new_cls):
    method_aliases = {
        "validate_python": "model_validate",
        "validate_json": "model_validate_json",
        # "dump_python": "model_dump",
        # "dump_json": "model_dump_json",
        "json_schema": "model_json_schema",
    }
    for alias_name, target_name in method_aliases.items():
        setattr(new_cls, alias_name, getattr(new_cls, target_name))
    return new_cls
