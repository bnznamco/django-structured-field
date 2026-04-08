"""Helpers to declare conditional/dependent field logic on Pydantic models.

These compile down to standard JSON Schema keywords (``if``/``then``/``else``,
``allOf``, ``dependentSchemas``, ``dependentRequired``) so that:

* Pydantic v2 enforces them at validation time out of the box.
* Any JSON Schema consumer (including the structured-widget-editor frontend)
  can read them without custom extensions.

The key concept is **controlled fields**: fields whose *visibility* in the form
is driven by a condition.  Pydantic normally emits every annotated field in the
top-level ``properties`` block, which would make all fields always visible.
``conditional_schema`` returns a *callable* (Pydantic v2 supports this for
``json_schema_extra``) that post-processes the generated schema and moves
controlled fields out of the top-level ``properties`` and into the ``then`` /
``else`` / ``dependentSchemas`` branches where they belong.  The frontend
then shows or hides them reactively as the data changes.

Typical usage::

    from typing import Literal, Optional
    from pydantic import ConfigDict
    from structured.pydantic.models import BaseModel
    from structured.pydantic.conditionals import (
        When, dependent_schemas, dependent_required, conditional_schema,
    )

    class Book(BaseModel):
        status: Literal["draft", "review", "published", "archived"] = "draft"
        archive_reason: Optional[str] = None   # shown only when archived
        published_at: Optional[str] = None     # shown only when published
        publisher: Optional[str] = None
        edition: Optional[str] = None          # shown only when publisher present

        model_config = ConfigDict(json_schema_extra=conditional_schema(
            When("status", equals="archived",
                 controls=["archive_reason"],
                 then={"required": ["archive_reason"]}),
            When("status", equals="published",
                 controls=["published_at"],
                 then={"required": ["published_at"]}),
            dependent_schemas(
                publisher={"_controls": ["edition"]},
            ),
        ))

``controls`` lists the field names whose schema should be moved from the base
``properties`` into the matching ``then``/``else`` block.  Without ``controls``,
``then`` only affects validation constraints (e.g. ``required``) on fields that
are always visible.
"""

from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Union

__all__ = [
    "When",
    "conditional_schema",
    "dependent_schemas",
    "dependent_required",
    "merge_schema_extra",
]

# Sentinel for "argument not provided"
_MISSING = object()


def _property_constraint(
    *,
    equals: Any = _MISSING,
    in_: Optional[Iterable[Any]] = None,
    not_equals: Any = _MISSING,
) -> Dict[str, Any]:
    constraint: Dict[str, Any] = {}
    if equals is not _MISSING:
        constraint["const"] = equals
    if in_ is not None:
        constraint["enum"] = list(in_)
    if not_equals is not _MISSING:
        constraint["not"] = {"const": not_equals}
    if not constraint:
        raise ValueError("When(...) requires one of: equals=, in_=, not_equals=")
    return constraint


