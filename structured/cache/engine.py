from __future__ import annotations
from collections import defaultdict
from inspect import isclass
from typing import Any, Dict, List, Tuple, Set, Sequence, Type, TYPE_CHECKING, Union, get_origin, get_args
from django.db.models import Model as DjangoModel
from django.apps import apps
from structured.settings import settings
from structured.utils.typing import get_type, find_model_type_from_args
from structured.utils.getter import pointed_getter
from structured.utils.setter import pointed_setter
from structured.pydantic.fields import ForeignKey, QuerySet
from .cache import Cache, ThreadSafeCache, ValueWithCache, CacheEnabledModel
from .rel_info import RelInfo

if TYPE_CHECKING:  # pragma: no cover
    from structured.pydantic.models import BaseModel


class CacheEngine:
    """
    The cache engine class that handles all the caching operations in a certain model.
    Each model has its own cache engine instance that is responsible for building and fetching the cache data.
    The cache engine is responsible for building and fetching the cache data for the given model.
    During the build process, the cache engine analyzes the model fields and builds the cache data accordingly.
    The cache data is then stored in the cache object.
    The fetch process retrieves the cache data from the cache object and returns the cached values.
    Pydantic serialization does the rest of the job by unpacking the cached values.
    """

    def __init__(self, related_fields: Dict[str, RelInfo]) -> None:
        self.__related_fields__ = related_fields

    @staticmethod
    def fetch_cache(instance: BaseModel) -> BaseModel:
        """
        Fetch values from the cache for the given instance.
        """
        for field_name in instance.model_fields_set:
            val = getattr(instance, field_name, None)
            if isinstance(val, ValueWithCache):
                setattr(instance, field_name, val.retrieve())
            elif isinstance(val, CacheEnabledModel):
                setattr(instance, field_name, CacheEngine.fetch_cache(val))
        return instance

    @classmethod
    def from_model(cls, model: BaseModel) -> "CacheEngine":
        """
        Creates a CacheEngine instance from the given model.
        """
        return cls(related_fields=cls.inspect_related_fields(model))

    @classmethod
    def inspect_related_fields(cls, model: Type[BaseModel]) -> Dict[str, RelInfo]:
        """
        Analyzes the model fields and returns only the related fields with a Relation Info obj in the following format:
        {
            field1: RelInfo(model, type, field),
            field2: RelInfo(model, type, field),
        }
        """
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

    def get_all_fk_data(self, data: Any) -> Dict[Type[DjangoModel], List[Tuple[str, Any]]]:
        """
        Get all foreign key data from the given data.
        """
        if isinstance(data, Sequence):
            fk_data = defaultdict(list)
            for index in range(len(data)):
                child_fk_data = self.get_all_fk_data(data[index])
                for model, tuples in child_fk_data.items():
                    fk_data[model] += [(f"{index}.{t[0]}", t[1]) for t in tuples]
            return fk_data
        return self.get_fk_data(data)

    def get_fk_data(self, data: Any) -> Dict[Type[DjangoModel], List[Tuple[str, Any]]]:
        """
        Get foreign key data from the given data.
        """
        fk_data = defaultdict(list)
        if not data:
            return fk_data
        for field_name, info in self.__related_fields__.items():
            if info.type == RelInfo.FKField:
                self._process_fk_field(data, field_name, info, fk_data)
            elif info.type == RelInfo.QSField:
                self._process_qs_field(data, field_name, info, fk_data)
            elif info.type == RelInfo.RLField:
                self._process_rl_field(data, field_name, info, fk_data)
            elif info.type == RelInfo.RIField:
                self._process_ri_field(data, field_name, info, fk_data)
        return fk_data

    def _process_fk_field(self, data: Any, field_name: str, info: RelInfo, fk_data: Dict[Type[DjangoModel], List[Tuple[str, Any]]]) -> None:
        """
        Process a foreign key field.
        """
        value = pointed_getter(data, field_name, None)
        if info.model._meta.abstract:
            info.model = self._resolve_abstract_model(value, info.model)
        if isinstance(value, DjangoModel):
            info.model = value.__class__
            value = value.pk
        if isinstance(value, dict):
            info.model = apps.get_model(*value["model"].split("."))
            value = value.get(info.model._meta.pk.attname, None)
        if value:
            if isinstance(value, ValueWithCache):
                fk_data = {}
                return
            attname = (
                info.model._meta.pk.attname if not info.model._meta.abstract else ""
            )
            fk_data[info.model].append(
                (field_name, pointed_getter(value, attname, value))
            )

    def _resolve_abstract_model(self, value: Any, model: Type[DjangoModel]) -> Type[DjangoModel]:
        """
        Resolve the abstract model from the given value.
        """
        if isinstance(value, dict) and "model" in value:
            return apps.get_model(*value["model"].split("."))
        if isinstance(value, DjangoModel) and not value._meta.abstract:
            return value.__class__
        if isinstance(value, (int, str)) and model._meta.abstract:
            raise ValueError("Cannot retrieve abstract models from primary key only.")
        return model

    def _process_qs_field(self, data: Any, field_name: str, info: RelInfo, fk_data: Dict[Type[DjangoModel], List[Tuple[str, Any]]]) -> None:
        """
        Process a queryset field.
        """
        value = pointed_getter(data, field_name, [])
        if isinstance(value, list):
            if any(isinstance(v, ValueWithCache) for v in value):
                fk_data = {}
                return
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

    def _process_rl_field(self, data: Any, field_name: str, info: RelInfo, fk_data: Dict[Type[DjangoModel], List[Tuple[str, Any]]]) -> None:
        """
        Process a related list field.
        """
        values = pointed_getter(data, field_name, [])
        if isinstance(values, list):
            for index in range(len(values)):
                for model, tuples in (
                    self.from_model(info.model).get_all_fk_data(values[index]).items()
                ):
                    fk_data[model] += [
                        (f"{field_name}.{index}.{t[0]}", t[1]) for t in tuples
                    ]

    def _process_ri_field(self, data: Any, field_name: str, info: RelInfo, fk_data: Dict[Type[DjangoModel], List[Tuple[str, Any]]]) -> None:
        """
        Process a related instance field.
        """
        value = pointed_getter(data, field_name, None)
        child_fk_data = self.from_model(info.model).get_all_fk_data(value)
        for model, tuples in child_fk_data.items():
            fk_data[model] += [(f"{field_name}.{t[0]}", t[1]) for t in tuples]

    def build_cache(self, data: Any) -> Any:
        """
        Build the cache for the given data.
        """
        if not settings.STRUCTURED_FIELD_CACHE_ENABLED:
            return data
        fk_data = self.get_all_fk_data(data)
        plainset = self._build_plainset(fk_data)
        cache = ThreadSafeCache() if settings.STRUCTURED_FIELD_SHARED_CACHE else Cache()
        self._populate_cache(cache, plainset)
        self._set_cache_values(data, fk_data, cache)
        return data

    def _build_plainset(self, fk_data: Dict[Type[DjangoModel], List[Tuple[str, Any]]]) -> Dict[Type[DjangoModel], Set[Any]]:
        """
        Build a plain set of foreign key data.
        """
        plainset = defaultdict(set)
        for model, tuples in fk_data.items():
            for t in tuples:
                if isinstance(t[1], Sequence):
                    plainset[model].update(t[1])
                else:
                    plainset[model].add(t[1])
        return plainset

    def _populate_cache(self, cache: Cache, plainset: Dict[Type[DjangoModel], Set[Any]]) -> None:
        """
        Populate the cache with the given plain set.
        """
        for model, values in plainset.items():
            models = list(cache.get(model, {}).values())
            pks = [value for value in values if not isinstance(value, model)]
            models_pks = [m.pk for m in models]
            pks = [pk for pk in pks if pk not in models_pks]
            if pks:
                models += list(model.objects.filter(pk__in=pks))
            cache[model].update({obj.pk: obj for obj in models})

    def _set_cache_values(self, data: Any, fk_data: Dict[Type[DjangoModel], List[Tuple[str, Any]]], cache: Cache) -> None:
        """
        Set the cache values in the given data.
        """
        for model, tuples in fk_data.items():
            for t in tuples:
                pointed_setter(data, t[0], ValueWithCache(cache, model, t[1]))

    @classmethod
    def add_cache_engine_to_class(cls, mdlcls: Type[Any]) -> Type[Any]:
        """
        Add a cache engine to the given model class.
        """
        cache_instance = cls.from_model(mdlcls)
        setattr(mdlcls, "_cache_engine", cache_instance)
        return mdlcls
