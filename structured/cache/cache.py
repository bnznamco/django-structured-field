from collections import defaultdict
from typing import Type, Union, Iterable, Dict, Any, TYPE_CHECKING
from django.db.models import Model as DjangoModel
from django.db.models.query import QuerySet as DjangoQuerySet
from django.db.models.signals import post_save, pre_delete
from pydantic import model_validator
import threading
from structured.settings import settings

if TYPE_CHECKING:  # pragma: no cover
    from structured.pydantic.models import BaseModel
    from structured.cache.engine import CacheEngine


class CacheEnabledModel:
    """
    A model class that enables caching.
    """

    _cache_engine: 'CacheEngine'

    @model_validator(mode="wrap")
    @classmethod
    def build_cache(cls, data: Dict[str, Any], handler: Any) -> Any:
        """
        Build and fetch cache for the given data.
        """
        data = cls._cache_engine.build_cache(data)
        instance: "BaseModel" = handler(data)
        return cls._cache_engine.fetch_cache(instance)


def get_global_cache():
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        return ThreadSafeCache()
    return None


class Cache(defaultdict):
    """
    The cache class that stores the cache data.
    Per-request caches do NOT connect to Django signals — they are short-lived
    and discarded after validation. Only ThreadSafeCache (shared mode) connects
    signals for cross-request cache invalidation.
    The cache data is stored in the following format:
    {
        Model1: {
            pk1: instance1,
            pk2: instance2,
            ...
        },
        Model2: {
            pk1: instance1,
            pk2: instance2,
            ...
        },
    """

    def __init__(self) -> None:
        super().__init__(dict)

    def flush(
        self, data: Union[DjangoModel, Iterable[DjangoModel], None] = None, **kwargs
    ) -> None:
        """
        Flush the cache for the given data or model.
        """
        model = kwargs.get("model", None)
        if model:
            self._flush_model(model)
        if data:
            self._flush_data(data)
        else:
            self.clear()

    def _flush_model(self, model: Union[str, Type[DjangoModel]]) -> None:
        """
        Flush the cache for the given model.
        """
        if isinstance(model, str):
            model = next((m for m in self.keys() if m.__name__ == model), None)
        if model and model in self:
            del self[model]

    def _flush_data(self, data: Union[DjangoModel, Iterable[DjangoModel]]) -> None:
        """
        Flush the cache for the given data.
        """
        if isinstance(data, DjangoModel):
            model = data.__class__
            if model in self and data.pk in self[model]:
                del self[model][data.pk]
        else:
            for instance in data:
                model = instance.__class__
                if model in self and instance.pk in self[model]:
                    del self[model][instance.pk]

    def set(self, data: Union[DjangoModel, Iterable[DjangoModel]]) -> None:
        """
        Set the cache for the given data.
        """
        if isinstance(data, DjangoModel):
            self[data.__class__].update({data.pk: data})
        else:
            for instance in data:
                self[instance.__class__].update({instance.pk: instance})


class ThreadSafeCache(Cache):
    """
    A singleton cache object that allows sharing cache data between fields and instances.
    This encapsulates the cache data inside a thread-safe singleton object.
    Every model instance invoking a cache operation will use the same cache object,
    allowing the cache data to be shared between them.
    All mutation methods are protected by a threading lock for thread safety.
    Connects to Django signals for cross-request cache invalidation.
    """

    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
            post_save.connect(self._on_instance_save)
            pre_delete.connect(self._on_instance_delete)

    @staticmethod
    def _on_instance_save(
        sender: Type[DjangoModel], instance: DjangoModel, **kwargs
    ) -> None:
        """
        Signal handler for saving a model instance.
        """
        cache = get_global_cache()
        if cache and instance.__class__ in cache:
            cache.set(instance)

    @staticmethod
    def _on_instance_delete(
        sender: Type[DjangoModel], instance: DjangoModel, **kwargs
    ) -> None:
        """
        Signal handler for deleting a model instance.
        """
        cache = get_global_cache()
        if cache and instance.__class__ in cache:
            cache.flush(instance)

    def set(self, data: Union[DjangoModel, Iterable[DjangoModel]]) -> None:
        with self._lock:
            super().set(data)

    def flush(
        self, data: Union[DjangoModel, Iterable[DjangoModel], None] = None, **kwargs
    ) -> None:
        with self._lock:
            super().flush(data, **kwargs)

    def __setitem__(self, key, value):
        with self._lock:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        with self._lock:
            super().__delitem__(key)

    def clear(self):
        with self._lock:
            super().clear()


class ValueWithCache:
    """
    A class that represents a cached value.
    This is used to retrieve values from the cache during the serialization process.
    The retrieve method fetches the needed values and returns accordingly to the field type (ForeignKey, QuerySet, etc.).
    """

    def __init__(
        self,
        cache: Cache,
        model: Type[DjangoModel],
        value: Union[Iterable[Union[str, int]], str, int],
    ) -> None:
        self.cache: Cache = cache
        self.value: Union[Iterable[Union[str, int]], str, int] = value
        self.model: Type[DjangoModel] = model

    def retrieve(self) -> Union[DjangoModel, DjangoQuerySet]:
        """
        Retrieve the value from the cache or database.
        """
        cache = self.cache.get(self.model)
        if hasattr(self.value, "__iter__") and not isinstance(self.value, str):
            pks = list(self.value)
            if cache:
                cached = [cache[i] for i in pks if i in cache]
                missing_pks = [i for i in pks if i not in cache]
                if missing_pks:
                    fetched = list(self.model.objects.filter(pk__in=missing_pks))
                    cached.extend(fetched)
                    # Update cache with newly fetched instances
                    for obj in fetched:
                        cache[obj.pk] = obj
                result = cached
            else:
                result = list(self.model.objects.filter(pk__in=pks))
            # Preserve original PK ordering
            pk_to_obj = {obj.pk: obj for obj in result}
            ordered = [pk_to_obj[pk] for pk in pks if pk in pk_to_obj]
            qs = self.model.objects.filter(pk__in=pks)
            setattr(qs, "_result_cache", ordered)
            return qs
        else:
            if cache:
                val = cache.get(self.value, None)
            else:
                val = None
            if val is None:
                return self.model._default_manager.filter(pk=self.value).first()
            else:
                return val
