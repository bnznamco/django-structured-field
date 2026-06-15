from typing_extensions import Annotated
from typing import Optional, List, Union, Literal
from django.db import models
from structured.fields import StructuredJSONField
from structured.pydantic.fields import ForeignKey, QuerySet
from structured.pydantic.models import BaseModel
from structured.pydantic.fields.serializer import FieldSerializer
from structured.pydantic.conditionals import When, conditional_schema, dependent_required
from rest_framework import serializers
from pydantic import ConfigDict, Field

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


class SearchDisplayModel(models.Model):
    """Relation target that contributes presentation-only fields (e.g. a
    thumbnail URL) to the relation search dropdown via the generic
    ``get_structured_search_display`` hook. The extra data appears ONLY in
    search results — never in the persisted relation wire format."""

    name = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=500, blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def get_structured_search_display(self) -> dict:
        return {"image": self.thumbnail, "description": f"Item {self.pk}"}


class CustomManagerModel(models.Model):
    """Relation target whose ONLY manager is custom-named: Django does not
    auto-create `objects`, so cache-layer code must use _default_manager."""

    name = models.CharField(max_length=255)
    items = models.Manager()

    def __str__(self) -> str:
        return self.name


class CustomPKModel(models.Model):
    """Relation target with a custom-NAMED primary key: the persisted wire
    format keys relations by the literal 'id', so readers must accept both
    'code' (the attname) and 'id'."""

    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)

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


# ---------------------------------------------------------------------------
# Conditional-logic showcase
# ---------------------------------------------------------------------------

class ArticleSchema(BaseModel):
    """Schema that demonstrates conditional / dependent field rules.

    Rules:
    * status == "archived"  → archive_reason becomes required
    * status == "published" → published_at becomes required
    * publisher present     → edition becomes required (dependentRequired)
    """

    status: Literal["draft", "review", "published", "archived"] = "draft"
    archive_reason: Optional[str] = None
    published_at: Optional[str] = None
    publisher: Optional[str] = None
    edition: Optional[str] = None

    model_config = ConfigDict(json_schema_extra=conditional_schema(
        When("status", equals="archived",
             controls=["archive_reason"],
             then={"required": ["archive_reason"]}),
        When("status", equals="published",
             controls=["published_at"],
             then={"required": ["published_at"]}),
        dependent_required(publisher=["edition"]),
        
    ))


def init_article_schema():
    return ArticleSchema()


class ArticleModel(models.Model):
    title = models.CharField(max_length=255)
    structured_data = StructuredJSONField(schema=ArticleSchema, default=init_article_schema)

    def __str__(self) -> str:
        return self.title


# ---------------------------------------------------------------------------
# Structured prefetch_related showcase
# ---------------------------------------------------------------------------
#
# These models exercise StructuredManager: an outer model whose
# StructuredJSONField references an Author, and Author itself has a FK to
# Country and a M2M to Tag. The tests verify that
# ``prefetch_related("structured_data__author__country")`` results in a
# single inner query per relation hop, regardless of how many outer rows
# (or how many distinct authors per row) are involved.

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL, related_name="authors")
    tags = models.ManyToManyField(Tag, blank=True, related_name="authors")

    def __str__(self) -> str:
        return self.name


class BookSchema(BaseModel):
    title: str
    author: Optional[ForeignKey[Author]] = None
    co_authors: QuerySet[Author]


def init_book_schema():
    return BookSchema(title="")


class BookModel(models.Model):
    """
    No explicit ``objects = StructuredManager()`` — relies on the
    auto-install pathway driven by ``class_prepared``.
    """

    title = models.CharField(max_length=255)
    structured_data = StructuredJSONField(schema=BookSchema, default=init_book_schema)

    def __str__(self) -> str:
        return self.title
