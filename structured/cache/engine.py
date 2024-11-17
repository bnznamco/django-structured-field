from __future__ import annotations
from collections import defaultdict
from inspect import isclass
from typing import Any, Dict, Sequence, Type, TYPE_CHECKING
from typing_extensions import get_args, get_origin
from structured.settings import settings
from structured.pydantic.fields import ForeignKey, QuerySet
from structured.utils.typing import find_model_type_from_args, get_type
from structured.utils.getter import pointed_getter
from structured.utils.setter import pointed_setter
from django.db.models import Model as DjangoModel
from typing import Iterable, Union
from pydantic import model_validator
import threading
from django.apps import apps
from django.db.models.signals import post_save, pre_delete

if TYPE_CHECKING:
    from structured.pydantic.models import BaseModel

# TODO:
# ::: Actually this is a first draft.
# The system should be more type safe.
# It should handle initialization made with model instance not only dicts
# Neet to check if there are problems with different formats for pks (model instaces or string or dicts)


class CacheEnabledModel:
    _cache_engine: CacheEngine

    @model_validator(mode="wrap")
    @classmethod
    def build_cache(cls, data, handler) -> Any:
        data = cls._cache_engine.build_cache(data)
        instance: "BaseModel" = handler(data)
        return cls._cache_engine.fetch_cache(instance)


class Cache(defaultdict):
    def flush(self, data: Union[DjangoModel, Iterable[DjangoModel], None] = None, **kwargs):
        model = kwargs.get("model", None)
        if model:
            if isinstance(model, str):
                model = next(
                    (m.__name__ for m in self.keys() if m.__name__ == model), None
                )
            if model in self:
                del self[model]
        if data:
            if isinstance(data, DjangoModel):
                model = data.__class__
                if model in self and data.pk in self[model]:
                    del self[model][data.pk]
            else:
                for instance in data:
                    model = instance.__class__
                    if model in self and instance.pk in self[model]:
                        del self[model][instance.pk]
        else:
            self.clear()

    def set(self, data: Union[DjangoModel, Iterable[DjangoModel]]):
        if isinstance(data, DjangoModel):
            self[data.__class__].update({data.pk: data})
        else:
            for instance in data:
                self[instance.__class__].update({instance.pk: instance})

    def __init__(self) -> None:
        super().__init__(dict)
        def on_save(sender, instance, **kwargs):
            cache = get_global_cache() or self
            if instance.__class__ in cache:
                cache.set(instance)
        def on_delete(sender, instance, **kwargs):
            cache = get_global_cache() or self
            if instance.__class__ in cache:
                cache.flush(instance)
        post_save.connect(on_save)
        pre_delete.connect(on_delete)


