from typing import Any, Dict, List, Type, ForwardRef, get_origin, get_args, Literal
from structured.pydantic.fields import ForeignKey, QuerySet
from django.db.models import Model as DjangoModel
from django.db.models.query import QuerySet as DjangoQuerySet
from pydantic._internal._typing_extra import eval_type_lenient
from inspect import isclass
from structured.utils.typing import get_type
from pydantic import Field
from typing_extensions import Annotated
import logging

logger = logging.getLogger(__name__)


def patch_annotation(annotation: Any, cls_namespace: Dict[str, Any]) -> Any:
    logger.debug("[patch_annotation] Called with annotation: %r", annotation)
    """Patch the annotation to handle special cases for Django and Pydantic."""
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        logger.debug("[patch_annotation] Need to evaluate string annotation: %r", annotation)
    origin = get_origin(annotation)
    if origin == Literal:
        logger.debug("[patch_annotation] Detected Literal, returning as is: %r", annotation)
        return annotation
    args = get_args(annotation)
    if origin == ForwardRef:
        result = patch_annotation(eval_type_lenient(annotation, cls_namespace), cls_namespace)
        logger.debug("[patch_annotation] Detected ForwardRef, evaluated: %r", result)
        return result
    elif isclass(origin) and issubclass(origin, ForeignKey):
        logger.debug("[patch_annotation] Detected ForeignKey, returning as is: %r", annotation)
        return annotation
    elif isclass(origin) and issubclass(origin, QuerySet):
        model = get_type(annotation)
        default_manager = getattr(model, "_default_manager", DjangoQuerySet[model]) or DjangoQuerySet[model]

        result = Annotated[
            annotation,
            Field(default_factory=lambda: default_manager.none()),
        ]
        logger.debug("[patch_annotation] Detected QuerySet, patched: %r", result)
        return result
    elif isclass(annotation) and issubclass(annotation, DjangoModel):
        result = ForeignKey[annotation]
        logger.debug("[patch_annotation] Detected DjangoModel, patched: %r", result)
        return result
    elif len(args) > 0 and origin is not None and origin != type:
        logger.debug(
            "[patch_annotation] Detected generic type (origin: %r) with args: %r, patching recursively.",
            origin, args
        )
        new_args = set()
        for arg in args:
            new_args.add(patch_annotation(arg, cls_namespace))
        args = tuple(new_args)
        if origin is list:
            origin = List
        elif origin is dict:
            origin = Dict
        result = origin[args]
        logger.debug("[patch_annotation] Result of recursion: %r", result)
        return result
    logger.debug("[patch_annotation] No patch needed, returning annotation as is: %r", annotation)
    return annotation


def map_method_aliases(new_cls: Type) -> Type:
    """Map method aliases for a new class."""
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
