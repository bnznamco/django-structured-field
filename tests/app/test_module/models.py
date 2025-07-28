from typing_extensions import Annotated
from typing import Optional, List, Union, Literal
from django.db import models
from structured.fields import StructuredJSONField
from structured.pydantic.fields import ForeignKey, QuerySet
from structured.pydantic.models import BaseModel
from structured.pydantic.fields.serializer import FieldSerializer
from rest_framework import serializers
from pydantic import Field

class CustomSimpleRelationModelSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "custom": "👻 I'm custom!"
        }


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
    file = models.FileField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class TestSchema(BaseModel):
    type: Literal["schema1"] = "schema1"
    name: str
    age: int = 0
    child: Optional["TestSchema"] = None
    childs: List["TestSchema"] = []
    fk_field: SimpleRelationModel = None
    qs_field: QuerySet[SimpleRelationModel]
    abstract_fk: ForeignKey[AbstractModel] = None
    custom_serializer_fk: Annotated[SimpleRelationModel, FieldSerializer(CustomSimpleRelationModelSerializer)] = None
    custom_serializer_qs: Annotated[QuerySet[SimpleRelationModel], FieldSerializer(CustomSimpleRelationModelSerializer, many=True)]


def init_schema():
    return TestSchema(name="", type="schema1")


class TestSchema2(BaseModel):
    type: Literal["schema2"] = "schema2"
    name_2: str
    age_2: int = 0
    child_2: Optional["TestSchema"] = None
    childs_2: List["TestSchema"] = Field(default_factory=list)
    fk_field_2: SimpleRelationModel = None
    qs_field_2: QuerySet[SimpleRelationModel]
    abstract_fk_2: ForeignKey[AbstractModel] = None


class UnionSchema(BaseModel):
    data: Union[TestSchema, TestSchema2] = Field(discriminator='type')


class RecursiveOnModelSchema(BaseModel):
    child_model: "ForeignKey[TestModel]" = None

def init_union_schema():
    return {"data": {"name": "", "type": "schema1"}}


class TestModel(models.Model):
    title = models.CharField(max_length=255)
    structured_data = StructuredJSONField(schema=TestSchema, default=init_schema)
    structured_data_list = StructuredJSONField(schema=TestSchema, default=list)
    structured_data_union = StructuredJSONField(schema=UnionSchema, default=init_union_schema)
    structured_data_recursive = StructuredJSONField(schema=RecursiveOnModelSchema, default=dict)
    
    def __str__(self) -> str:
        return self.title
