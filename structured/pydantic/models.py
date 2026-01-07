import sys
from typing import Any, Dict, Tuple, Optional, Type
from pydantic._internal._typing_extra import parent_frame_namespace
from pydantic._internal._generics import PydanticGenericMetadata
from pydantic._internal._model_construction import ModelMetaclass, build_lenient_weakvaluedict
from pydantic import ConfigDict, BaseModel as PyDBaseModel
from structured.utils.pydantic import map_method_aliases, patch_annotation
from abc import ABCMeta
from structured.cache import CacheEngine, CacheEnabledModel
from structured.utils.namespace import merge_cls_and_parent_ns


def _get_raw_annotations(namespace: Dict[str, Any]) -> Dict[str, Any]:
    """Get annotations from namespace, handling Python 3.14+ deferred annotations."""
    if sys.version_info >= (3, 14):
        if '__annotations__' in namespace:
            # `from __future__ import annotations` was used in the model's module
            return namespace['__annotations__']
        else:
            # See https://docs.python.org/3.14/library/annotationlib.html#using-annotations-in-a-metaclass:
            from annotationlib import Format, call_annotate_function, get_annotate_from_class_namespace

            if annotate := get_annotate_from_class_namespace(namespace):
                return call_annotate_function(annotate, format=Format.FORWARDREF)
            else:
                return {}
    else:
        return namespace.get('__annotations__', {})


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
        annotations: dict = dict(_get_raw_annotations(namespace))
        for base in bases:
            for base_ in base.__mro__:
                if base_ is PyDBaseModel:
                    break
                annotations.update(getattr(base_, "__annotations__", {}))
        cls_namespace = BaseModelMeta.__get_class_types_namespace__(
            mcs, cls_name, bases, namespace
        )
        for field in annotations:
            annotations[field] = patch_annotation(annotations[field], cls_namespace)
        namespace["__annotations__"] = annotations
        new_class = map_method_aliases(
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
        return CacheEngine.add_cache_engine_to_class(new_class)

    @staticmethod
    def __get_class_types_namespace__(
        mcs,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Dict[str, Any],
    ) -> Dict[str, Any]:
        cls = ABCMeta.__new__(mcs, cls_name, bases, namespace)
        parent_ns = parent_frame_namespace()
        parent_namespace = build_lenient_weakvaluedict(parent_ns) if parent_ns else None
        return merge_cls_and_parent_ns(cls, parent_namespace)


class BaseModel(CacheEnabledModel, PyDBaseModel, metaclass=BaseModelMeta):
    model_config = ConfigDict(extra='ignore')
