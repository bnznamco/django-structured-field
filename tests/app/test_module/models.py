from typing import Optional
from django.db import models
from structured.fields import StructuredJSONField
from structured.pydantic.fields import ForeignKey
from structured.pydantic.models import BaseModel


class TestSchema(BaseModel):
    name: str
    age: int = None
    child: Optional["TestSchema"] = {}
    childs: list["TestSchema"] = []

    # model: "TestModel" = None


def init_schema():
    TestSchema(name="")


class TestModel(models.Model):
    title = models.CharField(max_length=255)
    structured_data = StructuredJSONField(schema=TestSchema, default=init_schema)

    def __str__(self) -> str:
        return self.title
