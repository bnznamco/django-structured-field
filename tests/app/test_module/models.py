from typing import Optional
from django.db import models
from structured.fields import StructuredJSONField
from structured.pydantic.fields import ForeignKey
from structured.pydantic.models import BaseModel


class TestSchema(BaseModel):
    name: str
    age: int = None
    child: Optional["TestSchema"] = {}
    # model: "TestModel" = None


class TestModel(models.Model):
    structured_data = StructuredJSONField(schema=TestSchema, default=dict)
