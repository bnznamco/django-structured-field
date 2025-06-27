from typing import Any, Callable, Dict, Generic, TypeVar, Union, List, Type

from django.db import models as django_models
from pydantic import GetJsonSchemaHandler, SerializationInfo
from pydantic_core import core_schema as cs
from pydantic.json_schema import JsonSchemaValue
from structured.utils.options import build_relation_schema_options
from structured.utils.serializer import (
    build_standard_model_serializer,
    minimal_list_serialization,
)
from structured.utils.typing import get_type


T = TypeVar("T", bound=django_models.Model)


class QuerySet(Generic[T]):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: Callable[[Any], cs.CoreSchema]
    ) -> cs.CoreSchema:
        from structured.cache.engine import ValueWithCache

        def get_mclass() -> Type[django_models.Model]:
            return get_type(source)

        is_abstract = getattr(get_mclass()._meta, "abstract", False)
        if is_abstract:
            raise ValueError(
                "Abstract models cannot be used as QuerySet fields directly."
            )

        def validate_from_pk_list(
            values: List[Union[int, str]]
        ) -> django_models.QuerySet:
            preserved = django_models.Case(
                *[django_models.When(pk=pk, then=pos) for pos, pk in enumerate(values)]
            )
            return (
                get_mclass()._default_manager.filter(pk__in=values).order_by(preserved)
            )

        int_str_union = cs.union_schema([cs.str_schema(), cs.int_schema()])
        from_pk_list_schema = cs.chain_schema(
            [
                cs.list_schema(int_str_union),
                cs.no_info_plain_validator_function(validate_from_pk_list),
            ]
        )
        pk_attname = get_mclass()._meta.pk.attname

        def validate_from_dict(
            values: List[Dict[str, Union[str, int]]]
        ) -> django_models.QuerySet:
            pk_attname = get_mclass()._meta.pk.attname
            return validate_from_pk_list([data[pk_attname] for data in values])

        optional_field = cs.typed_dict_field(cs.str_schema(), required=False)
        from_dict_list_schema = cs.chain_schema(
            [
                cs.list_schema(
                    cs.typed_dict_schema(
                        {
                            pk_attname: cs.typed_dict_field(int_str_union),
                            "model": optional_field,
                            "name": optional_field,
                        }
                    )
                ),
                cs.no_info_plain_validator_function(validate_from_dict),
            ]
        )
        from_cache_schema = cs.chain_schema(
            [
                cs.is_instance_schema(ValueWithCache),
                cs.no_info_plain_validator_function(lambda v: v.retrieve()),
            ]
        )

        def validate_from_model_list(
            values: List[django_models.Model],
        ) -> django_models.QuerySet:
            if any(not isinstance(v, get_mclass()) for v in values):
                raise ValueError(f"Expected list of {get_mclass()} instances.")
            return get_mclass()._default_manager.filter(pk__in=[v.pk for v in values])

        from_model_list_schema = cs.chain_schema(
            [
                cs.list_schema(cs.is_instance_schema(get_mclass())),
                cs.no_info_plain_validator_function(validate_from_model_list),
            ]
        )

        def serialize_data(qs: django_models.QuerySet, info: SerializationInfo) -> List[Dict[str, Any]]:
            if info.mode == "python":
                serializer = build_standard_model_serializer(get_mclass(), depth=1)
                return serializer(instance=qs, many=True, context=info.context or {}).data
            return minimal_list_serialization(qs)

        return cs.json_or_python_schema(
            json_schema=cs.union_schema(
                [
                    from_cache_schema,
                    from_pk_list_schema,
                    from_dict_list_schema,
                    from_model_list_schema,
                ]
            ),
            python_schema=cs.union_schema(
                [
                    cs.is_instance_schema(django_models.QuerySet),
                    from_cache_schema,
                    from_pk_list_schema,
                    from_dict_list_schema,
                    from_model_list_schema,
                ]
            ),
            serialization=cs.plain_serializer_function_ser_schema(
                serialize_data, info_arg=True
            ),
            metadata={
                "relation": build_relation_schema_options(get_mclass(), many=True)
            },
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(cs.str_schema())
        json_schema.update(_core_schema.get("metadata", {}).get("relation", {}))
        return json_schema
