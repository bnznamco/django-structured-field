from typing import Type, Dict, Any
from django.db import models


def build_relation_schema_options(
    model: Type[models.Model], many: bool = False, nullable: bool = True
) -> Dict[str, Any]:
    """Build schema options for a relation field."""
    return {
        "format": "select2",
        "model": f"{model._meta.app_label}.{model.__name__}",
        "type": "relation",
        "multiple": many,
        "options": {
            "select2": {
                "placeholder": (
                    "Start writing to search for options"
                    if many
                    else "Select an option"
                ),
                "multiple": many,
                "allowClear": nullable,
                "ajax": {
                    "url": f"/structured_field/search_model/{model._meta.app_label}.{model.__name__}/",
                    "dataType": "json",
                    "data": "createQueryParams",
                    "processResults": "processResultData",
                },
            },
        },
    }
