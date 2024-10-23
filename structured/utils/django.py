from django.apps import apps
from typing import Type
from django.db import models as django_models


def import_abs_model(app_label: str, model_name: str) -> Type[django_models.Model]:
    module = apps.get_app_config(app_label).models_module
    model_class = getattr(module, model_name, None)
    if model_class and issubclass(model_class, django_models.Model):
        return model_class
    return None
