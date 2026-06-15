"""
Django ``QuerySet`` / ``Manager`` subclasses that make
``prefetch_related`` (and a locked-down ``select_related``) traverse paths
that cross a :class:`~structured.fields.StructuredJSONField`.

Usage
-----
Opt in by attaching :class:`StructuredManager` (or
``StructuredQuerySet.as_manager()``) to any model that owns a
``StructuredJSONField``::

    class Article(models.Model):
        structured_data = StructuredJSONField(schema=ArticleSchema)
        objects = StructuredManager()

Then write Django-flavored lookups across the JSON::

    Article.objects.prefetch_related("structured_data__author__country")
    Article.objects.prefetch_related(
        Prefetch(
            "structured_data__authors",
            queryset=Author.objects.active().select_related("country"),
        ),
    )

Design notes
------------
* ``prefetch_related("structured_data__author__country")`` is parsed by
  splitting on ``LOOKUP_SEP``. The head segment must name a
  ``StructuredJSONField`` on the queryset's model. Subsequent segments are
  walked against the schema's relation graph (built by
  :class:`structured.cache.engine.CacheEngine`) until a Django relation
  field (``FKField`` or ``QSField``) is reached. Everything past that
  point is applied as ``prefetch_related`` on the inner bulk fetch — the
  same query model Django itself uses for nested prefetches.

* ``select_related`` cannot SQL-JOIN through a JSON column. Any path
  whose head is a structured field raises ``FieldError`` with a redirect
  message — mirroring Django's behaviour for ``select_related`` on M2M.
  Users who want JOINs on inner relations can pass
  ``Prefetch(..., queryset=Inner.objects.select_related(...))``.

* Inner fetches happen exactly once per ``(target_model, plan)`` across
  the entire outer queryset, not once per outer row. PKs are gathered
  from raw JSON before structured-field validation runs, and the
  prefetch-enriched instances are pushed into a thread-local seed cache
  that :func:`structured.cache.engine.CacheEngine._populate_cache`
  consults before issuing its own filter. The existing per-instance
  cache machinery handles attribute attach.

* :class:`~django.db.models.Prefetch` objects are honoured. The supplied
  queryset is used as the base for the inner ``filter(pk__in=...)``. When
  combined with a path that has remaining segments past the structured
  field's terminal relation, the custom queryset is forwarded to the
  *terminal* relation as an inner Prefetch (matching Django's semantics
  for ``Prefetch("a__b__c", queryset=...)`` where ``queryset`` applies
  to ``c``).
"""
from __future__ import annotations

import copy
import threading
from collections import defaultdict
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Prefetch
from django.db.models.constants import LOOKUP_SEP

from structured.cache.rel_info import RelInfo


# ---------------------------------------------------------------------------
# Thread-local seed cache.
#
# StructuredQuerySet populates a {model: {pk: instance}} mapping with the
# results of its bulk inner fetches (each enriched with the user's
# select_related / prefetch_related hints). CacheEngine._populate_cache
# consults the active seed before issuing its own filter, so prefetch-aware
# instances flow into the per-instance cache without duplicate queries.
# ---------------------------------------------------------------------------

_state = threading.local()


def _seed_stack() -> List[Dict[Type[models.Model], Dict[Any, models.Model]]]:
    stack = getattr(_state, "stack", None)
    if stack is None:
        stack = []
        _state.stack = stack
    return stack


def current_seed_cache() -> Mapping[Type[models.Model], Mapping[Any, models.Model]]:
    """
    Return the currently-active seed mapping, or an empty dict if none.

    Consumed by :meth:`structured.cache.engine.CacheEngine._populate_cache`.
    """
    stack = _seed_stack()
    return stack[-1] if stack else {}


class _SeedScope:
    """Push/pop a seed mapping on the thread-local stack."""

    __slots__ = ("_seed",)

    def __init__(self, seed: Dict[Type[models.Model], Dict[Any, models.Model]]):
        self._seed = seed

    def __enter__(self):
        _seed_stack().append(self._seed)
        return self._seed

    def __exit__(self, *exc):
        _seed_stack().pop()


