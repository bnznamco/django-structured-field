"""
Tests that multiple ``StructuredJSONField``s on the same Django instance
share a single per-instance cache, so a model referenced from more than
one field is fetched only once.

The mechanism: ``StructuredDescriptor.__get__`` lazily attaches a
``Cache`` to the Django instance and passes it via pydantic
``info.context`` to every structured-field validator on that row. The
cache engine reuses it when populating, so overlapping PKs across
fields don't double-fetch.
"""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext


def _simple_relation_queries(captured):
    """Return only the queries that hit SimpleRelationModel."""
    return [q for q in captured if "simplerelationmodel" in q["sql"].lower()]


@pytest.mark.django_db
def test_per_instance_cache_shared_across_multiple_structured_fields():
    """
    Two structured fields on the SAME row, both referencing the SAME
    SimpleRelationModel — only one ``SELECT`` should hit it.

    Baseline (no sharing): two fields → two separate fetches.
    With sharing: the second field finds the row in the per-instance
    cache and skips its filter.
    """
    from tests.app.test_module.models import SimpleRelationModel, TestModel

    related = SimpleRelationModel.objects.create(name="shared")

    structured_data = {
        "name": "main",
        "fk_field": related.pk,
        "qs_field": [related.pk],
        "custom_serializer_fk": related.pk,
        "custom_serializer_qs": [related.pk],
    }
    # ``structured_data_list`` is many=True; same payload for the only item.
    instance = TestModel.objects.create(
        title="t",
        structured_data=structured_data,
        structured_data_list=[structured_data],
    )

    # Round-trip through the DB so descriptors run fresh validation.
    instance = TestModel.objects.get(pk=instance.pk)

    with CaptureQueriesContext(connection) as ctx:
        _ = instance.structured_data.fk_field.name
        _ = instance.structured_data_list[0].fk_field.name

    relation_hits = _simple_relation_queries(ctx.captured_queries)
    assert len(relation_hits) == 1, (
        f"per-instance cache failed to dedupe SimpleRelationModel fetches "
        f"across structured fields: {len(relation_hits)} fetches\n"
        + "\n".join(q["sql"] for q in relation_hits)
    )


@pytest.mark.django_db
def test_two_separate_instances_do_not_share_cache():
    """
    The cache is scoped to a Django instance — two distinct rows must
    not share. This pins the boundary so a future refactor doesn't
    accidentally make caches process-wide (which would re-introduce the
    SHARED-mode invalidation pitfalls without the signal handlers that
    SHARED mode wires up).
    """
    from tests.app.test_module.models import SimpleRelationModel, TestModel

    related = SimpleRelationModel.objects.create(name="shared-but-not-cached")

    payload = {
        "name": "main",
        "fk_field": related.pk,
        "qs_field": [related.pk],
        "custom_serializer_fk": related.pk,
        "custom_serializer_qs": [related.pk],
    }
    TestModel.objects.create(title="a", structured_data=payload)
    TestModel.objects.create(title="b", structured_data=payload)

    # Two SEPARATE fetches → two SEPARATE instances → no shared cache.
    a = TestModel.objects.get(title="a")
    b = TestModel.objects.get(title="b")

    with CaptureQueriesContext(connection) as ctx:
        _ = a.structured_data.fk_field.name
        _ = b.structured_data.fk_field.name

    relation_hits = _simple_relation_queries(ctx.captured_queries)
    assert len(relation_hits) == 2, (
        f"expected one SimpleRelationModel fetch per distinct instance "
        f"(got {len(relation_hits)}). If this fails, the per-instance "
        f"cache may have become global — check the cache-attach logic."
    )


@pytest.mark.django_db
def test_same_instance_repeated_access_is_idempotent():
    """
    Accessing the same field twice should not re-query — but that's
    handled by the descriptor short-circuit, not the per-instance cache.
    Pin it so the descriptor change doesn't silently regress.
    """
    from tests.app.test_module.models import SimpleRelationModel, TestModel

    related = SimpleRelationModel.objects.create(name="r")
    TestModel.objects.create(
        title="t",
        structured_data={
            "name": "main",
            "fk_field": related.pk,
            "qs_field": [related.pk],
            "custom_serializer_fk": related.pk,
            "custom_serializer_qs": [related.pk],
        },
    )
    instance = TestModel.objects.get(title="t")

    # Prime by accessing once.
    _ = instance.structured_data.fk_field.name

    with CaptureQueriesContext(connection) as ctx:
        _ = instance.structured_data.fk_field.name
        _ = instance.structured_data.fk_field.name

    assert len(ctx.captured_queries) == 0, "\n".join(
        q["sql"] for q in ctx.captured_queries
    )
