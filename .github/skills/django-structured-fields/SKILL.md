---
name: django-structured-fields
description: Skill for working on the django-structured-json-field codebase — a Django JSONField supercharged with Pydantic validation, FK/QS caching, a JSON-editor admin widget, and DRF integration. Use this skill when tasks involve StructuredJSONField, Pydantic BaseModel schemas, the cache engine, admin widget, REST framework serializers, data migration generation, or the frontend reactive-forms layer.
---

# Django Structured JSON Field — Agent Skill

## 1. Project Identity

| Key | Value |
|-----|-------|
| Package name | `django-structured-json-field` |
| Python module | `structured` |
| Version | Stored in `structured/__init__.py` (`__version__`) and `setup.py` |
| License | MIT |
| Python support | >= 3.10 (up to 3.14) |
| Django support | 4.2, 5.0, 5.1, 5.2 |
| Pydantic | >= 2.12 |
| DRF | >= 3.14, < 4.0 |
| Branch | `master` (release), `next` (beta), `feature/*` (development) |
| Semantic Release | Configured in `pyproject.toml` with version variables in `setup.py` and `structured/__init__.py` |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Django Model Layer                              │
│  StructuredJSONField(JSONField)  ←──  schema=SomePydanticModel         │
│  StructuredDescriptior           (lazy validation on __get__)          │
└────────────┬───────────────────────────────────────┬────────────────────┘
             │ validates via                         │ formfield()
             ▼                                       ▼
┌────────────────────────────┐       ┌──────────────────────────────────┐
│   Pydantic Layer           │       │   Widget Layer (Admin)           │
│   BaseModel (BaseModelMeta)│       │   StructuredJSONFormWidget       │
│   ForeignKey[T]            │       │   StructuredJSONFormField        │
│   QuerySet[T]              │       │   template: widget.html          │
│   FieldSerializer          │       │   JSONEditor + Select2           │
└────────────┬───────────────┘       └──────────────────────────────────┘
             │ @model_validator                       ▲ AJAX search
             ▼                                        │
┌────────────────────────────┐       ┌──────────────────────────────────┐
│   Cache Layer              │       │   Views                          │
│   CacheEngine              │       │   search_view (staff-only)       │
│   Cache / ThreadSafeCache  │       │   /structured_field/search_model │
│   ValueWithCache           │       └──────────────────────────────────┘
│   RelInfo                  │
└────────────────────────────┘       ┌──────────────────────────────────┐
                                     │   DRF Contrib                    │
                                     │   StructuredModelSerializer      │
                                     │   StructuredJSONField (DRF)      │
                                     │   FieldsOverrideMixin            │
                                     └──────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                    Frontend (reactive-forms/)                           │
│   main.js → JSONEditor init    callbacks.js → Select2 AJAX             │
│   patches.js → Select2 editor   scss/ → Admin theme integration        │
│   Rollup build → structured/static/js/ & css/                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Directory Map & File Roles

### Python — `structured/`