# ---------------------------------------------------------------------------
# Plan: the parsed form of a structured prefetch lookup.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StructuredPrefetchPlan:
    """
    The resolved form of a ``prefetch_related`` lookup that crosses a
    :class:`StructuredJSONField`.

    ``json_path`` is the walk inside the JSON document, with ``'*'``
    marking list iteration (introduced by RLField segments and by
    ``many=True`` on the outer field).

    ``inner_select_related`` / ``inner_prefetch_related`` are applied to
    the bulk ``filter(pk__in=…)`` that hydrates ``target_model``.

    ``custom_queryset`` (when set) replaces the default ``_default_manager``
    as the base for that filter.
    """

    field_name: str
    field_many: bool
    json_path: Tuple[str, ...]
    target_model: Type[models.Model]
    rel_type: str
    inner_select_related: Tuple[str, ...] = ()
    inner_prefetch_related: Tuple[Any, ...] = ()
    custom_queryset: Optional[models.QuerySet] = None
    original_lookup: str = ""


# ---------------------------------------------------------------------------
# Planner: lookup string  →  StructuredPrefetchPlan (or None to passthrough).
# ---------------------------------------------------------------------------


def _resolve_structured_field(model: Type[models.Model], head: str):
    """Return the ``StructuredJSONField`` named ``head`` on ``model`` or None."""
    from structured.fields import StructuredJSONField

    try:
        field = model._meta.get_field(head)
    except Exception:
        return None
    return field if isinstance(field, StructuredJSONField) else None


def _walk_schema(
    schema_cls: Any,
    segments: Sequence[str],
) -> Tuple[Tuple[str, ...], RelInfo, Tuple[str, ...]]:
    """
    Walk ``segments`` inside a structured schema's relation graph until a
    terminal Django relation (FK or QS) is reached.

    Returns ``(json_path, rel_info, remaining)`` where ``remaining`` is
    the slice of segments past the terminal relation — these become
    inner Django lookups on the target model.
    """
    rels: Dict[str, RelInfo] = schema_cls._cache_engine.__related_fields__
    json_path: List[str] = []
    for i, seg in enumerate(segments):
        info = rels.get(seg)
        if info is None:
            raise FieldError(
                f"Cannot resolve {seg!r} inside structured schema "
                f"{schema_cls.__name__}: no such structured relation."
            )
        if info.type in (RelInfo.FKField, RelInfo.QSField):
            json_path.append(seg)
            return tuple(json_path), info, tuple(segments[i + 1:])
        if info.type == RelInfo.RIField:
            json_path.append(seg)
        elif info.type == RelInfo.RLField:
            json_path.extend((seg, "*"))
        else:  # pragma: no cover
            raise FieldError(
                f"Unknown structured relation kind {info.type!r} for "
                f"{seg!r} in {schema_cls.__name__}."
            )
        schema_cls = info.model
        rels = schema_cls._cache_engine.__related_fields__

    raise FieldError(
        "Structured prefetch path ended on a nested schema rather than a "
        "Django relation. Append a relation name (a ForeignKey or QuerySet "
        "field) to the lookup."
    )


