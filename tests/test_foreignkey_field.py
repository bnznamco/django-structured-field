import pytest


# Can create a TestSchema object with a ForeignKey field
@pytest.mark.django_db
def test_foreign_key_field():
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    fk_instance = SimpleRelationModel.objects.create(name="test")
    instance = TestModel.objects.create(
        title="test",
        structured_data={"name": "John", "age": 42, "fk_field": fk_instance},
    )
    assert instance.structured_data.name == "John"
    assert instance.structured_data.age == 42
    assert instance.structured_data.fk_field == fk_instance


# Can create nested TestSchema objects with a ForeignKey field
@pytest.mark.django_db
def test_nested_foreign_key_field():
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    fk_instance1 = SimpleRelationModel.objects.create(name="test1")
    fk_instance2 = SimpleRelationModel.objects.create(name="test2")
    child_data = TestSchema(name="John", age=25, fk_field=fk_instance2)
    data = TestSchema(name="Alice", age=10, fk_field=fk_instance1, child=child_data)
    instance = TestModel.objects.create(title="test", structured_data=data)
    assert instance.structured_data.name == "Alice"
    assert instance.structured_data.age == 10
    assert instance.structured_data.fk_field == fk_instance1
    assert instance.structured_data.child.name == "John"
    assert instance.structured_data.child.age == 25
    assert instance.structured_data.child.fk_field == fk_instance2
