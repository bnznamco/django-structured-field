"""
Tests for :class:`structured.orm.StructuredQuerySet` — Django-flavoured
``prefetch_related`` / ``select_related`` across structured JSON paths.

The query-count assertions are the load-bearing part: the feature only
exists to collapse N+1 patterns, so each test pins both behaviour AND
query count.
"""
import pytest
from django.core.exceptions import FieldError
from django.db import connection
from django.db.models import Prefetch
from django.test.utils import CaptureQueriesContext


@pytest.fixture
def authors(db):
    """3 authors, each tied to its own country, with a couple of shared tags."""
    from tests.app.test_module.models import Author, Country, Tag

    countries = [Country.objects.create(name=n) for n in ("Italy", "France", "Spain")]
    tags = [Tag.objects.create(name=n) for n in ("fiction", "non-fiction")]
    authors = []
    for i, country in enumerate(countries):
        a = Author.objects.create(name=f"author-{i}", country=country)
        a.tags.set(tags)
        authors.append(a)
    return authors


@pytest.fixture
def books(authors):
    """5 books, each with a primary author and 2 co-authors drawn from `authors`."""
    from tests.app.test_module.models import BookModel

    return [
        BookModel.objects.create(
            title=f"book-{i}",
            structured_data={
                "title": f"book-{i}",
                "author": authors[i % len(authors)].pk,
                "co_authors": [a.pk for a in authors],
            },
        )
        for i in range(5)
    ]


# ---------------------------------------------------------------------------
# select_related: must refuse to JOIN through a JSON column.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_select_related_through_structured_field_raises():
    from tests.app.test_module.models import BookModel

    with pytest.raises(FieldError, match="cannot traverse the structured JSON field"):
        BookModel.objects.select_related("structured_data__author")


@pytest.mark.django_db
def test_select_related_on_non_structured_field_passes_through():
    """select_related must remain unaffected for non-structured paths."""
    from tests.app.test_module.models import BookModel

    # No structured field named 'title' → goes to Django, which will error on
    # its own terms (non-relation field). We just verify it isn't OUR error.
    with pytest.raises(FieldError) as excinfo:
        list(BookModel.objects.select_related("title"))
    assert "cannot traverse the structured JSON field" not in str(excinfo.value)


# ---------------------------------------------------------------------------
# prefetch_related: query-count assertions.
# ---------------------------------------------------------------------------


def _count_queries(callable_):
    """Run ``callable_`` and return (count, captured) for diagnostic output."""
    with CaptureQueriesContext(connection) as ctx:
        callable_()
    return len(ctx.captured_queries), ctx.captured_queries


@pytest.mark.django_db
def test_prefetch_fk_collapses_inner_fetches_against_baseline(books):
    """
    Concrete proof the optimization is real, not just an upper-bound win.

    With 5 books referencing 3 distinct authors across 3 countries:

    * **baseline** (no prefetch): 11 queries — the cache engine fetches
      authors per-row (5×) and each ``author.country`` access fires its
      own FK query (5×), plus the outer SELECT.
    * **optimized** (``Prefetch(queryset=Author.objects.select_related('country'))``):
      2 queries — one outer SELECT and one bulk Author JOIN-Country.

    The pinned counts make accidental regressions loud; the baseline
    comparison makes the win self-documenting.
    """
    from tests.app.test_module.models import Author, BookModel

    def baseline():
        for book in BookModel.objects.all():
            _ = book.structured_data.author.country.name

    def optimized():
        qs = BookModel.objects.prefetch_related(
            Prefetch(
                "structured_data__author",
                queryset=Author.objects.select_related("country"),
            )
        )
        for book in qs:
            _ = book.structured_data.author.country.name

    baseline_n, _ = _count_queries(baseline)
    optimized_n, optimized_qs = _count_queries(optimized)

    assert baseline_n == 11, f"baseline query count drifted: {baseline_n}"
    assert optimized_n == 2, (
        f"optimized query count drifted: {optimized_n}\n"
        + "\n".join(q["sql"] for q in optimized_qs)
    )
    assert optimized_n < baseline_n, (
        f"prefetch did not reduce query count "
        f"(baseline={baseline_n}, optimized={optimized_n})"
    )


