import json

from django.forms import Media
from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class StructuredJSONFormWidget(Widget):
    template_name = "json-forms/widget.html"

    def __init__(self, schema, ui_schema=None, extra_css=None, extra_js=None, **kwargs):
        self.schema = schema
        self.ui_schema = ui_schema
        self.extra_css = extra_css
        self.extra_js = extra_js
        super().__init__(**kwargs)

    @property
    def media(self):
        css = [
            "css/structured-field-form.min.css",
            "libs/fontawesome/css/all.min.css",
        ]
        if self.extra_css:
            css.extend(self.extra_css)
        js = [
            "libs/jsoneditor/jsoneditor.js",
            "js/structured-field-form.js",
        ]
        if self.extra_js:
            js.extend(self.extra_js)
        return Media(css={"all": css}, js=js)

    @classmethod
    def order_anyof_allof(cls, schema):
        """
        Order anyOf and allOf lists by the presence of null type
        This is needed to make sure that the null option is always the first one preventing loops in the editor
        """

        def sort_key(key, _schema):
            if key in _schema:
                val = _schema.pop(key)
                _schema[key] = sorted(val, key=lambda x: "null" != x.get("type", ""))

        if isinstance(schema, dict):
            for key in ["anyOf", "allOf", "oneOf"]:
                sort_key(key, schema)
            for _, value in schema.items():
                cls.order_anyof_allof(value)
        elif isinstance(schema, list):
            for item in schema:
                cls.order_anyof_allof(item)
        return schema

    def render(self, name, value, attrs=None, renderer=None):
        context = {
            "data": value,
            "name": name,
            "schema": json.dumps(self.order_anyof_allof(self.schema.copy())),
            "ui_schema": json.dumps(self.ui_schema) if self.ui_schema else "{}",
        }

        return mark_safe(render_to_string(self.template_name, context))
