from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
import pytest


# Heavy nested TestSchema object with a ForeignKey field hits database only once
@pytest.mark.django_db
def test_heavy_nested_foreign_key_field():
    from django.conf import settings
    from django.db import connection, reset_queries

    settings.DEBUG = True  # enable debug mode to count db calls

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i}") for i in range(100)]
    )

    model_list = list(SimpleRelationModel.objects.all())

    child_data1 = TestSchema(name="John", age=25, fk_field=model_list[10])
    child_data2 = TestSchema(
        name="John", age=25, fk_field=model_list[23], child=child_data1
    )
    child_data3 = TestSchema(
        name="John", age=25, fk_field=model_list[51], child=child_data2
    )
    child_data4 = TestSchema(
        name="John", age=25, fk_field=model_list[77], child=child_data3
    )
    child_data5 = TestSchema(
        name="John", age=25, fk_field=model_list[99], child=child_data4
    )
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
    assert (
        instance.structured_data.child.child.child.child.child.fk_field.name == "test10"
    )
    assert len(connection.queries) == 2

    settings.DEBUG = False  # disable debug mode


# Heavy nested TestSchema object with a Queryset field hits database only once
@pytest.mark.django_db
def test_heavy_nested_queryset_field():
    from django.conf import settings
    from django.db import connection, reset_queries

    settings.DEBUG = True  # enable debug mode to count db calls

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i}") for i in range(100)]
    )

    model_list = list(SimpleRelationModel.objects.all())

    child_data1 = TestSchema(name="John", age=25, qs_field=model_list[10:20])
    child_data2 = TestSchema(
        name="John", age=25, qs_field=model_list[20:30], child=child_data1
    )
    child_data3 = TestSchema(
        name="John", age=25, qs_field=model_list[30:40], child=child_data2
    )
    child_data4 = TestSchema(
        name="John", age=25, qs_field=model_list[40:50], child=child_data3
    )
    child_data5 = TestSchema(
        name="John", age=25, qs_field=model_list[50:60], child=child_data4
    )
    data = TestSchema(
        name="Alice", age=10, qs_field=model_list[0:10], child=child_data5
    )

    TestModel.objects.create(title="test", structured_data=data)

    # reset connection queries
    reset_queries()
    # get instance from database
    instance = TestModel.objects.first()
    assert len(connection.queries) == 1
    assert instance.structured_data.qs_field.count() == 10
    assert instance.structured_data.child.qs_field.count() == 10
    assert instance.structured_data.child.child.qs_field.count() == 10
    assert instance.structured_data.child.child.child.qs_field.count() == 10
    assert instance.structured_data.child.child.child.child.qs_field.count() == 10
    assert instance.structured_data.child.child.child.child.child.qs_field.count() == 10
    assert len(connection.queries) == 2

    settings.DEBUG = False  # disable debug mode