@pytest.mark.django_db
def test_prefetch_fk_bare_chain_against_baseline(books):
    """
    Bare ``prefetch_related("a__b__c")`` semantics: one query per relation
    hop. 5 books / 3 authors / 3 countries:

    * baseline: 11 queries (same as above)
    * optimized: 3 queries (outer + Author bulk + Country bulk)

    This is the case where the user did NOT pass a custom queryset, so
    Country is loaded as a second prefetch hop rather than a JOIN.
    """
    from tests.app.test_module.models import BookModel

    def baseline():
        for book in BookModel.objects.all():
            _ = book.structured_data.author.country.name

    def optimized():
        qs = BookModel.objects.prefetch_related("structured_data__author__country")
        for book in qs:
            _ = book.structured_data.author.country.name

    baseline_n, _ = _count_queries(baseline)
    optimized_n, optimized_qs = _count_queries(optimized)

    assert baseline_n == 11
    assert optimized_n == 3, (
        f"optimized query count drifted: {optimized_n}\n"
        + "\n".join(q["sql"] for q in optimized_qs)
    )
    assert optimized_n < baseline_n


@pytest.mark.django_db
def test_prefetch_qs_collapses_against_baseline(books):
    """
    QSField + inner country prefetch.

    Each book's ``co_authors`` is a QSField pointing at all 3 authors.
    Touching ``co.country.name`` for every co-author on every book:

    * baseline: 21 queries — per-row co_authors fetch + per-author
      country access.
    * optimized: 3 queries — outer + Author bulk + Country bulk.
    """
    from tests.app.test_module.models import BookModel

    def baseline():
        for book in BookModel.objects.all():
            for co in book.structured_data.co_authors:
                _ = co.country.name

    def optimized():
        qs = BookModel.objects.prefetch_related(
            "structured_data__co_authors__country"
        )
        for book in qs:
            for co in book.structured_data.co_authors:
                _ = co.country.name

    baseline_n, _ = _count_queries(baseline)
    optimized_n, optimized_qs = _count_queries(optimized)

    assert baseline_n == 21, f"baseline query count drifted: {baseline_n}"
    assert optimized_n == 3, (
        f"optimized query count drifted: {optimized_n}\n"
        + "\n".join(q["sql"] for q in optimized_qs)
    )
    assert optimized_n < baseline_n


@pytest.mark.django_db
def test_prefetch_related_lookup_passthrough_for_django_relations(books):
    """A lookup that does NOT name a structured field falls back to Django."""
    from tests.app.test_module.models import BookModel

    # `title` is a CharField on the outer model, not a structured field.
    # Django will raise FieldError for prefetch_related on a non-relation —
    # we just confirm we surfaced Django's error, not ours.
    with pytest.raises(Exception) as excinfo:
        list(BookModel.objects.prefetch_related("title"))
    assert "structured" not in str(excinfo.value).lower()


@pytest.mark.django_db
def test_prefetch_related_clone_preserves_plan(books):
    """
    Cloning the queryset (via ``.filter``) must keep structured plans
    AND keep the per-hop query count: outer + Author + Country = 3,
    matching the un-cloned bare-chain case. If the clone dropped the
    plan we'd fall back to the 11-query baseline.
    """
    from tests.app.test_module.models import BookModel

    base = BookModel.objects.prefetch_related("structured_data__author__country")
    filtered = base.filter(title__startswith="book-")

    def run():
        for book in filtered:
            _ = book.structured_data.author.country.name

    n, captured = _count_queries(run)
    assert n == 3, (
        f"clone dropped the structured plan: {n} queries\n"
        + "\n".join(q["sql"] for q in captured)
    )


@pytest.mark.django_db
def test_prefetch_related_none_clears(books):
    """``prefetch_related(None)`` must clear structured plans too."""
    from tests.app.test_module.models import BookModel

    qs = (
        BookModel.objects
        .prefetch_related("structured_data__author__country")
        .prefetch_related(None)
    )
    # Should not raise even though it traverses Author/Country lazily.
    list(qs)


@pytest.mark.django_db
def test_prefetch_unknown_relation_inside_schema_raises():
    from tests.app.test_module.models import BookModel

    with pytest.raises(FieldError, match="no such structured relation"):
        BookModel.objects.prefetch_related("structured_data__nope")