| Path | Role |
|------|------|
| `structured/__init__.py` | Package init, `__version__` |
| `structured/fields.py` | **Core**: `StructuredJSONField`, `StructuredDescriptior` (Django model field) |
| `structured/apps.py` | Django `AppConfig` |
| `structured/settings.py` | `Settings` singleton — reads `STRUCTURED_FIELD` from Django settings |
| `structured/urls.py` | URL patterns for admin AJAX search endpoint |
| `structured/views.py` | `search_view` — staff-only model search for Select2 dropdowns |
| `structured/pydantic/models.py` | `BaseModel`, `BaseModelMeta` — custom Pydantic model with metaclass |
| `structured/pydantic/__init__.py` | Re-exports `BaseModel` |
| `structured/pydantic/fields/foreignkey.py` | `ForeignKey[T]` — Pydantic type for single Django model FK |
| `structured/pydantic/fields/queryset.py` | `QuerySet[T]` — Pydantic type for Django QuerySet/M2M-like |
| `structured/pydantic/fields/serializer.py` | `FieldSerializer` — custom DRF serializer override for fields |
| `structured/cache/cache.py` | `Cache`, `ThreadSafeCache` — in-memory caches with Django signal listeners |
| `structured/cache/engine.py` | `CacheEngine` — N+1 prevention: batch FK/QS lookups |
| `structured/cache/rel_info.py` | `RelInfo` — data class for relationship metadata |
| `structured/cache/__init__.py` | `CacheEnabledModel` mixin, `ValueWithCache` wrapper |
| `structured/widget/widgets.py` | `StructuredJSONFormWidget` — JSON editor admin widget |
| `structured/widget/fields.py` | `StructuredJSONFormField` — Django form field with Pydantic validation |
| `structured/contrib/restframework.py` | DRF integration: serializer field, mixin, `StructuredModelSerializer` |
| `structured/migrations/structured_json_migration.py` | `StructuredJSONMigrationGenerator` — schema migration code generator |
| `structured/management/commands/generate_schema_migration.py` | Management command to analyze data + generate migration templates |
| `structured/utils/cast.py` | `cast_to_python`, `cast_to_model` — type coercion helpers |
| `structured/utils/context.py` | `build_context`, `increase_context_depth` — serialization context |
| `structured/utils/dict.py` | `dict_merge` — deep dict merge (used in PATCH) |
| `structured/utils/django.py` | `import_abs_model` — import abstract Django models by label |
| `structured/utils/errors.py` | `map_pydantic_errors` — Pydantic → Django error dict conversion |
| `structured/utils/getter.py` | `pointed_getter` — dot-path traversal reader |
| `structured/utils/setter.py` | `pointed_setter` — dot-path traversal writer |
| `structured/utils/namespace.py` | `merge_cls_and_parent_ns` — namespace merging for forward refs |
| `structured/utils/options.py` | `build_relation_schema_options` — Select2 JSON schema metadata |
| `structured/utils/pydantic.py` | `patch_annotation`, `map_method_aliases` — annotation rewriting engine |
| `structured/utils/replace.py` | `find_and_replace_dict` — recursive dict transformation |
| `structured/utils/serializer.py` | `build_model_serializer`, `BaseModelSerializer` — dynamic DRF serializer factory |
| `structured/utils/typing.py` | `LazyType`, `get_type`, `find_model_type_from_args` — type introspection |

### Frontend — `reactive-forms/`

| Path | Role |
|------|------|
| `reactive-forms/main.js` | Entry point: initializes JSONEditor for `.structured-field-editor` elements |
| `reactive-forms/callbacks.js` | `initCallbacks()` — Select2 AJAX params (`_q`, `page`) and result mapping |
| `reactive-forms/patches.js` | `patchSelect2Editor()` — extends JSONEditor's Select2 editor for relation types |
| `reactive-forms/scss/main.scss` | SCSS entry — imports component stylesheets |
| `reactive-forms/scss/components/editor.scss` | `.structured-field-editor` styling (Django admin theme vars) |
| `reactive-forms/scss/components/select2.custom.scss` | Select2 dropdown theming (Django admin CSS vars) |

### Build output → `structured/static/`

| Path | Content |
|------|---------|
| `structured/static/js/structured-field-form.js` | Unminified IIFE bundle (dev) |
| `structured/static/js/structured-field-form.min.js` | Minified IIFE bundle (prod) |
| `structured/static/css/structured-field-form.min.css` | Compiled + compressed SCSS |
| `structured/static/libs/` | Vendored libraries (JSONEditor, Select2, FontAwesome) |

### Template

| Path | Content |
|------|---------|
| `structured/templates/json-forms/widget.html` | Django template: renders `<div>` with `data-schema`, `data-formdata`, `data-uischema` attributes + hidden `<textarea>` for form submission |

### Tests — `tests/`