def When(
    field: str,
    *,
    equals: Any = _MISSING,
    in_: Optional[Iterable[Any]] = None,
    not_equals: Any = _MISSING,
    controls: Optional[List[str]] = None,
    then: Optional[Mapping[str, Any]] = None,
    else_: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a single ``{"if": ..., "then": ..., "else": ...}`` clause.

    Parameters
    ----------
    field:
        The field whose value drives the condition (the "controller").
    equals / in\\_ / not_equals:
        Value constraint for the controller field.
    controls:
        Field names that should only be visible when this condition is
        satisfied.  ``conditional_schema`` will move their schemas from
        the model's top-level ``properties`` into ``then.properties`` so
        the frontend hides them when the condition is not met.
    then / else\\_ :
        Extra JSON Schema fragments merged when the condition matches /
        does not match (e.g. ``{"required": ["archive_reason"]}``).
    """
    constraint = _property_constraint(equals=equals, in_=in_, not_equals=not_equals)
    clause: Dict[str, Any] = {
        "if": {
            "properties": {field: constraint},
            "required": [field],
        },
        "_controls": list(controls or []),
    }
    if then is not None:
        clause["then"] = dict(then)
    if else_ is not None:
        clause["else"] = dict(else_)
    return clause


def dependent_schemas(**mapping: Mapping[str, Any]) -> Dict[str, Any]:
    """Wrap kwargs as a ``{"dependentSchemas": {...}}`` fragment.

    Each key is a field name; when that field is present and non-empty,
    its mapped schema fragment is merged into the parent.

    To make certain fields visible only when the key is present, include
    ``"_controls": ["field1", "field2"]`` in the branch dict — or use the
    shorthand ``controls(...)`` helper::

        dependent_schemas(
            publisher={"_controls": ["edition"]},
        )
    """
    return {"dependentSchemas": {k: dict(v) for k, v in mapping.items()}}


def dependent_required(**mapping: List[str]) -> Dict[str, Any]:
    """Wrap kwargs as a ``{"dependentRequired": {...}}`` fragment.

    Each key is a field name; the value is the list of fields that
    become *required* whenever that key is present and non-empty.
    The dependent fields are not hidden — use :func:`dependent_schemas`
    with ``_controls`` if you also want them hidden.
    """
    return {"dependentRequired": {k: list(v) for k, v in mapping.items()}}


def merge_schema_extra(*fragments: Mapping[str, Any]) -> Dict[str, Any]:
    """Shallow-merge ``json_schema_extra`` fragments, unioning known keys.

    ``allOf`` lists are concatenated; ``dependentSchemas`` /
    ``dependentRequired`` dicts are merged.  Anything else is overwritten
    by later fragments.
    """
    out: Dict[str, Any] = {}
    for frag in fragments:
        if not frag:
            continue
        for k, v in frag.items():
            if k == "allOf" and isinstance(out.get("allOf"), list) and isinstance(v, list):
                out["allOf"] = out["allOf"] + list(v)
            elif k in ("dependentSchemas", "dependentRequired") and isinstance(out.get(k), dict) and isinstance(v, dict):
                merged = dict(out[k])
                merged.update(v)
                out[k] = merged
            else:
                out[k] = v
    return out


def _pop_controlled_fields(properties: Dict[str, Any], controls: List[str]) -> Dict[str, Any]:
    """Remove *controls* from *properties* and return their schemas."""
    moved: Dict[str, Any] = {}
    for field in controls:
        if field in properties:
            moved[field] = properties.pop(field)
    return moved


def conditional_schema(
    *rules: Union[Mapping[str, Any], None],
) -> Callable[[Dict[str, Any]], None]:
    """Combine ``When(...)`` clauses and dependent_* fragments into a
    ``json_schema_extra`` *callable* ready to assign to ``ConfigDict``.

    Pydantic v2 calls ``json_schema_extra`` with the fully-generated schema
    dict so it can be mutated in place.  We use this to move every
    **controlled** field (listed in ``controls=``) out of the top-level
    ``properties`` and into the appropriate ``then`` / ``else`` /
    ``dependentSchemas`` branch.  This ensures the frontend only renders
    those fields when their condition is satisfied.

    Rules that carry no ``controls`` only affect validation constraints
    (e.g. toggling ``required``) on fields that are always visible.
    """
    # Snapshot the rules now so the returned callable is self-contained.
    _rules = [dict(r) for r in rules if r]

    def apply(schema: Dict[str, Any]) -> None:
        properties: Dict[str, Any] = schema.setdefault("properties", {})
        all_of: List[Dict[str, Any]] = []
        dep_schemas: Dict[str, Any] = {}
        dep_required: Dict[str, Any] = {}

        for rule in _rules:
            # ── if/then/else clause produced by When() ────────────────────
            if "if" in rule:
                controls = rule.get("_controls") or []
                then = dict(rule.get("then") or {})
                else_ = dict(rule.get("else") or {})

                # Move controlled fields into the then branch.
                moved = _pop_controlled_fields(properties, controls)
                if moved:
                    then.setdefault("properties", {}).update(moved)

                clause: Dict[str, Any] = {"if": rule["if"]}
                if then:
                    clause["then"] = then
                if else_:
                    clause["else"] = else_
                all_of.append(clause)

            # ── dependentSchemas fragment ─────────────────────────────────
            elif "dependentSchemas" in rule:
                for key, branch in rule["dependentSchemas"].items():
                    branch = dict(branch)
                    controls = branch.pop("_controls", [])
                    moved = _pop_controlled_fields(properties, controls)
                    if moved:
                        branch.setdefault("properties", {}).update(moved)
                    dep_schemas[key] = branch

            # ── dependentRequired fragment ────────────────────────────────
            elif "dependentRequired" in rule:
                dep_required.update(rule["dependentRequired"])

            # ── plain dict (extra top-level keywords) ────────────────────
            else:
                for k, v in rule.items():
                    schema[k] = v

        if all_of:
            existing = schema.get("allOf", [])
            schema["allOf"] = existing + all_of
        if dep_schemas:
            existing = schema.get("dependentSchemas", {})
            schema["dependentSchemas"] = {**existing, **dep_schemas}
        if dep_required:
            existing = schema.get("dependentRequired", {})
            schema["dependentRequired"] = {**existing, **dep_required}

    return apply