@pytest.mark.django_db
def test_prefetch_only_naming_field_raises():
    from tests.app.test_module.models import BookModel

    with pytest.raises(FieldError, match="only names the structured field"):
        BookModel.objects.prefetch_related("structured_data")


# ---------------------------------------------------------------------------
# Whole-document seeding: accessing a structured field hydrates ALL its
# relations, so the prefetch must seed every relation in the document — not
# just the named path — or the rest falls back to a per-row N+1.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_partial_filter_does_not_n_plus_1_unprefetched_relations(books):
    """A FILTERED subset must not regress: accessing the document hydrates
    ``co_authors`` (a QSField) even though only ``author`` was prefetched. The
    co-authors are batch-fetched once, not per row.

    Without whole-document seeding this was 4 queries for 2 rows and grew with
    the row count; the planned ``author`` path only *coincidentally* covered
    ``co_authors`` when the whole table was loaded.
    """
    from tests.app.test_module.models import Author, BookModel

    # book-0 / book-2 reference authors 1 & 3; author 2 appears only via
    # co_authors, so it is the PK the planned path fails to cover.
    qs = BookModel.objects.filter(title__in=["book-0", "book-2"]).prefetch_related(
        Prefetch(
            "structured_data__author",
            queryset=Author.objects.select_related("country"),
        )
    )

    def run():
        for book in qs:
            _ = book.structured_data.author.country.name      # planned path
            assert all(co.name for co in book.structured_data.co_authors)  # hydrated

    n, captured = _count_queries(run)
    # outer rows + author(+country) + one batched co_authors fetch.
    assert n == 3, (
        f"un-prefetched co_authors N+1'd on a filtered subset: {n} queries\n"
        + "\n".join(q["sql"] for q in captured)
    )


@pytest.mark.django_db
def test_partial_filter_query_count_is_independent_of_row_count(authors):
    """The whole-document seed makes the count O(1) in rows: a 1-row and a
    10-row filtered slice issue the same number of queries (no N+1 tail)."""
    from tests.app.test_module.models import Author, BookModel

    # Fixed primary author across all rows so the planned ``author`` seed never
    # grows; co_authors always references every author, so authors 2 & 3 are
    # only ever reachable via the un-prefetched co_authors path. The query count
    # must then be constant no matter how many rows match.
    for i in range(20):
        BookModel.objects.create(
            title=f"row-{i}",
            structured_data={
                "title": f"row-{i}",
                "author": authors[0].pk,
                "co_authors": [a.pk for a in authors],
            },
        )

    def run(titles):
        qs = BookModel.objects.filter(title__in=titles).prefetch_related(
            Prefetch(
                "structured_data__author",
                queryset=Author.objects.select_related("country"),
            )
        )
        for book in qs:
            _ = book.structured_data.author.country.name
            _ = [co.name for co in book.structured_data.co_authors]

    one, _ = _count_queries(lambda: run(["row-1"]))
    ten, _ = _count_queries(lambda: run([f"row-{i}" for i in range(1, 20, 2)]))
    assert one == ten, f"row count leaked into query count: {one} vs {ten} (N+1)"


@pytest.mark.django_db
def test_two_plans_same_model_do_not_clobber_enriched_instances(books):
    """Two plans targeting the same model (an FK ``author`` with an inner
    ``country`` join + the ``co_authors`` QSField) must not have the plainer
    fetch overwrite the enriched one in the seed. Previously this *added* a
    query (the country prefetch was lost); now it composes cleanly."""
    from tests.app.test_module.models import Author, BookModel

    qs = BookModel.objects.filter(title__in=["book-0", "book-2"]).prefetch_related(
        Prefetch(
            "structured_data__author",
            queryset=Author.objects.select_related("country"),
        ),
        "structured_data__co_authors",
    )

    def run():
        for book in qs:
            _ = book.structured_data.author.country.name

    n, captured = _count_queries(run)
    assert n == 3, (
        f"same-model plans clobbered each other: {n} queries\n"
        + "\n".join(q["sql"] for q in captured)
    )


# ---------------------------------------------------------------------------
# Auto-install: managers are promoted via class_prepared without any
# explicit opt-in in the model body.
# ---------------------------------------------------------------------------


