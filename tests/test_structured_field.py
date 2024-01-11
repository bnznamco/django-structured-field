from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
import pytest, json


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


# Can create a TestSchema object with a ForeignKey field
@pytest.mark.django_db
def test_foreign_key_field():
    fk_instance = SimpleRelationModel.objects.create(name="test")
    instance = TestModel.objects.create(
        title="test",
        structured_data={"name": "John", "age": 42, "fk_field": fk_instance},
    )
    assert instance.structured_data.name == "John"
    assert instance.structured_data.age == 42
    assert instance.structured_data.fk_field == fk_instance


# Can create a TestSchema object with a QuerySet field
@pytest.mark.django_db
def test_queryset_field():
    names = ["test1", "test2", "test3", "test4", "test5"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names]
    )
    instance = TestModel.objects.create(
        title="test",
        structured_data={
            "name": "John",
            "age": 42,
            "qs_field": SimpleRelationModel.objects.filter(name__in=names),
        },
    )
    assert instance.structured_data.name == "John"
    assert instance.structured_data.age == 42
    assert instance.structured_data.qs_field.count() == len(names)


# TestSchema with QuerySet field mantains the order of the given QuerySet
@pytest.mark.django_db
def test_queryset_field_order():
    names = ["test1", "test2", "test3", "test4", "test5"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names]
    )
    instance = TestModel.objects.create(
        title="test",
        structured_data={
            "name": "John",
            "age": 42,
            "qs_field": SimpleRelationModel.objects.filter(name__in=names).order_by(
                "name"
            ),
        },
    )
    assert instance.structured_data.name == "John"
    assert instance.structured_data.age == 42
    assert instance.structured_data.qs_field.first().name == names[0]
    assert instance.structured_data.qs_field.last().name == names[-1]
    assert json.dumps(
        list(
            instance.structured_data.qs_field.values_list("name", flat=True).order_by(
                "name"
            )
        )
    ) == json.dumps(names)


# Can create nested TestSchema objects with a ForeignKey field
@pytest.mark.django_db
def test_nested_foreign_key_field():
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


# Can create nested TestSchema objects with a QuerySet field
@pytest.mark.django_db
def test_nested_queryset_field():
    names1 = ["test1", "test2", "test3", "test4", "test5"]
    names2 = ["test6", "test7", "test8", "test9", "test10"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names1 + names2]
    )
    child_data = TestSchema(
        name="John",
        age=25,
        qs_field=SimpleRelationModel.objects.filter(name__in=names2),
    )
    data = TestSchema(
        name="Alice",
        age=10,
        qs_field=SimpleRelationModel.objects.filter(name__in=names1),
        child=child_data,
    )
    instance = TestModel.objects.create(title="test", structured_data=data)
    assert instance.structured_data.name == "Alice"
    assert instance.structured_data.age == 10
    assert instance.structured_data.qs_field.count() == len(names1)
    assert instance.structured_data.child.name == "John"
    assert instance.structured_data.child.age == 25
    assert instance.structured_data.child.qs_field.count() == len(names2)


# Heavy nested TestSchema object with a ForeignKey field hits database only once
@pytest.mark.django_db
def test_heavy_nested_foreign_key_field():
    from django.conf import settings
    from django.db import connection
    from django.db import reset_queries


    settings.DEBUG = True # enable debug mode to count db calls
    
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i}") for i in range(100)]
    ) 
    
    model_list = list(SimpleRelationModel.objects.all()) 
    
    child_data1 = TestSchema(name="John", age=25, fk_field=model_list[10])
    child_data2 = TestSchema(name="John", age=25, fk_field=model_list[23], child=child_data1)
    child_data3 = TestSchema(name="John", age=25, fk_field=model_list[51], child=child_data2)
    child_data4 = TestSchema(name="John", age=25, fk_field=model_list[77],child=child_data3)
    child_data5 = TestSchema(name="John", age=25, fk_field=model_list[99], child=child_data4)
    data = TestSchema(name="Alice", age=10, fk_field=model_list[0], child=child_data5)
    
    TestModel.objects.create(title="test", structured_data=data) 

    # reset connection queries
    reset_queries()
    # get instance from database
    instance = TestModel.objects.first()
    assert len(connection.queries) == 1
    assert instance.structured_data.fk_field.name == "test0"
    assert instance.structured_data.child.fk_field.name == "test99"
    assert instance.structured_data.child.child.fk_field.name == "test77"
    assert instance.structured_data.child.child.child.fk_field.name == "test51"
    assert instance.structured_data.child.child.child.child.fk_field.name == "test23"
    assert instance.structured_data.child.child.child.child.child.fk_field.name == "test10"
    assert len(connection.queries) == 2
    
    settings.DEBUG = False # disable debug mode
    
    
