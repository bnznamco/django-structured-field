# 🔀 Conditional Logic

Django Structured JSON Field ships with a set of helpers for declaring
**conditional and dependent field rules** directly on your Pydantic schema.
The rules compile down to standard JSON Schema keywords (`if`/`then`/`else`,
`allOf`, `dependentSchemas`, `dependentRequired`) so that:

- The **frontend widget editor** hides or shows fields dynamically as the user
  fills in the form.
- Any JSON Schema consumer can read the constraints without custom extensions.

> **Note** – Pydantic v2 does not enforce `if`/`then`/`else` or
> `dependentRequired` at Python validation time; those keywords are schema-only
> annotations consumed by the editor. Standard Pydantic field validation
> (types, `Field(...)` constraints, `@model_validator`) still applies as usual.

---

## 📦 Import

```python
from structured.pydantic.conditionals import (
    When,
    conditional_schema,
    dependent_required,
    dependent_schemas,
)
from pydantic import ConfigDict
```

---

## 🧩 `When` – value-driven visibility and required rules

Use `When` to show a field (or make it required) only when a controlling field
holds a specific value.

```python
from typing import Literal, Optional
from structured.pydantic.models import BaseModel
from structured.pydantic.conditionals import When, conditional_schema
from pydantic import ConfigDict

class ArticleSchema(BaseModel):
    status: Literal["draft", "review", "published", "archived"] = "draft"
    archive_reason: Optional[str] = None   # only relevant when archived
    published_at: Optional[str] = None     # only relevant when published

    model_config = ConfigDict(json_schema_extra=conditional_schema(
        When(
            "status",
            equals="archived",
            controls=["archive_reason"],        # hide until condition matches
            then={"required": ["archive_reason"]},
        ),
        When(
            "status",
            equals="published",
            controls=["published_at"],
            then={"required": ["published_at"]},
        ),
    ))
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `field` | The controlling field name. |
| `equals` | Fires when the field equals this value (`const`). |
| `in_` | Fires when the field is one of these values (`enum`). |
| `not_equals` | Fires when the field is **not** this value. |
| `controls` | Field names to move into the `then` branch — the editor hides them until the condition is met. |
| `then` | Extra JSON Schema fragment applied when the condition matches (e.g. `{"required": [...]}`) |
| `else_` | Extra JSON Schema fragment applied when the condition does **not** match. |

---

## 🔗 `dependent_required` – presence-driven required fields

Use `dependent_required` when a field becoming required depends on another
field simply being present (regardless of its value).

```python
from structured.pydantic.conditionals import dependent_required

class ArticleSchema(BaseModel):
    publisher: Optional[str] = None
    edition: Optional[str] = None   # required whenever publisher is filled in

    model_config = ConfigDict(json_schema_extra=conditional_schema(
        dependent_required(publisher=["edition"]),
    ))
```

---

## 🗂️ `dependent_schemas` – presence-driven visibility

Use `dependent_schemas` when you want a field to be **hidden** until another
field is present, and also want to attach a schema fragment to that branch.

```python
from structured.pydantic.conditionals import dependent_schemas

class ArticleSchema(BaseModel):
    publisher: Optional[str] = None
    edition: Optional[str] = None

    model_config = ConfigDict(json_schema_extra=conditional_schema(
        dependent_schemas(
            publisher={"_controls": ["edition"]},
        ),
    ))
```

The `_controls` key inside the branch dict tells `conditional_schema` to move
those fields out of top-level `properties` and into the branch — so the editor
renders them only when `publisher` is present.

---

## 🔀 Combining multiple rules

All helpers can be combined freely inside a single `conditional_schema(...)` call:

```python
class ArticleSchema(BaseModel):
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
```

`When` clauses are grouped under `allOf`; `dependent_required` /
`dependent_schemas` fragments are merged at the top level.

---

## 🛠️ Using with a Django model

Wire the schema to a `StructuredJSONField` the usual way:

```python
from django.db import models
from structured.fields import StructuredJSONField

def init_article():
    return ArticleSchema()

class ArticleModel(models.Model):
    title = models.CharField(max_length=255)
    structured_data = StructuredJSONField(schema=ArticleSchema, default=init_article)
```

The editor will automatically pick up the conditional rules from the schema and
render the form accordingly — hiding `archive_reason` until the user selects
*archived*, and hiding `published_at` until the user selects *published*.

---

## 🔄 Next Steps

- [🧰 Admin Integration](../Admin%20Integration/README.md) – register your model in the Django admin
- [🔗 Relationships](../Relationships/README.md) – ForeignKey and QuerySet fields inside schemas
- [📦 Installation and Basic Usage](../Installation%20and%20Basic%20Usage/README.md)