def test_auto_install_promotes_managers_on_structured_models():
    """
    Every model with a ``StructuredJSONField`` should have a
    structured-aware queryset class on its default manager, even when
    the user did not write ``objects = StructuredManager()``.
    """
    from structured.orm import StructuredQuerySetMixin
    from tests.app.test_module.models import (
        ArticleModel,
        BookModel,
        TestModel,
    )

    for model in (TestModel, ArticleModel, BookModel):
        qs_cls = model._meta.local_managers[0]._queryset_class
        assert issubclass(qs_cls, StructuredQuerySetMixin), (
            f"{model.__name__}.objects should expose StructuredQuerySetMixin "
            f"behaviour automatically; got queryset class {qs_cls.__name__!r}."
        )


def test_auto_install_leaves_unrelated_models_alone():
    """
    Models without a StructuredJSONField must keep their original
    queryset class — promotion is opt-in by virtue of using the field.
    """
    from structured.orm import StructuredQuerySetMixin
    from tests.app.test_module.models import Author, Country, Tag

    for model in (Author, Country, Tag):
        qs_cls = model._meta.local_managers[0]._queryset_class
        assert not issubclass(qs_cls, StructuredQuerySetMixin), (
            f"{model.__name__} should not be promoted: it has no "
            f"StructuredJSONField."
        )


def test_auto_install_preserves_inherited_custom_manager():
    """A model that adds a StructuredJSONField to a parent carrying a custom
    manager (inherited from an abstract base, so never in ``local_managers``)
    must KEEP that manager's methods. The auto-install promotes it in place
    instead of overwriting ``objects`` with a bare StructuredManager.
    """
    from structured.orm import StructuredQuerySetMixin
    from tests.app.test_module.models import PublishableBookModel

    mgr = PublishableBookModel.objects
    assert hasattr(mgr, "published"), (
        "inherited .published() was lost — the manager was replaced, not promoted"
    )
    assert issubclass(mgr._queryset_class, StructuredQuerySetMixin), (
        "promoted manager is not structured-aware"
    )


@pytest.mark.django_db
def test_inherited_manager_method_and_structured_prefetch_compose(authors):
    """The promoted inherited manager exposes BOTH its own query method
    (``.published()``) and the structured prefetch optimization."""
    from tests.app.test_module.models import Author, PublishableBookModel

    for i in range(4):
        PublishableBookModel.objects.create(
            title=f"pub-book-{i}",
            is_published=(i % 2 == 0),
            structured_data={
                "title": f"pub-book-{i}",
                "author": authors[i % len(authors)].pk,
                "co_authors": [a.pk for a in authors],
            },
        )

    # 1. The inherited custom method survived promotion and filters correctly.
    published = list(PublishableBookModel.objects.published())
    assert len(published) == 2 and all(b.is_published for b in published)

    # 2. The structured prefetch optimization is available on the same manager
    #    (2 queries: outer rows + one batched author fetch with country joined).
    qs = PublishableBookModel.objects.prefetch_related(
        Prefetch(
            "structured_data__author",
            queryset=Author.objects.select_related("country"),
        )
    )
    with CaptureQueriesContext(connection) as ctx:
        loaded = list(qs)
        names = [b.structured_data.author.country.name for b in loaded]

    assert all(names)
    assert len(ctx.captured_queries) == 2, (
        f"structured prefetch lost on the promoted inherited manager: "
        f"{len(ctx.captured_queries)} queries"
    )


@pytest.mark.django_db
def test_auto_install_works_end_to_end_without_explicit_manager(books):
    """
    The query-count guarantees from earlier tests also hold without any
    explicit ``objects = StructuredManager()`` on the model.
    """
    from tests.app.test_module.models import Author, BookModel

    qs = BookModel.objects.prefetch_related(
        Prefetch(
            "structured_data__author",
            queryset=Author.objects.select_related("country"),
        )
    )

    with CaptureQueriesContext(connection) as ctx:
        loaded = list(qs)
        names = [book.structured_data.author.country.name for book in loaded]

    assert len(ctx.captured_queries) == 2, (
        f"auto-installed manager did not deliver the 2-query optimization: "
        f"{len(ctx.captured_queries)} queries\n"
        + "\n".join(q["sql"] for q in ctx.captured_queries)
    )
    assert all(names)