| Path | Role |
|------|------|
| `tests/app/app/settings.py` | Django settings (`DJANGO_SETTINGS_MODULE`) |
| `tests/app/app/urls.py` | URL config: admin + structured.urls + DRF router |
| `tests/app/test_module/models.py` | **All test models and schemas** — `TestModel`, `TestSchema`, `TestSchema2`, `UnionSchema`, `RecursiveOnModelSchema`, `SimpleRelationModel`, abstract models |
| `tests/app/test_module/admin.py` | Admin registration for test models |
| `tests/app/test_module/serializers.py` | `TestModelSerializer(StructuredModelSerializer)` |
| `tests/app/test_module/views.py` | `TestModelViewSet(ModelViewSet)` |
| `tests/fixtures/__init__.py` | `load_json_fixture()`, `load_asset()` helpers |
| `tests/fixtures/assets/` | Binary test assets (PNG) |
| `tests/utils/media.py` | `load_asset_and_remove_media()` — file test helper |
| `conftest.py` | Root fixtures: `django_db_setup`, `cache_setting_fixture`, `recursion_depth_setting_fixture` |

---

## 4. Key Concepts & Design Patterns

### 4.1 Lazy Descriptor Validation
`StructuredDescriptior` (in `fields.py`) extends `DeferredAttribute`. Data stays as a raw dict in `instance.__dict__` until the attribute is accessed. On first access, `schema.validate_python()` converts it to a Pydantic model instance and caches in `__dict__`. This means zero validation cost if the field is never read.

### 4.2 Metaclass-Driven Annotation Rewriting
`BaseModelMeta.__new__` runs `patch_annotation()` on every field annotation. This auto-converts:
- A bare Django `Model` class → `ForeignKey[Model]`
- `QuerySet[Model]` → `Annotated[QuerySet[Model], Field(default_factory=...)]`
- Forward references are resolved via module globals + parent frame namespace

This allows users to write `author: User` and get full FK behavior automatically.

### 4.3 Batched Cache Loading (N+1 Prevention)
`CacheEngine.build_cache()` flow:
1. `get_all_fk_data(data)` walks all nested fields recursively, collecting `{Model: [pk_list]}`.
2. `_build_plainset()` deduplicates PKs per model class.
3. `_populate_cache()` issues one `Model.objects.filter(pk__in=pks)` per model.
4. `_set_cache_values()` replaces raw PKs in the data dict with `ValueWithCache` wrappers.
5. `fetch_cache()` calls `.retrieve()` on each wrapper after validation.

Relationship types tracked via `RelInfo`:
- `fk` — single ForeignKey
- `qs` — QuerySet (many)
- `rel` — nested BaseModel (recurse into its cache engine)
- `rel_l` — list of nested BaseModels

### 4.4 Signal-Based Cache Invalidation
`Cache` registers `post_save` and `pre_delete` Django signals to keep cached model instances up-to-date. `ThreadSafeCache` (`CACHE.SHARED = True`) is a singleton — may retain stale data across requests if signals aren't firing.

### 4.5 Dual Serialization: `_raw` Property
`StructuredJSONField.contribute_to_class()` adds a `<field>_raw` property to the Django model class. This returns the raw dict from `from_db_value()` without validation — useful for migrations and debugging.

### 4.6 Dynamic DRF Serializer Factory
`build_model_serializer(model)` creates a `ModelSerializer` subclass on-the-fly for any Django model. It maps `StructuredJSONField` to `JSONFieldInnerSerializer` and respects `MAX_DEPTH` to prevent infinite recursion.

### 4.7 PATCH Deep Merge
The DRF `StructuredJSONField.to_internal_value()` handles PATCH by deep-merging old + new data via `dict_merge()`, so partial updates don't wipe unmodified nested fields.

### 4.8 JSON Schema for Admin Widget
FK/QS fields add `format: "select2"` and `type: "relation"` to their JSON schema. The JSONEditor resolver detects this and uses the patched Select2 editor (`patches.js`), which makes AJAX calls to `/structured_field/search_model/<model>/` for autocomplete.

### 4.9 Schema Migration Generator
The `generate_schema_migration` command:
1. Scans all DB rows for validation errors against the current schema.
2. Groups errors by type/location.
3. Generates a complete Django migration file with `RunPython` + transform functions.
4. Supports `--analyze-only` for inspection without generating files.

### 4.10 Python 3.14 / PEP 649 Support
`BaseModelMeta._get_raw_annotations()` handles deferred annotations using `annotationlib.get_annotations(FORMAT.FORWARDREF)` on Python 3.14+.