def _plan_lookup(
    model: Type[models.Model],
    lookup: Union[str, Prefetch],
) -> Optional[StructuredPrefetchPlan]:
    """
    Return a :class:`StructuredPrefetchPlan` for ``lookup`` if it crosses a
    structured field on ``model``, or ``None`` to defer to Django.
    """
    custom_queryset: Optional[models.QuerySet] = None
    to_attr: Optional[str] = None
    if isinstance(lookup, Prefetch):
        path = lookup.prefetch_through
        custom_queryset = lookup.queryset
        to_attr = getattr(lookup, "to_attr", None)
    else:
        path = lookup

    segments = path.split(LOOKUP_SEP)
    head = segments[0]
    field = _resolve_structured_field(model, head)
    if field is None:
        return None

    if to_attr:
        raise FieldError(
            f"Prefetch(to_attr=…) is not supported across structured field "
            f"{head!r}: results are always attached inside the JSON document."
        )

    if len(segments) == 1:
        raise FieldError(
            f"Lookup {path!r} only names the structured field; append a "
            f"relation inside its schema, e.g. {head}__fk_field."
        )

    json_path, rel_info, remaining = _walk_schema(field.orig_schema, segments[1:])

    if rel_info.model._meta.abstract:
        raise FieldError(
            f"Cannot prefetch through abstract relation "
            f"{rel_info.model.__name__!r}: concrete model resolution requires "
            f"inspecting each row's JSON discriminator. Open an issue if you "
            f"need this."
        )

    if remaining:
        if custom_queryset is not None:
            # Django semantics: a Prefetch(queryset=...) applies to the
            # terminal segment. Carry the custom queryset down as an inner
            # Prefetch and clear it at the outer step.
            inner_prefetch: Tuple[Any, ...] = (
                Prefetch(LOOKUP_SEP.join(remaining), queryset=custom_queryset),
            )
            custom_queryset = None
        else:
            inner_prefetch = (LOOKUP_SEP.join(remaining),)
    else:
        inner_prefetch = ()

    if field.many:
        json_path = ("*",) + json_path

    return StructuredPrefetchPlan(
        field_name=head,
        field_many=field.many,
        json_path=json_path,
        target_model=rel_info.model,
        rel_type=rel_info.type,
        inner_select_related=(),
        inner_prefetch_related=inner_prefetch,
        custom_queryset=custom_queryset,
        original_lookup=path,
    )


# ---------------------------------------------------------------------------
# Executor: run the planned prefetches against a list of outer rows.
# ---------------------------------------------------------------------------


def _gather_pks(
    node: Any,
    json_path: Sequence[str],
    pk_attname: str,
) -> List[Any]:
    """
    Walk raw JSON at ``json_path`` and collect PKs at the leaf.

    Handles ``'*'`` segments (list iteration), and terminal nodes that
    are scalars, dicts (FK shape), or lists (QSField shape).
    """
    if node is None:
        return []
    if not json_path:
        if isinstance(node, list):
            return [pk for item in node for pk in _extract_terminal(item, pk_attname)]
        return _extract_terminal(node, pk_attname)

    head, *rest = json_path
    if head == "*":
        if not isinstance(node, list):
            return []
        return [pk for item in node for pk in _gather_pks(item, rest, pk_attname)]
    if isinstance(node, dict):
        return _gather_pks(node.get(head), rest, pk_attname)
    return []


def _extract_terminal(node: Any, pk_attname: str) -> List[Any]:
    if node is None:
        return []
    if isinstance(node, dict):
        # wire-format dicts key the pk as 'id' regardless of the attname
        pk = node.get(pk_attname, node.get("id"))
        return [pk] if pk is not None else []
    return [node]


