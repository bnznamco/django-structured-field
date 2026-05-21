# 🚀 Prefetching Relations

This guide explains how to use Django's `prefetch_related` (and `select_related`) across relations that live *inside* a `StructuredJSONField`.

## 📋 Overview

The per-instance [Caching](../Caching/README.md) layer already collapses the queries needed to hydrate one row's structured data. But once you iterate a queryset of N rows, each row pays its own cache-build cost — and any follow-on FKs on the loaded models (`author.country`, `co_author.publisher`, …) trigger Django's normal N+1.

The structured `prefetch_related` machinery solves that:

* **One inner query per relation hop, across the entire outer queryset** — same semantics as Django's stock `prefetch_related`.
* **Drop-in syntax**: `MyModel.objects.prefetch_related("structured_data__author__country")` Just Works.
* **Auto-installed** on any model that owns a `StructuredJSONField` — no manager opt-in required.
* `Prefetch(queryset=…)` honoured for fine-grained control (custom managers, inner `select_related`, etc.).

## 🎯 Concrete impact

Measured on a fixture of 5 books × 3 distinct authors × 3 countries:

| Access pattern | Without prefetch | With prefetch | Win |
|---|---:|---:|---:|
| `book.structured_data.author.country.name`<br>via `Prefetch(queryset=Author.objects.select_related("country"))` | **11 queries** | **2 queries** | 5.5× |
| `book.structured_data.author.country.name`<br>via bare `prefetch_related("structured_data__author__country")` | **11 queries** | **3 queries** | 3.7× |
| `book.structured_data.co_authors[*].country.name`<br>via `prefetch_related("structured_data__co_authors__country")` | **21 queries** | **3 queries** | 7× |

Numbers stay constant as the outer queryset grows — the whole point of `prefetch_related`.

## 🧩 Basic Usage

```python
from django.db import models
from structured.fields import StructuredJSONField
from structured.pydantic.fields import ForeignKey, QuerySet
from structured.pydantic.models import BaseModel


class Country(models.Model):
    name = models.CharField(max_length=255)


class Author(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)


class BookSchema(BaseModel):
    title: str
    author: ForeignKey[Author] = None
    co_authors: QuerySet[Author]


class Book(models.Model):
    title = models.CharField(max_length=255)
    structured_data = StructuredJSONField(schema=BookSchema, default=dict)
    # No `objects = StructuredManager()` needed — auto-installed.
```

Now you can prefetch through the JSON:

```python
# Bare chain — one query per relation hop (4 queries total for the chain).
for book in Book.objects.prefetch_related("structured_data__author__country"):
    print(book.structured_data.author.country.name)

# QSField — bulk-fetch all co-authors + their countries.
for book in Book.objects.prefetch_related("structured_data__co_authors__country"):
    for co in book.structured_data.co_authors:
        print(co.country.name)
```

## 🔧 Fine-Grained Control with `Prefetch`

When you want SQL JOINs on inner relations, pass a `Prefetch` object with a custom queryset — this collapses the inner-hop query into the outer prefetch:

```python
from django.db.models import Prefetch

qs = Book.objects.prefetch_related(
    Prefetch(
        "structured_data__author",
        queryset=Author.objects.select_related("country"),
    )
)
```

This produces **2 queries** total instead of 3 — the country is JOINed into the author bulk fetch.

Other things `Prefetch(queryset=…)` lets you do:

* Filter the inner queryset: `Author.objects.active()`
* Use a custom manager: `Author.archived_objects.all()`
* Chain further `prefetch_related` / `select_related`

The custom queryset behaves like Django's stock semantics — when the lookup has additional segments past the structured field's terminal relation (e.g. `structured_data__author__country`), the queryset applies to the **deepest** segment.

## 🛑 `select_related` Through a Structured Field — Why It Raises

```python
Book.objects.select_related("structured_data__author")
# → FieldError: select_related() cannot traverse the structured JSON field
#   'structured_data': JSON values are not SQL-joinable. Use prefetch_related()
#   instead, optionally with Prefetch(queryset=...select_related(...)) for
#   inner relations.
```

This is intentional and matches Django's own posture: `select_related` is a SQL JOIN, and JSON columns have no FK constraint for the compiler to join on. The error redirects you to the right tool. If you want JOINs on relations *past* the structured field (e.g. `author.country`), use the `Prefetch(queryset=Author.objects.select_related("country"))` recipe above.

