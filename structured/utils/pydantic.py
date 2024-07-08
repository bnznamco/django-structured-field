from django.db import models
from typing import Type


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


def build_relation_schema_options(model: Type[models.Model], many: bool = False, nullable: bool = True):
    return {
        "format": "select2",
        "model": f"{model._meta.app_label}.{model.__name__}",
        "type": "relation",
        "multiple": many,
        "options": {
            "select2": {
                "placeholder": "Select an option",
                "multiple": many,
                "allowClear": nullable,
                "ajax": {
                    "url": f"/structured_field/search_model/{model._meta.app_label}.{model.__name__}/",
                    "dataType": "json",
                    "data": "createQueryParams",
                    "processResults": "processResultData",
                }
            },
        },
    }