### 4.11 Extra = 'ignore' by Default
`BaseModel` uses `ConfigDict(extra='ignore')`, meaning unknown fields in JSON data are silently dropped. This makes schema evolution forward-compatible — no need to migrate data when removing fields.

---

## 5. Coding Conventions

### Python

- **Import style**: Standard library → third-party → Django → local. Absolute imports within the `structured` package.
- **No docstrings in most internal code**: Code is self-documenting; inline comments used sparingly for non-obvious logic.
- **Type annotations**: Used extensively throughout. Pydantic models are fully typed. Internal utilities use basic type hints.
- **Naming**:
  - Classes: `PascalCase`
  - Functions/methods: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_single_underscore_prefix`
  - File names: `snake_case.py`
- **Note**: `StructuredDescriptior` is the established spelling (typo preserved for backward compatibility). Do NOT rename it.
- **Error mapping**: Pydantic `ValidationError` is always converted to nested dicts via `map_pydantic_errors()` before surfacing to Django/DRF.
- **Field registration in `__init__`**: Custom Pydantic fields define their core schema via `__get_pydantic_core_schema__` classmethod.
- **Metaclass usage**: `BaseModelMeta` extends Pydantic's `ModelMetaclass` and must be maintained carefully — annotation patching order matters.
- **Settings access**: Always through the `Settings` singleton (`structured.settings`), never directly from `django.conf.settings`.

### Frontend (JavaScript / SCSS)

- **Plain ES modules**: No framework (React/Vue). Uses vanilla JS + JSONEditor library.
- **IIFE output**: Rollup bundles to IIFE format for Django admin (no module loader).
- **Class extension**: `patches.js` extends `JSONEditor.defaults.editors.select2` using ES6 class syntax.
- **Django CSS variables**: SCSS uses Django admin CSS custom properties (`--body-bg`, `--border-color`, `--error-fg`, etc.) for theme integration.
- **Data flow**: JSON schema + form data passed via HTML `data-*` attributes on the widget `<div>`. Editor changes write back to a hidden `<textarea>`.
- **Build command**: `pnpm run build` (or `npx rollup -c`) — outputs to `structured/static/`.

### Tests

- **Framework**: pytest + pytest-django.
- **Markers**: All DB tests use `@pytest.mark.django_db`.
- **Cache parametrization**: Most tests are decorated with `@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)` to run across all cache configurations.
- **Late imports**: Models are imported inside test functions, not at module top level.
- **Standalone functions**: Tests are top-level pytest functions (not classes), except `TestRestFramework` which uses a class with `setup_method`.
- **Query counting**: `django_assert_num_queries` from pytest-django for cache/performance assertions.
- **Admin tests**: Use `admin_client` fixture, POST data as strings, check HTTP 302 redirects.
- **DRF tests**: Use `rest_framework.test.APIClient`.
- **Settings override**: `conftest.py` provides indirect parametrize fixtures that modify `settings.STRUCTURED_FIELD` dict.
- **Test DB**: SQLite at `test_db.sqlite3`, managed by session-scoped `django_db_setup` fixture.

---

## 6. How to Add or Modify Features

### Adding a New Pydantic Field Type

1. Create a new file in `structured/pydantic/fields/` (e.g., `mytype.py`).
2. Define a class with `__class_getitem__` (for generic syntax) and `__get_pydantic_core_schema__`.
3. Implement validators (from raw data) and serializer (to JSON).
4. If it references Django models, add relationship handling in `structured/cache/engine.py` — register a new `RelInfo` type.
5. If it needs admin widget support, add JSON schema metadata (e.g., `format`, `type` keys) and handle it in `reactive-forms/patches.js`.
6. Export from `structured/pydantic/fields/__init__.py`.
7. Add annotation patching support in `structured/utils/pydantic.py` → `patch_annotation()` if auto-conversion is desired.

### Adding a New Utility

1. Create a file in `structured/utils/`.
2. Use pure functions with type hints.
3. Import into `structured/utils/__init__.py` if it should be part of the public API.

### Modifying the Cache System

- Cache population: `structured/cache/engine.py` → `_populate_cache()`.
- Cache invalidation: `structured/cache/cache.py` → signal handlers.
- Relationship discovery: `engine.py` → `_get_rel_info()` and `get_all_fk_data()`.
- Shared cache singleton: `cache.py` → `ThreadSafeCache`.
- **Important**: The cache wraps raw PK values with `ValueWithCache` *before* Pydantic validation, then resolves them *after*. This two-phase design is critical.

### Modifying the Admin Widget

- Python side: `structured/widget/widgets.py` manages which CSS/JS files are loaded, and `structured/widget/fields.py` handles form validation.
- Template: `structured/templates/json-forms/widget.html` — the `data-schema`, `data-formdata`, `data-uischema` attributes.
- JS side: `reactive-forms/main.js` initializes JSONEditor, `callbacks.js` configures AJAX, `patches.js` extends Select2 for relations.
- After JS/SCSS changes, rebuild: `pnpm run build` (or `npx rollup -c rollup.config.mjs`).
- Built assets go to `structured/static/js/` and `structured/static/css/`.

### Modifying DRF Integration

- `structured/contrib/restframework.py` contains the serializer field, mixin, and `StructuredModelSerializer`.
- `to_representation` uses `model_dump()` with context depth tracking.
- `to_internal_value` handles PATCH via `dict_merge` and validates via Pydantic schema.
- Error mapping uses `map_pydantic_errors()`.

### Adding/Modifying Migrations Support

- `structured/migrations/structured_json_migration.py` — the generator class.
- `structured/management/commands/generate_schema_migration.py` — the CLI entry point.
- The generator analyzes live data via `analyze_validation_errors()` and produces Python code strings.

---

## 7. How to Write Tests

### Test Location & Naming
- Test files go in `tests/` with `test_` prefix.
- Use standalone functions (not classes) unless shared setup is needed.

### Required Patterns

```python
import pytest

