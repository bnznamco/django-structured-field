import pytest, json


# Can create a TestSchema object with a QuerySet field
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_queryset_field(setting_fixture):
    from tests.app.test_module.models import SimpleRelationModel, TestModel 
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
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_queryset_field_order(setting_fixture):
    from tests.app.test_module.models import SimpleRelationModel, TestModel
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


# Can create nested TestSchema objects with a QuerySet field
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_nested_queryset_field(setting_fixture):
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
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


# Can edit a QuerySet and save the changes to the database
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_queryset_field_edit(setting_fixture):
    from tests.app.test_module.models import SimpleRelationModel, TestModel
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
    assert instance.structured_data.qs_field.count() == len(names)
    names = ["test62", "test37", "test78"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names]
    )
    instance.structured_data.qs_field = SimpleRelationModel.objects.filter(
        name__in=names
    )
    instance.save()
    assert instance.structured_data.qs_field.count() == len(names)
    assert set(instance.structured_data.qs_field.values_list("name", flat=True)) == set(
        names
    )
