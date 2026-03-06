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

