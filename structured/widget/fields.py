from structured.widget.widgets import StructuredJSONFormWidget
from django.forms import JSONField


class StructuredJSONFormField(JSONField):
    widget = StructuredJSONFormWidget
    
    def __init__(self, schema, ui_schema=None, *args, **kwargs):
        self.schema = schema
        self.ui_schema = ui_schema
        self.widget = StructuredJSONFormWidget(schema, ui_schema)
        super().__init__(*args, **kwargs)