@pytest.mark.django_db
@pytest.mark.parametrize(
    "cache_setting_fixture",
    ["cache_enabled", "cache_disabled", "shared_cache"],
    indirect=True,
)
def test_my_feature(cache_setting_fixture):
    # Import models inside the test function
    from tests.app.test_module.models import TestModel, SimpleRelationModel

    # Create test data
    rel = SimpleRelationModel.objects.create(name="Test")
    obj = TestModel.objects.create(
        title="Test",
        structured_data={"name": "test", "age": 25, "fk_field": rel.pk},
    )

    # Refresh and assert
    obj.refresh_from_db()
    assert obj.structured_data.name == "test"
    assert obj.structured_data.fk_field == rel
```

### Query Count Tests

```python
@pytest.mark.django_db
def test_query_efficiency(django_assert_num_queries):
    from tests.app.test_module.models import TestModel
    obj = TestModel.objects.create(...)
    with django_assert_num_queries(N):
        obj.refresh_from_db()
        _ = obj.structured_data.some_field
```

### DRF Tests

```python
from rest_framework.test import APIClient

class TestMyAPI:
    def setup_method(self):
        self.client = APIClient()
        # Create test data

    @pytest.mark.django_db
    def test_get(self):
        response = self.client.get("/api/testmodels/1/")
        assert response.status_code == 200
```

### Test Models
All test schemas and Django models live in `tests/app/test_module/models.py`. If a new model/schema is needed for testing, add it there and run `python manage.py makemigrations test_module`.

### Running Tests

```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_structured_field.py -v

# With coverage
pytest --cov=structured -s -vv --cov-report=xml --cov-report=term-missing

