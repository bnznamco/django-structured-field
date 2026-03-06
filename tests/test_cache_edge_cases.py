import pytest
import threading


# --- Edge Case #1/#5: Signal handler leak ---
# Per-request Cache instances should NOT connect to Django signals.
# Only ThreadSafeCache should connect signals.

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_per_request_cache_no_signal_leak(cache_setting_fixture):
    """Per-request Cache instances should not register signal handlers."""
    from django.db.models.signals import post_save, pre_delete
    from structured.cache.cache import Cache

    initial_save_count = len(post_save.receivers)
    initial_delete_count = len(pre_delete.receivers)

    # Create multiple Cache instances (simulating multiple validations)
    caches = [Cache() for _ in range(10)]

    # Signal receiver count should NOT grow
    assert len(post_save.receivers) == initial_save_count
    assert len(pre_delete.receivers) == initial_delete_count

    # Caches should still work for storage
    del caches


# --- Edge Case #4: _flush_model string lookup ---

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["shared_cache"], indirect=True)
def test_flush_model_by_string_name(cache_setting_fixture):
    """Flushing cache by model string name should work correctly."""
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache import get_global_cache

    global_cache = get_global_cache()
    global_cache.flush()

    # Populate some cache data
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(5)]
    )
    model_list = list(SimpleRelationModel.objects.all())
    global_cache.set(model_list)

    assert len(global_cache[SimpleRelationModel]) == 5

    # Flush by string name
    global_cache.flush(model="SimpleRelationModel")

    # Cache for that model should be empty
    assert not global_cache.get(SimpleRelationModel)


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_flush_model_by_string_name_basic_cache(cache_setting_fixture):
    """Flushing basic Cache by model string name should work correctly."""
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache.cache import Cache

    cache = Cache()

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(5)]
    )
    model_list = list(SimpleRelationModel.objects.all())
    cache.set(model_list)

    assert len(cache[SimpleRelationModel]) == 5

    cache.flush(model="SimpleRelationModel")

    assert not cache.get(SimpleRelationModel)


# --- Edge Case #9: RelInfo.model mutation ---

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_abstract_fk_does_not_mutate_relinfo(cache_setting_fixture):
    """Processing abstract FK should not permanently mutate the shared RelInfo model."""
    from tests.app.test_module.models import (
        ChildModel1, ChildModel2, TestModel, TestSchema,
    )
    from structured.settings import settings
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        from structured.cache import get_global_cache
        get_global_cache().flush()

    child1 = ChildModel1.objects.create(common_field="c1", child_field="f1")
    child2 = ChildModel2.objects.create(common_field="c2", child_field="f2")

    # Create with ChildModel1 as abstract FK
    obj1 = TestModel.objects.create(
        title="test1",
        structured_data={"name": "Alice", "age": 10, "abstract_fk": child1},
    )
    obj1.refresh_from_db()
    assert obj1.structured_data.abstract_fk == child1

    # Create with ChildModel2 — should NOT be affected by the previous resolution
    obj2 = TestModel.objects.create(
        title="test2",
        structured_data={"name": "Bob", "age": 20, "abstract_fk": child2},
    )
    obj2.refresh_from_db()
    assert obj2.structured_data.abstract_fk == child2

    # Re-read obj1 — should still resolve to ChildModel1
    obj1.refresh_from_db()
    assert obj1.structured_data.abstract_fk == child1
    assert isinstance(obj1.structured_data.abstract_fk, ChildModel1)


# --- Edge Case #3: QS _result_cache consistency ---

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "shared_cache"], indirect=True)
def test_queryset_cache_ordering_preserved(cache_setting_fixture):
    """QuerySet from cache should preserve the original PK ordering."""
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    from structured.settings import settings
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        from structured.cache import get_global_cache
        get_global_cache().flush()

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(10)]
    )
    model_list = list(SimpleRelationModel.objects.all())

    # Deliberately reverse order
    reversed_list = list(reversed(model_list))
    data = TestSchema(name="Alice", age=10, qs_field=reversed_list)

    obj = TestModel.objects.create(title="test", structured_data=data)
    obj.refresh_from_db()

    qs = obj.structured_data.qs_field
    result_pks = [item.pk for item in qs]
    expected_pks = [item.pk for item in reversed_list]
    assert result_pks == expected_pks


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "shared_cache"], indirect=True)
def test_queryset_cache_handles_missing_pks(cache_setting_fixture):
    """QuerySet retrieval should handle PKs missing from cache by falling back to DB."""
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    from structured.settings import settings
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        from structured.cache import get_global_cache
        get_global_cache().flush()

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(5)]
    )
    model_list = list(SimpleRelationModel.objects.all())

    data = TestSchema(name="Alice", age=10, qs_field=model_list)
    obj = TestModel.objects.create(title="test", structured_data=data)
    obj.refresh_from_db()

    # All items should be retrievable
    qs = obj.structured_data.qs_field
    assert qs.count() == 5