def _merge_plans(
    plans: Sequence[StructuredPrefetchPlan],
) -> List[StructuredPrefetchPlan]:
    """
    Collapse plans that share ``(field_name, json_path, target_model)``.

    String lookups union; conflicting ``custom_queryset`` instances on the
    same site raise. This mirrors Django's behaviour for repeated
    ``prefetch_related`` calls referencing the same lookup.
    """
    grouped: Dict[Tuple[str, Tuple[str, ...], Type[models.Model]], List[StructuredPrefetchPlan]] = (
        defaultdict(list)
    )
    for plan in plans:
        grouped[(plan.field_name, plan.json_path, plan.target_model)].append(plan)

    merged: List[StructuredPrefetchPlan] = []
    for group in grouped.values():
        custom: Optional[models.QuerySet] = None
        for p in group:
            if p.custom_queryset is None:
                continue
            if custom is None:
                custom = p.custom_queryset
            elif custom is not p.custom_queryset:
                raise FieldError(
                    f"Conflicting Prefetch querysets for "
                    f"{p.original_lookup!r}: two Prefetch objects target "
                    f"the same structured site with different querysets."
                )

        # dict.fromkeys preserves first-seen order across the merged group.
        sr = tuple(dict.fromkeys(x for p in group for x in p.inner_select_related))
        pr = tuple(dict.fromkeys(x for p in group for x in p.inner_prefetch_related))
        head = group[0]
        merged.append(
            StructuredPrefetchPlan(
                field_name=head.field_name,
                field_many=head.field_many,
                json_path=head.json_path,
                target_model=head.target_model,
                rel_type=head.rel_type,
                inner_select_related=sr,
                inner_prefetch_related=pr,
                custom_queryset=custom,
                original_lookup=head.original_lookup,
            )
        )
    return merged


def _field_cache_engine(model: Type[models.Model], field_name: str):
    """Cache engine for the schema of ``model.field_name`` (a
    ``StructuredJSONField``), or ``None``.

    Used to enumerate every relation a document hydrates by reusing the
    engine's own extraction — which already handles nested / list / union /
    abstract shapes — instead of re-walking the schema by hand.
    """
    field = _resolve_structured_field(model, field_name)
    if field is None:
        return None
    schema = getattr(field, "orig_schema", None)
    return getattr(schema, "_cache_engine", None)


def _plan_is_enriched(plan: StructuredPrefetchPlan) -> bool:
    """Whether ``plan`` carries fetch hints (custom queryset / select_related /
    inner prefetch).

    NB: ``custom_queryset is not None`` — never ``bool(queryset)``, which would
    evaluate the queryset against the DB just to test it.
    """
    return bool(
        plan.custom_queryset is not None
        or plan.inner_select_related
        or plan.inner_prefetch_related
    )


def _seed_planned_paths(
    rows: Sequence[models.Model],
    merged: Sequence[StructuredPrefetchPlan],
) -> Dict[Type[models.Model], Dict[Any, models.Model]]:
    """Fetch each planned path (with its hints) into a fresh seed mapping.

    Enriching plans are seeded first and never overwritten by a plainer fetch of
    the same instance — two plans may target the same model (e.g. an FK field
    and a QuerySet field on one document both pointing at Author).
    """
    seed: Dict[Type[models.Model], Dict[Any, models.Model]] = defaultdict(dict)
    for plan in sorted(merged, key=lambda p: not _plan_is_enriched(p)):
        pk_attname = plan.target_model._meta.pk.attname
        pks: Set[Any] = set()
        for row in rows:
            raw = row.__dict__.get(plan.field_name)
            if raw is not None:
                pks.update(_gather_pks(raw, plan.json_path, pk_attname))
        if not pks:
            continue
        base = (
            plan.custom_queryset.all()
            if plan.custom_queryset is not None
            else plan.target_model._default_manager.all()
        )
        qs = base.filter(pk__in=pks)
        if plan.inner_select_related:
            qs = qs.select_related(*plan.inner_select_related)
        if plan.inner_prefetch_related:
            qs = qs.prefetch_related(*plan.inner_prefetch_related)
        for obj in qs:
            seed[plan.target_model].setdefault(obj.pk, obj)
    return seed


