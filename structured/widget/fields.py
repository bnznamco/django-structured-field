from typing import Any, Union
from structured.pydantic.models import BaseModel
from structured.widget.widgets import StructuredJSONFormWidget
from django.forms import JSONField, ValidationError
from pydantic import ValidationError as PydanticValidationError
from django.utils.translation import gettext_lazy as _


class StructuredJSONFormField(JSONField):
    widget = StructuredJSONFormWidget
    default_error_messages = {
        "invalid": _("Check errors below."),
    }

    def __init__(self, schema, ui_schema=None, *args, **kwargs):
        self.schema = schema
        self.ui_schema = ui_schema
        self.widget = StructuredJSONFormWidget(schema, ui_schema)
        super().__init__(*args, **kwargs)

    def validate_schema(self, value):
        try:
            return self.schema.validate_python(value)
        except PydanticValidationError:
            raise ValidationError(self.error_messages["invalid"], code="invalid")

    def to_python(self, value: Any) -> Any:
        value = super().to_python(value)
        self.validate_schema(value)
        return value

    def prepare_value(self, value: Union[BaseModel, dict]) -> Any:
        if isinstance(value, BaseModel):
            value = value.model_dump()
        return super().prepare_value(value)
