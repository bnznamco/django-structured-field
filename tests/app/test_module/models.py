from __future__ import annotations
from typing import Optional, List
from django.db import models
from structured.fields import StructuredJSONField
from structured.pydantic.fields import ForeignKey, QuerySet
from structured.pydantic.models import BaseModel


class AbstractModel(models.Model):
    common_field = models.CharField(max_length=255)

    class Meta:
        abstract = True


class ChildModel1(AbstractModel):
    child_field = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.pk}) - {self.common_field}"


class ChildModel2(AbstractModel):
    child_field = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.pk}) - {self.common_field}"


class SimpleRelationModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class TestSchema(BaseModel):
    name: str
    age: int = None
    child: Optional["TestSchema"] = None
    childs: List["TestSchema"] = []
    fk_field: SimpleRelationModel = None
    qs_field: QuerySet[SimpleRelationModel]
    abstract_fk: ForeignKey[AbstractModel] = None


def init_schema():
    return TestSchema(name="")


class TestModel(models.Model):
    title = models.CharField(max_length=255)
    structured_data = StructuredJSONField(schema=TestSchema, default=init_schema)

    def __str__(self) -> str:
        return self.title