class ThreadSafeCache(Cache):
    """
    It is a singleton cache object that allows sharing cache data between fields and instances.
    Need to improve data reliability and thread safety.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        
        return cls._instance


class ValueWithCache:
    def __init__(self, cache, model, value) -> None:
        self.cache: Cache = cache
        self.value: Union[Iterable[Union[str, int]], str, int] = value
        self.model: Type[DjangoModel] = model

    def retrieve(self):
        cache = self.cache.get(self.model)
        if hasattr(self.value, "__iter__") and not isinstance(self.value, str):
            qs = self.model.objects.filter(pk__in=self.value)
            setattr(
                qs,
                "_result_cache",
                [cache[i] for i in self.value if i in cache] if cache else [],
            )
            return qs
        else:
            val = cache.get(self.value, None)
            if val is None:
                return self.model._default_manager.get(pk=self.value)
            else:
                return val


class RelInfo:
    FKField: str = "fk"
    QSField: str = "qs"
    RIField: str = "rel"
    RLField: str = "rel_l"

    def __init__(self, model, type, field) -> None:
        self.model = model
        self.type = type
        self.field = field


class CacheEngine:
    def __init__(self, related_fields: Dict[str, RelInfo]) -> None:
        self.__related_fields__ = related_fields

    @staticmethod
    def fetch_cache(instance):
        for field_name in instance.model_fields_set:
            val = getattr(instance, field_name, None)
            if isinstance(val, ValueWithCache):
                setattr(instance, field_name, val.retrieve())
            elif isinstance(val, CacheEnabledModel):
                setattr(instance, field_name, CacheEngine.fetch_cache(val))
        return instance

    @classmethod
    def from_model(cls, model: BaseModel) -> "CacheEngine":
        return cls(related_fields=cls.inspect_related_fields(model))

    @classmethod
    def inspect_related_fields(cls, model: Type[BaseModel]) -> Dict[str, RelInfo]:
        related = {}
        for field_name, field in model.model_fields.items():
            annotation = field.annotation
            origin = get_origin(annotation)
            args = get_args(annotation)

            if isclass(origin) and issubclass(origin, ForeignKey):
                related[field_name] = RelInfo(
                    get_type(annotation), RelInfo.FKField, field
                )
            elif isclass(origin) and issubclass(origin, QuerySet):
                related[field_name] = RelInfo(
                    get_type(annotation), RelInfo.QSField, field
                )

            elif isclass(origin) and issubclass(origin, Sequence):
                subclass = find_model_type_from_args(args, model, CacheEnabledModel)
                if subclass:
                    related[field_name] = RelInfo(subclass, RelInfo.RLField, field)

            elif isclass(annotation) and issubclass(annotation, CacheEnabledModel):
                related[field_name] = RelInfo(annotation, RelInfo.RIField, field)

            elif origin and origin is Union:
                subclass = find_model_type_from_args(args, model, CacheEnabledModel)
                if subclass:
                    related[field_name] = RelInfo(subclass, RelInfo.RIField, field)

        return related

    def get_all_fk_data(self, data):
        if isinstance(data, Sequence):
            fk_data = defaultdict(list)
            for index in range(len(data)):
                child_fk_data = self.get_all_fk_data(data[index])
                for model, touples in child_fk_data.items():
                    fk_data[model] += [(f"{index}.{t[0]}", t[1]) for t in touples]
            return fk_data
        return self.get_fk_data(data)

    # flake8: noqa: C901
    def get_fk_data(self, data):
        fk_data = defaultdict(list)
        if not data:
            return fk_data
        for field_name, info in self.__related_fields__.items():
            if info.type == RelInfo.FKField:
                value = pointed_getter(data, field_name, None)
                if info.model._meta.abstract:
                    if isinstance(value, dict) and "model" in value:
                        info.model = apps.get_model(*value["model"].split("."))
                    if isinstance(value, DjangoModel) and not value._meta.abstract:
                        info.model = value.__class__
                    elif isinstance(value, int) or isinstance(value, str) and value.isnumeric():
                        raise ValueError(
                            "Cannot retrieve abstract models from primary key only."
                        )
                if isinstance(value, DjangoModel):
                    info.model = value.__class__
                    value = value.pk
                if isinstance(value, dict):
                    info.model = apps.get_model(*value["model"].split("."))
                    value = value.get(info.model._meta.pk.attname, None)
                if value:
                    if isinstance(
                        value, ValueWithCache
                    ):  # needed to break recursive cache builds
                        fk_data = {}
                        break
                    attname = ""
                    if not info.model._meta.abstract:
                        attname = info.model._meta.pk.attname
                    fk_data[info.model].append(
                        (
                            field_name,
                            pointed_getter(value, attname, value),
                        )
                    )
            elif info.type == RelInfo.QSField:
                value = pointed_getter(data, field_name, [])
                if isinstance(value, list):
                    if any(
                        True for v in value if isinstance(v, ValueWithCache)
                    ):  # needed to break recursive cache builds
                        fk_data = {}
                        break
                    fk_data[info.model].append(
                        (
                            field_name,
                            [
                                pointed_getter(i, info.model._meta.pk.attname, i)
                                for i in value
                                if i
                            ],
                        )
                    )

            elif info.type == RelInfo.RLField:
                values = pointed_getter(data, field_name, [])
                if isinstance(values, list):
                    for index in range(len(values)):
                        for model, touples in (
                            self.from_model(info.model)
                            .get_all_fk_data(values[index])
                            .items()
                        ):
                            fk_data[model] += [
                                (f"{field_name}.{index}.{t[0]}", t[1]) for t in touples
                            ]
            elif info.type == RelInfo.RIField:
                value = pointed_getter(data, field_name, None)
                child_fk_data = self.from_model(info.model).get_all_fk_data(value)
                for model, touples in child_fk_data.items():
                    fk_data[model] += [(f"{field_name}.{t[0]}", t[1]) for t in touples]
        return fk_data

    def build_cache(self, data: Any) -> Any:
        if not settings.STRUCTURED_FIELD_CACHE_ENABLED:
            return data
        fk_data = self.get_all_fk_data(data)
        plainset = defaultdict(set)
        for model, touples in fk_data.items():
            for t in touples:
                if isinstance(t[1], Sequence):
                    plainset[model].update(t[1])
                else:
                    plainset[model].add(t[1])
        if settings.STRUCTURED_FIELD_SHARED_CACHE:
            cache = ThreadSafeCache()
        else:
            cache = Cache()
        for model, values in plainset.items():
            models = list(cache.get(model, {}).values())
            pks = []
            for value in values:
                if isinstance(value, model):
                    models.append(value)
                else:
                    pks.append(value)
            models_pks = [m.pk for m in models]
            pks = [pk for pk in pks if pk not in models_pks]
            if len(pks):
                models += list(model.objects.filter(pk__in=pks))
            cache[model].update({obj.pk: obj for obj in models})

        for model, touples in fk_data.items():
            for t in touples:
                pointed_setter(data, t[0], ValueWithCache(cache, model, t[1]))
        return data

    @classmethod
    def add_cache_engine_to_class(cls, mdlcls: Type[Any]) -> Type[Any]:
        cache_instance = cls.from_model(mdlcls)
        setattr(mdlcls, "_cache_engine", cache_instance)
        return mdlcls


def get_global_cache():
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        return ThreadSafeCache()
    return None
