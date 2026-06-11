import pytest
import json


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_structured_field(cache_setting_fixture):
    from tests.app.test_module.models import TestModel
    instance = TestModel.objects.create(
        title="test", structured_data={"name": "John", "age": 42}
    )
    assert instance.structured_data.name == "John"
    assert instance.structured_data.age == 42


# create an instance of TestModel with structured_data as a valid TestSchema object
@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_valid_test_schema_object(cache_setting_fixture):
    from tests.app.test_module.models import TestModel, TestSchema
    schema = TestSchema(name="John", age=25)
    instance = TestModel(title="test", structured_data=schema)
    assert instance.structured_data == schema


# Can access fields of nested structured_data in TestModel
@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_nested_structured_field(cache_setting_fixture):
    from tests.app.test_module.models import TestModel, TestSchema
    child_data = TestSchema(name="John", age=25)
    data = TestSchema(name="Alice", age=10, child=child_data)
    instance = TestModel.objects.create(title="test", structured_data=data)
    assert instance.structured_data.name == "Alice"
    assert instance.structured_data.age == 10
    assert instance.structured_data.child.name == "John"
    assert instance.structured_data.child.age == 25


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_structured_field_validate_invalid_data(cache_setting_fixture):
    """StructuredJSONField.validate should raise ValidationError for invalid data."""
    from django.core.exceptions import ValidationError
    from tests.app.test_module.models import TestModel

    field = TestModel._meta.get_field("structured_data")
    with pytest.raises(ValidationError):
        field.validate({"name": 123, "age": "not_a_number"}, None)


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_structured_field_get_prep_value_list(cache_setting_fixture):
    """get_prep_value should handle list of models for many=True."""
    from tests.app.test_module.models import TestModel, TestSchema

    field = TestModel._meta.get_field("structured_data_list")
    schemas = [
        TestSchema(name="John", age=25),
        TestSchema(name="Jane", age=30),
    ]
    result = field.get_prep_value(schemas)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 2


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_structured_field_get_db_prep_value(cache_setting_fixture):
    """get_db_prep_value should work the same as get_prep_value."""
    from tests.app.test_module.models import TestModel, TestSchema

    field = TestModel._meta.get_field("structured_data")
    schema = TestSchema(name="John", age=25)
    result = field.get_db_prep_value(schema, connection=None, prepared=False)
    parsed = json.loads(result)
    assert parsed["name"] == "John"


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_structured_field_raw_data_property(cache_setting_fixture):
    """Test raw data property getter/setter/deleter."""
    from tests.app.test_module.models import TestModel

    data = {"name": "Test", "age": 10}
    obj = TestModel.objects.create(title="test", structured_data=data)
    obj.refresh_from_db()

    # Access raw data
    raw = obj.structured_data_raw
    assert raw is not None


# None handling: get_prep_value and the descriptor must pass NULL through
@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_structured_field_none_handling(cache_setting_fixture, caplog):
    import logging
    from tests.app.test_module.models import TestModel

    field = TestModel._meta.get_field("structured_data")
    assert field.get_prep_value(None) is None
    assert field.get_db_prep_value(None, connection=None) is None

    obj = TestModel(title="t")
    obj.__dict__["structured_data"] = None  # simulate a NULL column value
    with caplog.at_level(logging.WARNING, logger="structured.fields"):
        assert obj.structured_data is None
        assert obj.structured_data is None  # repeated access stays silent
    assert not [r for r in caplog.records if "Error validating" in r.getMessage()]


# On validation failure the descriptor must return PRISTINE raw data,
# not the dict mutated in place by the cache engine
@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_descriptor_returns_unpolluted_raw_on_validation_failure(cache_setting_fixture):
    from structured.cache.cache import ValueWithCache
    from tests.app.test_module.models import TestModel, SimpleRelationModel

    rel = SimpleRelationModel.objects.create(name="rel")
    obj = TestModel(title="t")
    # invalid data (age must be int) that ALSO contains a relation pk,
    # so the cache engine splices a ValueWithCache before validation fails
    obj.__dict__["structured_data"] = {
        "name": "x",
        "age": "not-an-int",
        "fk_field": rel.pk,
    }
    value = obj.structured_data
    assert isinstance(value, dict)
    assert value["fk_field"] == rel.pk
    assert not isinstance(value.get("fk_field"), ValueWithCache)
    # repeated access stays consistent
    assert obj.structured_data["fk_field"] == rel.pk


# Regression: <field>_raw must be per-instance, not field-level shared state
@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled"], indirect=True)
def test_structured_field_raw_data_is_per_instance(cache_setting_fixture):
    """Every instance must see ITS OWN raw data, not the last loaded row's."""
    from tests.app.test_module.models import TestModel

    TestModel.objects.create(title="a", structured_data={"name": "alpha", "age": 1})
    TestModel.objects.create(title="b", structured_data={"name": "beta", "age": 2})

    first, second = list(TestModel.objects.order_by("pk"))
    assert first.structured_data_raw["name"] == "alpha"
    assert second.structured_data_raw["name"] == "beta"
    assert first.structured_data_raw is not second.structured_data_raw


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_structured_field_raw_data_survives_validation_unpolluted(cache_setting_fixture):
    """Raw data read AFTER field access must be the pre-validation JSON,
    without ValueWithCache placeholders spliced in by the cache engine."""
    from structured.cache.cache import ValueWithCache
    from tests.app.test_module.models import TestModel, SimpleRelationModel

    rel = SimpleRelationModel.objects.create(name="rel")
    TestModel.objects.create(
        title="t",
        structured_data={"name": "x", "age": 1, "fk_field": rel.pk},
    )
    obj = TestModel.objects.get(title="t")
    _ = obj.structured_data  # triggers validation (mutates the raw dict in place)
    raw = obj.structured_data_raw
    assert not isinstance(raw.get("fk_field"), ValueWithCache)
    # the persisted wire format for an FK is the minimal {id, name, model} dict
    assert raw["fk_field"]["id"] == rel.pk


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_structured_field_raw_data_invalidated_on_assignment(cache_setting_fixture):
    """Assigning new raw data must refresh what <field>_raw returns."""
    from tests.app.test_module.models import TestModel

    obj = TestModel.objects.create(title="t", structured_data={"name": "old", "age": 1})
    obj = TestModel.objects.get(pk=obj.pk)
    _ = obj.structured_data  # validate + stash
    assert obj.structured_data_raw["name"] == "old"
    obj.structured_data = {"name": "new", "age": 2}
    assert obj.structured_data_raw["name"] == "new"