def _seed_document_relations(
    rows: Sequence[models.Model],
    merged: Sequence[StructuredPrefetchPlan],
    seed: Dict[Type[models.Model], Dict[Any, models.Model]],
) -> None:
    """Seed every *other* relation the documents hydrate, in place.

    Accessing a structured field resolves the whole document, not just the
    planned path. Reuse the field's own cache engine to enumerate the document's
    relations from the raw JSON, then batch-fetch — one query per model — the
    PKs the planned fetches did not already cover (plain: these carry no hints).
    Without this, those relations fall back to a per-row ``filter(pk__in=…)``.
    """
    model_cls = type(rows[0])
    extra_pks: Dict[Type[models.Model], Set[Any]] = defaultdict(set)
    for field_name in {plan.field_name for plan in merged}:
        engine = _field_cache_engine(model_cls, field_name)
        if engine is None:
            continue
        for row in rows:
            raw = row.__dict__.get(field_name)
            if raw is None:
                continue
            for model, tuples in engine.get_all_fk_data(raw).items():
                for _path, value in tuples:
                    if isinstance(value, (list, tuple, set, frozenset)):
                        extra_pks[model].update(v for v in value if v is not None)
                    elif value is not None:
                        extra_pks[model].add(value)

    for model, pks in extra_pks.items():
        missing = {pk for pk in pks if pk not in seed.get(model, {})}
        if not missing:
            continue
        for obj in model._default_manager.filter(pk__in=missing):
            seed[model].setdefault(obj.pk, obj)


def _execute_structured_prefetch(
    rows: Sequence[models.Model],
    plans: Sequence[StructuredPrefetchPlan],
) -> None:
    """
    Build a complete seed, then force structured-field validation under it.

    1. :func:`_seed_planned_paths` — bulk-fetch each planned path with its hints
       (gathering PKs from each row's raw JSON, read directly from ``__dict__``
       to avoid triggering the structured-field descriptor).
    2. :func:`_seed_document_relations` — accessing a structured field hydrates
       the WHOLE document, not just the planned path, so batch-fetch the
       remaining relation PKs too. Without this a relation sharing the document
       with the prefetched path falls back to a per-row ``filter(pk__in=…)`` —
       an N+1 that only stays hidden when the planned path's PKs happen to cover
       it.
    3. Push the seed onto the thread-local stack and force-evaluate the
       structured fields. The cache engine consults the seed before issuing its
       own queries, so every prefetched instance is reused.
    """
    if not rows or not plans:
        return

    merged = _merge_plans(plans)
    seed = _seed_planned_paths(rows, merged)
    _seed_document_relations(rows, merged, seed)

    fields_touched = {plan.field_name for plan in merged}
    if not seed:
        # Nothing to seed (all paths were empty); still trigger validation so
        # the queryset behaves consistently with stock prefetch_related.
        for field_name in fields_touched:
            for row in rows:
                getattr(row, field_name, None)
        return

    with _SeedScope(seed):
        for field_name in fields_touched:
            for row in rows:
                getattr(row, field_name, None)


# ---------------------------------------------------------------------------
# QuerySet / Manager.
# ---------------------------------------------------------------------------


class StructuredQuerySetMixin:
    """
    Mix this into a custom ``QuerySet`` subclass to gain structured-field
    awareness in ``prefetch_related`` / ``select_related``.

    Most users should reach for :class:`StructuredQuerySet` or
    :class:`StructuredManager` instead.
    """

    def select_related(self, *fields):  # type: ignore[override]
        for lookup in fields:
            if not isinstance(lookup, str):
                continue
            head = lookup.split(LOOKUP_SEP, 1)[0]
            if _resolve_structured_field(self.model, head) is not None:
                raise FieldError(
                    f"select_related() cannot traverse the structured JSON "
                    f"field {head!r}: JSON values are not SQL-joinable. Use "
                    f"prefetch_related() instead, optionally with "
                    f"Prefetch(queryset=...select_related(...)) for inner "
                    f"relations."
                )
        return super().select_related(*fields)

    def prefetch_related(self, *lookups):  # type: ignore[override]
        if lookups == (None,):
            qs = super().prefetch_related(None)
            qs._structured_prefetch_plans = ()
            return qs

        passthrough: List[Any] = []
        plans: List[StructuredPrefetchPlan] = []
        for lookup in lookups:
            plan = _plan_lookup(self.model, lookup)
            if plan is None:
                passthrough.append(lookup)
            else:
                plans.append(plan)

        qs = super().prefetch_related(*passthrough) if passthrough else self._chain()
        if plans:
            existing = tuple(getattr(qs, "_structured_prefetch_plans", ()))
            qs._structured_prefetch_plans = existing + tuple(plans)
        return qs

    def _clone(self, **kwargs):  # type: ignore[override]
        clone = super()._clone(**kwargs)
        plans = getattr(self, "_structured_prefetch_plans", ())
        if plans:
            clone._structured_prefetch_plans = plans
        # Intentionally do not carry the "already executed" sentinel —
        # clones are fresh, unevaluated querysets.
        return clone

    def _fetch_all(self):  # type: ignore[override]
        already_done = getattr(self, "_structured_prefetched", False)
        super()._fetch_all()
        if already_done:
            return
        plans = getattr(self, "_structured_prefetch_plans", ())
        if plans and self._result_cache:
            _execute_structured_prefetch(self._result_cache, plans)
            self._structured_prefetched = True


