from tests.app.test_module.models import TestModel, TestSchema
import pytest


@pytest.mark.django_db
def test_structured_field():
    instance = TestModel.objects.create(structured_data={"name": "John", "age": 42})
    assert instance.structured_data.name == "John"
    assert instance.structured_data.age == 42


# create an instance of TestModel with structured_data as a valid TestSchema object
@pytest.mark.django_db
def test_valid_test_schema_object():
    schema = TestSchema(name="John", age=25)
    instance = TestModel(structured_data=schema)
    assert instance.structured_data == schema


# Can access fields of nested structured_data in TestModelz
@pytest.mark.django_db
def test_nested_structured_field():
    schema = TestSchema(name="John", age=25)
    nested_schema = TestSchema(name="Alice", age=10, child=schema)
    instance = TestModel.objects.create(structured_data=nested_schema)
    assert instance.structured_data.name == "Alice"
    assert instance.structured_data.age == 10
    assert instance.structured_data.child.name == "John"
    assert instance.structured_data.child.age == 25