## 🔗 Composition & Chaining

Structured plans compose with everything Django already supports:

```python
# Multiple structured prefetches
Book.objects.prefetch_related(
    "structured_data__author__country",
    "structured_data__co_authors__country",
)

# Mixed with regular Django prefetches and select_related
Book.objects.select_related("category").prefetch_related(
    "structured_data__author",
    "comments",  # regular reverse FK
)

# Chained — clones preserve the structured plan
Book.objects.prefetch_related("structured_data__author__country").filter(
    title__startswith="The"
)

# Clear all prefetches (structured AND regular) with the canonical idiom
qs = Book.objects.prefetch_related("structured_data__author").prefetch_related(None)
```

## 🛠️ Opting Out / Customising the Manager

Auto-install is on by default but is **purely additive** — your existing managers keep their custom methods. Specifically:

* If you declared `objects = MyManager()`, its `_queryset_class` is wrapped to mix in the structured behaviour. Your custom methods stay intact.
* If you declared no manager, Django's auto-created `objects = Manager()` is wrapped.
* If you want a custom queryset that also has structured awareness, mix in `StructuredQuerySetMixin`:

```python
from structured.orm import StructuredQuerySetMixin

class BookQuerySet(StructuredQuerySetMixin, models.QuerySet):
    def published(self):
        return self.filter(published=True)

class Book(models.Model):
    ...
    objects = BookQuerySet.as_manager()
```

To disable auto-install entirely:

```python
# settings.py
STRUCTURED_FIELD = {
    "AUTO_INSTALL_MANAGER": False,
}
```

Then attach the manager explicitly where you want it:

```python
from structured.orm import StructuredManager

class Book(models.Model):
    ...
    objects = StructuredManager()
```

## ⚠️ Pitfalls & Limitations

### Django's own `prefetch_related` can't see JSON paths

This works because we provide a custom manager. If you use a plain `Manager()` (with auto-install disabled), `Book.objects.prefetch_related("structured_data__author")` does **not** raise — but it also does **not** prefetch. Django silently treats the path as unresolvable on the JSON column. Always make sure your model uses `StructuredManager` (auto or explicit) for structured paths to take effect.

### Polymorphic / abstract FKs

`ForeignKey[AbstractModel]` is not currently supported in prefetch paths — the concrete model can only be resolved by reading each row's JSON discriminator, which the planner doesn't do yet. A `FieldError` is raised with a clear message. Open an issue if you need this.

### `.iterator()` and the QSField

Calling `.iterator()` on a queryset returned by a structured QSField bypasses the cached result list and re-queries without the prefetches. Treat structured QSFields as materialised lists once accessed.

### Shared cache + prefetches

When `STRUCTURED_FIELD.CACHE.SHARED = True`, cached instances live across requests. A prefetch-enriched instance carries its joined data (e.g. `author.country.name`) into the cache; if `Country` is later renamed, the cached `author` still holds the stale country object. Don't mix shared cache with long-lived workers if you rely on prefetched secondary relations being fresh.

### Per-type, not per-call-site

Prefetches you request at the call site apply to all references of that model along the path. There's no per-position prefetching (e.g. "prefetch country only for the FK at `child.child.author`"). This matches Django's `prefetch_related` semantics.

## 🔍 How It Works (Brief)

1. `prefetch_related(lookup)` is intercepted by the structured queryset; lookups whose head names a `StructuredJSONField` are parsed against the schema's relation graph.
2. After the outer rows are fetched, PKs are gathered from raw JSON across **all** rows in one pass.
3. One inner query per target model — enriched with your `select_related`/`prefetch_related` hints — runs across the entire outer queryset.
4. Results land in a thread-local seed cache that the per-instance [Caching](../Caching/README.md) engine consults before issuing its own queries. No duplicate work; no manual attach.

## 🔄 Next Steps

- [⚡ Caching](../Caching/README.md) — the per-instance layer prefetches build on top of
- [🔗 Relationships](../Relationships/README.md) — the relation field types (`ForeignKey`, `QuerySet`) that can be prefetched
- [🛠️ Settings Configuration](../Settings%20Configuration/README.md) — the `AUTO_INSTALL_MANAGER` setting
