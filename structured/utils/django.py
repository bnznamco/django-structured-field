from django.apps import apps
from typing import Any, Type, Optional
from django.db import models as django_models


def import_abs_model(app_label: str, model_name: str) -> Optional[Type[django_models.Model]]:
    """Import an absolute model by app label and model name."""
    module = apps.get_app_config(app_label).models_module
    model_class = getattr(module, model_name, None)
    if model_class and issubclass(model_class, django_models.Model):
        return model_class
    return None


def extract_pk(data: Any, model: Type[django_models.Model]) -> Any:
    """
    Extract a primary-key value from a relation reference: a model instance
    yields its pk; a dict is read by the model's real pk attname, falling
    back to the literal 'id' key — the wire format (json-mode dumps, the
    search API, the widget's emitted items) always uses 'id' regardless of
    the pk's actual name (None when neither key is present). Anything else
    (a bare pk) passes through.
    """
    if isinstance(data, django_models.Model):
        return data.pk
    if not isinstance(data, dict):
        return data
    # abstract models have no pk field (_meta.pk is None)
    pk_field = model._meta.pk
    attname = pk_field.attname if pk_field is not None else "id"
    if attname in data:
        return data[attname]
    return data.get("id")
