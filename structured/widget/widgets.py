import json

from django.forms import Media
from django.forms.widgets import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils.translation import get_language
from structured.pydantic.models import BaseModel


def get_field_language(field_name: str) -> str:
    """
    Detect the language associated with a translated field, covering the main
    Django translation packages:
    - django-modeltranslation / django-translated-fields
    - django-parler
    - django-hvad / django-nece
    The suffix check is tried first; if nothing matches we fall back to the
    currently active Django language.
    """
    languages = [code.replace("-", "_") for code, _ in getattr(settings, "LANGUAGES", [])]
    for lang in sorted(languages, key=len, reverse=True):
        if field_name.endswith(f"_{lang}"):
            return lang
    return get_language() or ""


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
        self.errors = {}
        super().__init__(**kwargs)

    @property
    def media(self):
        css = []
        if self.extra_css:
            css.extend(self.extra_css)
        js = [
            "https://bnznamco.github.io/structured-widget-editor/latest/structured-widget-editor.iife.js",
            "js/structured-field-init.js",
        ]
        if self.extra_js:
            js.extend(self.extra_js)
        return Media(css={"all": css}, js=js)

    def get_editor_schema(self):
        return order_anyof_allof(self.schema.json_schema())

    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(self.attrs, attrs)
        context = {
            "data": value,
            "name": name,
            "schema": json.dumps(self.get_editor_schema()),
            "ui_schema": json.dumps(self.ui_schema) if self.ui_schema else "{}",
            "errors": json.dumps(self.errors),
            "widget_id": final_attrs.get("id", "id_%s" % name),
            "widget_class": final_attrs.get("class", ""),
            "language": get_field_language(name),
        }

        return mark_safe(render_to_string(self.template_name, context))
