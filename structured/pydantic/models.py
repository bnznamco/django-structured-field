from inspect import isclass
from typing import Any, Dict, Tuple, get_origin, Optional, Type
from pydantic._internal._typing_extra import (
    get_cls_types_namespace,
    parent_frame_namespace,
    eval_type_lenient,
)
from pydantic._internal._generics import PydanticGenericMetadata
from pydantic._internal._model_construction import ModelMetaclass
from django.db.models import Model as DjangoModel
from pydantic import BaseModel as PyDBaseModel
from pydantic import Field, model_validator
from typing_extensions import Annotated

from .fields import ForeignKey, QuerySet
from structured.utils.typing import get_type
from structured.utils.pydantic import map_method_aliases
from abc import ABCMeta


class BaseModelMeta(ModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Dict[str, Any],
        __pydantic_generic_metadata__: Optional[PydanticGenericMetadata] = None,
        __pydantic_reset_parent_namespace__: bool = True,
        _create_model_module: Optional[str] = None,
        **kwargs,
    ):
        annotations: dict = namespace.get("__annotations__", {})
        for base in bases:
            for base_ in base.__mro__:
                if base_ is PyDBaseModel:
                    break
                annotations.update(base_.__annotations__)
        cls_namespace = BaseModelMeta.__get_class_types_namespace__(
            mcs, cls_name, bases, namespace
        )
        for field in annotations:
            annotation = annotations[field]
            if isinstance(annotation, str):
                annotation = eval_type_lenient(annotation, cls_namespace)
            origin = get_origin(annotation)
            if isclass(annotation) and issubclass(annotation, DjangoModel):
                annotations[field] = ForeignKey[annotation]
            elif isclass(origin) and issubclass(origin, QuerySet):
                annotations[field] = Annotated[
                    annotation,
                    Field(default_factory=get_type(annotation)._default_manager.none),
                ]
        namespace["__annotations__"] = annotations
        return map_method_aliases(
            super().__new__(
                mcs,
                cls_name,
                bases,
                namespace,
                __pydantic_generic_metadata__,
                __pydantic_reset_parent_namespace__,
                _create_model_module,
                **kwargs,
            )
        )

    @staticmethod
    def __get_class_types_namespace__(
        mcs,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Dict[str, Any],
    ) -> Dict[str, Any]:
        cls = ABCMeta.__new__(mcs, cls_name, bases, namespace)
        return get_cls_types_namespace(cls, parent_frame_namespace())


class BaseModel(PyDBaseModel, metaclass=BaseModelMeta):
    @model_validator(mode="wrap")
    @classmethod
    def build_cache(cls, data, handler) -> Any:
        from structured.cache.engine import CacheEngine

        data = CacheEngine.from_model(cls).inject_cache(data)
        instance: "BaseModel" = handler(data)
        return CacheEngine.retrieve_missing_valwithcache(instance)