class StructuredQuerySet(StructuredQuerySetMixin, models.QuerySet):
    """Drop-in :class:`~django.db.models.QuerySet` with structured-field awareness."""


class StructuredManager(models.Manager.from_queryset(StructuredQuerySet)):
    """
    Manager that returns :class:`StructuredQuerySet` instances.

    Attach to any model with a :class:`~structured.fields.StructuredJSONField`::

        class Article(models.Model):
            structured_data = StructuredJSONField(schema=ArticleSchema)
            objects = StructuredManager()

    In most cases you do *not* need to attach this explicitly — see
    :func:`_promote_managers` below. Auto-install can be disabled with
    ``STRUCTURED_FIELD = {"AUTO_INSTALL_MANAGER": False}``.
    """


# ---------------------------------------------------------------------------
# Auto-install: promote managers on any model owning a StructuredJSONField.
#
# Django fires ``class_prepared`` after all fields and managers (including
# the auto-created ``objects = Manager()`` for models that declare none)
# have been wired up. We listen for that signal and:
#
#   1. Swap each local manager's ``_queryset_class`` for a synthesized
#      subclass that mixes :class:`StructuredQuerySetMixin` on top of the
#      original — preserving any custom manager methods or queryset
#      methods the user defined.
#   2. If no manager — local or inherited — is structured-aware after
#      step 1, make the model's default manager structured-aware. When that
#      manager is *inherited* (e.g. ``objects`` from an abstract base, which
#      never appears in ``local_managers``), it's cloned locally with the
#      mixin layered on — preserving its class, name and methods — rather
#      than overwritten with a bare :class:`StructuredManager` that would
#      drop them. Only when there's nothing to inherit do we install a plain
#      StructuredManager. This handles child models that add a structured
#      field to a parent that didn't have one.
#
# The synthesis is memoised so ``isinstance`` checks and pickling stay
# stable across calls. Promotion is a no-op for managers that are
# already structured-aware.
# ---------------------------------------------------------------------------


_promoted_qs_classes: Dict[Type[models.QuerySet], Type[models.QuerySet]] = {}


def _promote_qs_class(qs_cls: Type[models.QuerySet]) -> Type[models.QuerySet]:
    """
    Return a QuerySet class that mixes :class:`StructuredQuerySetMixin`
    on top of ``qs_cls``. Memoised by source class so repeated calls
    return the same synthesized type — keeping ``isinstance`` and pickle
    behaviour stable.
    """
    if issubclass(qs_cls, StructuredQuerySetMixin):
        return qs_cls
    cached = _promoted_qs_classes.get(qs_cls)
    if cached is not None:
        return cached
    promoted = type(
        f"Structured{qs_cls.__name__}",
        (StructuredQuerySetMixin, qs_cls),
        {"__module__": qs_cls.__module__},
    )
    _promoted_qs_classes[qs_cls] = promoted
    return promoted


