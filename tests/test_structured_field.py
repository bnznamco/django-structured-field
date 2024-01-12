from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
import pytest


@pytest.mark.django_db
def test_structured_field():
    instance = TestModel.objects.create(
        title="test", structured_data={"name": "John", "age": 42}
    )
    assert instance.structured_data.name == "John"
    assert instance.structured_data.age == 42


# create an instance of TestModel with structured_data as a valid TestSchema object
@pytest.mark.django_db
def test_valid_test_schema_object():
    schema = TestSchema(name="John", age=25)
    instance = TestModel(title="test", structured_data=schema)
    assert instance.structured_data == schema


# Can access fields of nested structured_data in TestModel
@pytest.mark.django_db
def test_nested_structured_field():
    child_data = TestSchema(name="John", age=25)
    data = TestSchema(name="Alice", age=10, child=child_data)
    instance = TestModel.objects.create(title="test", structured_data=data)
    assert instance.structured_data.name == "Alice"
    assert instance.structured_data.age == 10
    assert instance.structured_data.child.name == "John"
    assert instance.structured_data.child.age == 25