# --- Edge Case #7: ThreadSafeCache thread safety ---

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["shared_cache"], indirect=True)
def test_thread_safe_cache_concurrent_writes(cache_setting_fixture):
    """ThreadSafeCache should handle concurrent writes without errors."""
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache import get_global_cache

    global_cache = get_global_cache()
    global_cache.flush()

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(100)]
    )
    model_list = list(SimpleRelationModel.objects.all())

    errors = []

    def write_to_cache(items):
        try:
            for item in items:
                global_cache.set(item)
        except Exception as e:
            errors.append(e)

    # Spawn multiple threads writing to the same cache
    threads = []
    chunk_size = 10
    for i in range(0, len(model_list), chunk_size):
        chunk = model_list[i:i + chunk_size]
        t = threading.Thread(target=write_to_cache, args=(chunk,))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent writes produced errors: {errors}"
    assert len(global_cache[SimpleRelationModel]) == 100


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["shared_cache"], indirect=True)
def test_thread_safe_cache_concurrent_flush_and_write(cache_setting_fixture):
    """ThreadSafeCache should handle concurrent flush+write without errors."""
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache import get_global_cache

    global_cache = get_global_cache()
    global_cache.flush()

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(50)]
    )
    model_list = list(SimpleRelationModel.objects.all())
    global_cache.set(model_list)

    errors = []

    def flush_cache():
        try:
            global_cache.flush()
        except Exception as e:
            errors.append(e)

    def write_to_cache():
        try:
            global_cache.set(model_list)
        except Exception as e:
            errors.append(e)

    # Run flush and write concurrently
    threads = [
        threading.Thread(target=flush_cache),
        threading.Thread(target=write_to_cache),
        threading.Thread(target=flush_cache),
        threading.Thread(target=write_to_cache),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent operations produced errors: {errors}"


# --- Edge Case #2: _process_fk/qs_field ValueWithCache early return ---

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "shared_cache"], indirect=True)
def test_double_validation_does_not_crash(cache_setting_fixture):
    """Re-validating already-cached data should not crash or corrupt state."""
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    from structured.settings import settings
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        from structured.cache import get_global_cache
        get_global_cache().flush()

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(5)]
    )
    model_list = list(SimpleRelationModel.objects.all())

    data = TestSchema(name="Alice", age=10, fk_field=model_list[0], qs_field=model_list)
    obj = TestModel.objects.create(title="test", structured_data=data)

    # First access triggers validation + cache
    obj.refresh_from_db()
    assert obj.structured_data.fk_field == model_list[0]

    # Second access from same instance should work
    obj.refresh_from_db()
    assert obj.structured_data.fk_field == model_list[0]
    assert obj.structured_data.qs_field.count() == 5


# --- ValueWithCache partial QS cache hit & FK no cache ---

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_value_with_cache_qs_partial_hit(cache_setting_fixture):
    """Test QuerySet retrieve when some PKs are cached and some are not."""
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache.cache import Cache, ValueWithCache

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(5)]
    )
    model_list = list(SimpleRelationModel.objects.all())

    cache = Cache()
    # Only cache first 2 items
    for obj in model_list[:2]:
        cache[SimpleRelationModel][obj.pk] = obj

    all_pks = [obj.pk for obj in model_list]
    vwc = ValueWithCache(cache, SimpleRelationModel, all_pks)
    result = vwc.retrieve()

    # Should return all 5 items from cache + DB
    assert result.count() == 5
    # Cache should now contain all items
    assert len(cache[SimpleRelationModel]) == 5


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_value_with_cache_fk_no_cache(cache_setting_fixture):
    """Test FK retrieve when there's no cache entry for the model."""
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache.cache import Cache, ValueWithCache

    obj = SimpleRelationModel.objects.create(name="test")
    cache = Cache()
    # Don't populate cache for SimpleRelationModel

    vwc = ValueWithCache(cache, SimpleRelationModel, obj.pk)
    result = vwc.retrieve()

    assert result is not None
    assert result.pk == obj.pk


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_value_with_cache_qs_no_cache(cache_setting_fixture):
    """Test QuerySet retrieve when there's no cache at all for the model."""
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache.cache import Cache, ValueWithCache

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(3)]
    )
    model_list = list(SimpleRelationModel.objects.all())
    all_pks = [obj.pk for obj in model_list]

    cache = Cache()
    # No cache populated for SimpleRelationModel

    vwc = ValueWithCache(cache, SimpleRelationModel, all_pks)
    result = vwc.retrieve()

    assert result.count() == 3


# --- _resolve_abstract_model error paths ---

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_resolve_abstract_model_raises_on_pk_only(cache_setting_fixture):
    """Passing an int/str PK for an abstract model should raise ValueError."""
    from structured.cache.engine import CacheEngine
    from tests.app.test_module.models import AbstractModel

    engine = CacheEngine(related_fields={})
    with pytest.raises(ValueError, match="Cannot retrieve abstract models"):
        engine._resolve_abstract_model(42, AbstractModel)


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_resolve_abstract_model_raises_on_string_pk(cache_setting_fixture):
    """Passing a string PK for an abstract model should raise ValueError."""
    from structured.cache.engine import CacheEngine
    from tests.app.test_module.models import AbstractModel

    engine = CacheEngine(related_fields={})
    with pytest.raises(ValueError, match="Cannot retrieve abstract models"):
        engine._resolve_abstract_model("some-pk", AbstractModel)