def _model_owns_structured_field(model_cls: Type[models.Model]) -> bool:
    """
    True if this model exposes any :class:`StructuredJSONField` — locally
    declared or inherited from a concrete parent.

    Uses ``_meta.fields`` rather than ``get_fields()`` because the app
    registry isn't ready at ``class_prepared`` time, and ``get_fields``
    needs it for the reverse-relation tree. ``_meta.fields`` is built
    during ``ModelBase.__new__`` (before the signal fires) and includes
    inherited concrete fields.
    """
    from structured.fields import StructuredJSONField

    return any(isinstance(f, StructuredJSONField) for f in model_cls._meta.fields)


def _promote_managers(sender: Type[models.Model], **kwargs: Any) -> None:
    """
    ``class_prepared`` handler. See module docstring for the rationale.

    Skips abstract and proxy models — they don't own DB tables of their
    own, so manager promotion is handled (or unnecessary) on the
    concrete class.
    """
    from structured.settings import settings

    if not settings.STRUCTURED_AUTO_INSTALL_MANAGER:
        return
    if sender._meta.abstract or sender._meta.proxy:
        return
    if not _model_owns_structured_field(sender):
        return

    for manager in sender._meta.local_managers:
        original = manager._queryset_class
        promoted = _promote_qs_class(original)
        if promoted is not original:
            manager._queryset_class = promoted

    # If neither a local nor an inherited manager carries the mixin, make the
    # model's default manager structured-aware. A model that *inherits* its
    # manager from a (possibly abstract) base has no local manager for the loop
    # above to promote — Django surfaces inherited managers only as ephemeral
    # copies in ``_meta.managers``, never in ``local_managers``. Rather than
    # overwrite ``objects`` with a bare StructuredManager — which would discard
    # the inherited manager's own methods (e.g. a custom ``.public()``) — clone
    # that manager locally with the mixin layered onto its queryset, preserving
    # its class, name and methods. Only when there's genuinely nothing to
    # inherit do we fall back to a plain StructuredManager.
    if not any(
        issubclass(m._queryset_class, StructuredQuerySetMixin)
        for m in sender._meta.managers
    ):
        if not _promote_inherited_default_manager(sender):
            mgr = StructuredManager()
            mgr.auto_created = True
            mgr.contribute_to_class(sender, "objects")


def _promote_inherited_default_manager(sender: Type[models.Model]) -> bool:
    """Re-install the model's inherited default manager *locally* with
    :class:`StructuredQuerySetMixin` mixed onto its queryset class.

    Preserves the inherited manager's class, name and methods, so a model that
    gains a :class:`~structured.fields.StructuredJSONField` keeps the manager it
    inherited (e.g. one exposing ``.public()``) instead of having it replaced by
    a bare :class:`StructuredManager`. Returns ``False`` when there is no
    inherited manager worth promoting, leaving the caller to install a plain
    StructuredManager.
    """
    meta = sender._meta
    name = meta.default_manager_name or "objects"
    inherited = meta.managers_map.get(name)
    if inherited is None:
        # No manager under the expected name — fall back to the resolved default
        # (lowest depth/creation-counter), e.g. a model whose only manager is
        # custom-named.
        managers = meta.managers
        if not managers:
            return False
        inherited = managers[0]
    promoted_qs = _promote_qs_class(inherited._queryset_class)
    if promoted_qs is inherited._queryset_class:
        return False  # already structured-aware; nothing to do
    promoted_mgr = copy.copy(inherited)
    promoted_mgr._queryset_class = promoted_qs
    promoted_mgr.auto_created = True
    promoted_mgr.contribute_to_class(sender, inherited.name)
    return True


# Connect once at module load. ``class_prepared`` is dispatched per model
# during ``ModelBase.__new__``; since ``structured/__init__.py`` imports
# this module, the handler is in place before any user model with a
# StructuredJSONField finishes preparation.
from django.db.models.signals import class_prepared  # noqa: E402

class_prepared.connect(_promote_managers, dispatch_uid="structured.orm._promote_managers")
