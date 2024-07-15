import json

from django.forms import Media
from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from structured.pydantic.models import BaseModel


def sort_key(key, _schema):
    if key in _schema:
        val = _schema.pop(key)
        _schema[key] = sorted(val, key=lambda x: "null" != x.get("type", ""))


def order_anyof_allof(schema):
    """
    Order anyOf and allOf lists by the presence of null type
    This is needed to make sure that the null option is always the first one preventing loops in the editor
    """
    if isinstance(schema, dict):
        for key in ["anyOf", "allOf", "oneOf"]:
            sort_key(key, schema)
        for _, value in schema.items():
            order_anyof_allof(value)
    elif isinstance(schema, list):
        for item in schema:
            order_anyof_allof(item)
    return schema


class StructuredJSONFormWidget(Widget):
    template_name = "json-forms/widget.html"

    def __init__(
        self, schema: BaseModel, ui_schema=None, extra_css=None, extra_js=None, **kwargs
    ):
        self.schema: BaseModel = schema
        self.ui_schema = ui_schema
        self.extra_css = extra_css
        self.extra_js = extra_js
        super().__init__(**kwargs)

    @property
    def media(self):
        css = [
            "libs/select2/select2.style.css",
            "libs/fontawesome/css/all.min.css",
            "css/structured-field-form.min.css",
        ]
        if self.extra_css:
            css.extend(self.extra_css)
        js = [
            "https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js",
            "libs/select2/select2.min.js",
            "libs/jsoneditor/jsoneditor.js",
            "js/structured-field-form.js",
        ]
        if self.extra_js:
            js.extend(self.extra_js)
        return Media(css={"all": css}, js=js)

    def get_editor_schema(self):
        return order_anyof_allof(self.schema.json_schema())

    def render(self, name, value, attrs=None, renderer=None):
        context = {
            "data": value,
            "name": name,
            "schema": json.dumps(self.get_editor_schema()),
            "ui_schema": json.dumps(self.ui_schema) if self.ui_schema else "{}",
        }

        return mark_safe(render_to_string(self.template_name, context))