# Via Makefile
make test
```

---

## 8. Common Debugging Scenarios

### "N+1 queries" / Performance Issues
- Check if `STRUCTURED_FIELD['CACHE']['ENABLED']` is `True`.
- Inspect `CacheEngine.get_all_fk_data()` — verify all FK/QS fields are discovered.
- Use `django_assert_num_queries` in tests to verify.
- Look at `_get_rel_info()` in `engine.py` to confirm relationship type detection.

### Pydantic Validation Errors
- `StructuredJSONField.validate()` calls `schema.validate_python(cast_to_python(value))`.
- Errors are mapped via `map_pydantic_errors()` → nested dict keyed by field path.
- For DRF, errors surface as DRF `ValidationError` with the same nested structure.
- Check `patch_annotation()` in `utils/pydantic.py` if annotation rewriting is suspected.

### Admin Widget Not Rendering
- Ensure `structured` is in `INSTALLED_APPS`.
- Ensure `path("", include("structured.urls"))` is in URL config.
- Check that `formfield()` in `fields.py` returns `StructuredJSONFormField` with correct schema.
- Verify static files are built: `structured/static/js/structured-field-form.min.js` must exist.

### Select2 Autocomplete Not Working
- The AJAX endpoint is `/structured_field/search_model/<app_label>.<model_name>/`.
- `views.py` → `search()` requires staff authentication.
- Check `build_relation_schema_options()` in `utils/options.py` for JSON schema metadata.
- Frontend: `callbacks.js` sends `_q` (search term) and `page` params.
- `patches.js` resolver checks `schema.type === "relation"` and `schema.format === "select2"`.

### Forward Reference Resolution Issues
- `BaseModelMeta` builds a namespace from module globals + parent frame.
- `utils/namespace.py` → `merge_cls_and_parent_ns()`.
- Python 3.14: Uses `annotationlib.get_annotations(FORMAT.FORWARDREF)`.
- Check `LazyType` in `utils/typing.py` for dot-path type resolution.

### Cache Invalidation Problems
- `Cache` uses `post_save` / `pre_delete` signals.
- `ThreadSafeCache` (`CACHE.SHARED = True`) is a singleton — may retain stale data across requests if signals aren't firing.
- `flush(filters=None)` clears cache optionally per-model.
- Inspect signal connections in `cache.py`.

### Schema Migration Issues
- Run `python manage.py generate_schema_migration <app> <model> --analyze-only` first.
- Generated migration is a template — humans must review and customize transform functions.
- `extra='ignore'` means removed fields don't need migration (silently dropped).
- New required fields without defaults DO need data migration.

---

## 9. Settings Reference

Configure via `STRUCTURED_FIELD` dict in Django settings:

```python
STRUCTURED_FIELD = {
    "CACHE": {
        "ENABLED": True,    # Enable FK/QS cache (default: True)
        "SHARED": False,    # Use global thread-safe cache (default: False, experimental)
    },
    "SERIALIZATION": {
        "MAX_DEPTH": 2,     # Max depth for nested model serialization (default: 2)
    },
}
```

Access in code: `from structured.settings import Settings; Settings().CACHE_ENABLED`.

---

## 10. Build & Development Commands

```bash
# Python
pip install -e ".[dev]"            # Install in dev mode
pytest -v                          # Run tests
make test                          # Lint (flake8) + tests with coverage
python manage.py makemigrations    # After model changes
python manage.py migrate           # Apply migrations
python manage.py generate_schema_migration <app> <model>  # Schema migration

# Frontend
pnpm install                       # Install JS dependencies
pnpm run build                     # Build JS/CSS → structured/static/
npx rollup -c rollup.config.mjs    # Manual build
# Rollup config: reactive-forms/main.js → structured/static/js/ + css/

# Versioning
# Managed by python-semantic-release via pyproject.toml
# Version stored in: setup.py (__version__) and structured/__init__.py (__version__)
```

---

## 11. Important Warnings

1. **Do NOT rename `StructuredDescriptior`** — it's a known typo preserved for backward compatibility.
2. **Annotation patching order matters** in `BaseModelMeta.__new__()` — `patch_annotation()` must run before `super().__new__()` calls Pydantic's metaclass.
3. **Cache two-phase design**: `ValueWithCache` wrappers are injected *before* Pydantic validation and resolved *after*. Do not change this order.
4. **`extra='ignore'` is intentional** on `BaseModel` — do not change to `'forbid'` without considering all downstream migration implications.
5. **Models imported inside tests** — this is intentional to avoid import-time side effects with Django app registry.
6. **Test DB (`test_db.sqlite3`)** is created by session-scoped fixture — do not commit it or rely on its state between test runs programmatically.
7. **Frontend build output** (`structured/static/`) is committed to the repo — after JS/SCSS changes, rebuild before committing.
8. **Abstract model FK resolution** uses a `model` key in the dict data to determine the concrete model class. `QuerySet` fields do NOT support abstract models.