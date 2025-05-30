from typing import Any, Union
from structured.pydantic.models import BaseModel
from structured.widget.widgets import StructuredJSONFormWidget
from pydantic import ValidationError as PydanticValidationError
from django.forms import JSONField, ValidationError
from django.utils.translation import gettext_lazy as _
import json
import traceback
import logging

logger = logging.getLogger(__name__)


class StructuredJSONFormField(JSONField):
    widget = StructuredJSONFormWidget
    default_error_messages = {
        "invalid": _("Check errors below."),
        "invalid_schema": _(
            "The provided data does not match the expected schema. Please check the errors below."
        ),
    }

    def __init__(self, schema, ui_schema=None, *args, **kwargs):
        self.schema = schema
        self.ui_schema = ui_schema
        self.widget = StructuredJSONFormWidget(schema, ui_schema)
        super().__init__(*args, **kwargs)

    def validate_schema(self, value):
        try:
            return value and self.schema.validate_python(value.copy())
        except PydanticValidationError:
            traceback.print_exc()
            logger.error(
                "Validation error in StructuredJSONFormField",
                extra={
                    "value": value,
                    "schema": self.schema,
                    "ui_schema": self.ui_schema,
                },
            )
            raise ValidationError(self.error_messages["invalid_schema"], code="invalid_schema")

    def to_python(self, value: Any) -> Any:
        value = super().to_python(value)
        self.validate_schema(value)
        return value

    def prepare_value(self, value: Union[BaseModel, dict]) -> str:
        if isinstance(value, BaseModel):
            value = value.model_dump(mode="json")
        if isinstance(value, list):
            value = [v.model_dump(mode="json") if isinstance(v, BaseModel) else v for v in value]
        return json.dumps(value)
