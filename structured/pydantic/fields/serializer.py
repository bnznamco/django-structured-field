from rest_framework import serializers
from typing import Callable, Union, Dict, Any
from structured.utils.serializer import minimal_serialization, minimal_list_serialization
from structured.cache.engine import ValueWithCache
from django.db import models as django_models
from pydantic import SerializationInfo
from pydantic_core import core_schema as cs


class FieldSerializer:
    def __init__(self, SerializerClass: serializers.Serializer, many: bool = False):
        self.serializer_class = SerializerClass
        self.many = many
        if not issubclass(self.serializer_class, serializers.Serializer):
            raise TypeError(
                "'%s' must be a subclass of rest_framework.serializers.Serializer" % self.serializer_class.__name__
            )

        def serialize_data(
            instance: Union[ValueWithCache, django_models.Model, None],
            info: SerializationInfo,
        ) -> Union[Dict[str, Any], None]:
            if isinstance(instance, ValueWithCache):
                instance = instance.retrieve()
            if info.mode == "python":
                return self.serializer_class(instance=instance, many=self.many, context=info.context or {}).data
            if self.many:
                return minimal_list_serialization(instance)
            return minimal_serialization(instance)

        self.serializer_function = serialize_data

    def __get_pydantic_core_schema__(
        self, source: Any, handler: Callable[[Any], cs.CoreSchema]
    ) -> cs.CoreSchema:
        schema = handler(source)
        schema["serialization"] = cs.plain_serializer_function_ser_schema(
            self.serializer_function, info_arg=True
        )
        return schema
