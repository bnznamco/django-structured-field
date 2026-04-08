"""Tests for structured.pydantic.conditionals helpers."""

from typing import Literal, Optional

import pytest
from pydantic import BaseModel, ConfigDict

from structured.pydantic.conditionals import (
    When,
    conditional_schema,
    dependent_required,
    dependent_schemas,
    merge_schema_extra,
)

# Showcase schema from the test application.
from tests.app.test_module.models import ArticleSchema


# ---------------------------------------------------------------------------
# When() clause shape
# ---------------------------------------------------------------------------

def test_when_builds_if_clause():
    clause = When("status", equals="archived", then={"required": ["archive_reason"]})
    assert clause["if"] == {
        "properties": {"status": {"const": "archived"}},
        "required": ["status"],
    }
    assert clause["then"] == {"required": ["archive_reason"]}
    assert clause["_controls"] == []


def test_when_stores_controls():
    clause = When("status", equals="archived", controls=["archive_reason"])
    assert clause["_controls"] == ["archive_reason"]


def test_when_supports_in_and_not_equals():
    clause = When("kind", in_=["a", "b"], then={"required": ["x"]})
    assert clause["if"]["properties"]["kind"] == {"enum": ["a", "b"]}

    clause = When("kind", not_equals="x", then={"required": ["y"]})
    assert clause["if"]["properties"]["kind"] == {"not": {"const": "x"}}


def test_when_requires_a_constraint():
    with pytest.raises(ValueError):
        When("status", then={"required": ["x"]})


# ---------------------------------------------------------------------------
# dependent_* helpers
# ---------------------------------------------------------------------------

def test_dependent_required_shape():
    assert dependent_required(publisher=["edition"]) == {
        "dependentRequired": {"publisher": ["edition"]}
    }


def test_dependent_schemas_shape():
    frag = dependent_schemas(publisher={"properties": {"edition": {"type": "string"}}})
    assert frag == {
        "dependentSchemas": {
            "publisher": {"properties": {"edition": {"type": "string"}}}
        }
    }


# ---------------------------------------------------------------------------
# merge_schema_extra
# ---------------------------------------------------------------------------

def test_merge_schema_extra_unions_allof_and_dependents():
    a = {"allOf": [{"if": 1}], "dependentRequired": {"x": ["a"]}}
    b = {"allOf": [{"if": 2}], "dependentRequired": {"y": ["b"]}}
    merged = merge_schema_extra(a, b)
    assert merged["allOf"] == [{"if": 1}, {"if": 2}]
    assert merged["dependentRequired"] == {"x": ["a"], "y": ["b"]}


# ---------------------------------------------------------------------------
# conditional_schema: callable applied to schema
# ---------------------------------------------------------------------------

def _make_book_schema():
    class Book(BaseModel):
        status: Literal["draft", "archived"] = "draft"
        archive_reason: Optional[str] = None

        model_config = ConfigDict(json_schema_extra=conditional_schema(
            When("status", equals="archived",
                 controls=["archive_reason"],
                 then={"required": ["archive_reason"]}),
        ))

    return Book.model_json_schema()


def test_controlled_field_removed_from_base_properties():
    schema = _make_book_schema()
    # archive_reason must NOT be in top-level properties — hidden until condition matches
    assert "archive_reason" not in schema.get("properties", {})


def test_controlled_field_placed_in_then_properties():
    schema = _make_book_schema()
    then = schema["allOf"][0]["then"]
    assert "archive_reason" in then["properties"]


def test_required_also_in_then():
    schema = _make_book_schema()
    then = schema["allOf"][0]["then"]
    assert "archive_reason" in then.get("required", [])


def test_non_controlled_when_leaves_base_properties_intact():
    """When() without controls= only toggles required; the field stays visible."""
    class Book(BaseModel):
        status: Literal["draft", "archived"] = "draft"
        archive_reason: Optional[str] = None

        model_config = ConfigDict(json_schema_extra=conditional_schema(
            When("status", equals="archived",
                 then={"required": ["archive_reason"]}),
        ))

    schema = Book.model_json_schema()
    # No controls → field stays in base properties (always rendered)
    assert "archive_reason" in schema["properties"]
    assert "archive_reason" not in schema["allOf"][0].get("then", {}).get("properties", {})


def test_dependent_schemas_with_controls():
    class Book(BaseModel):
        publisher: Optional[str] = None
        edition: Optional[str] = None

        model_config = ConfigDict(json_schema_extra=conditional_schema(
            dependent_schemas(publisher={"_controls": ["edition"]}),
        ))

    schema = Book.model_json_schema()
    assert "edition" not in schema.get("properties", {})
    assert "edition" in schema["dependentSchemas"]["publisher"]["properties"]


def test_conditional_schema_returns_callable():
    fn = conditional_schema(
        When("status", equals="archived", then={"required": ["archive_reason"]}),
    )
    assert callable(fn)


def test_pydantic_emits_allof_and_if_keywords():
    schema = _make_book_schema()
    assert "allOf" in schema
    assert schema["allOf"][0]["if"]["properties"]["status"]["const"] == "archived"


# ---------------------------------------------------------------------------
# Integration – ArticleSchema showcase (tests/app/test_module/models.py)
# ---------------------------------------------------------------------------

def test_article_schema_has_two_when_clauses():
    schema = ArticleSchema.model_json_schema()
    assert "allOf" in schema
    assert len(schema["allOf"]) == 2


def test_article_schema_dependent_required_for_publisher():
    schema = ArticleSchema.model_json_schema()
    assert schema.get("dependentRequired") == {"publisher": ["edition"]}


def test_article_schema_archived_clause_requires_archive_reason():
    schema = ArticleSchema.model_json_schema()
    clause = next(
        c for c in schema["allOf"]
        if c["if"]["properties"]["status"].get("const") == "archived"
    )
    assert "archive_reason" in clause["then"].get("required", [])


def test_article_schema_published_clause_requires_published_at():
    schema = ArticleSchema.model_json_schema()
    clause = next(
        c for c in schema["allOf"]
        if c["if"]["properties"]["status"].get("const") == "published"
    )
    assert "published_at" in clause["then"].get("required", [])


def test_article_schema_controlled_fields_not_in_top_level_properties():
    schema = ArticleSchema.model_json_schema()
    top_props = set(schema.get("properties", {}).keys())
    assert "archive_reason" not in top_props
    assert "published_at" not in top_props


def test_article_schema_controlled_fields_in_then_branches():
    schema = ArticleSchema.model_json_schema()
    for clause in schema["allOf"]:
        const = clause["if"]["properties"]["status"].get("const")
        if const == "archived":
            assert "archive_reason" in clause["then"]["properties"]
        elif const == "published":
            assert "published_at" in clause["then"]["properties"]


def test_article_schema_default_instance():
    article = ArticleSchema()
    assert article.status == "draft"
    assert article.archive_reason is None
    assert article.published_at is None
