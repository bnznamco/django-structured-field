import pytest


@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["shared_cache"], indirect=True)
def test_shared_cache_engine(setting_fixture, django_assert_num_queries):
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    from structured.cache import get_global_cache

    global_cache = get_global_cache()
    global_cache.flush()
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(100)]
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
    with django_assert_num_queries(1):
        TestModel.objects.first()

    for child in [child_data1, child_data2, child_data3, child_data4, child_data5]:
        assert global_cache[SimpleRelationModel][
            child.fk_field.pk
        ] == SimpleRelationModel.objects.get(pk=child.fk_field.pk)

    instance_to_update = SimpleRelationModel.objects.get(pk=child_data2.fk_field.pk)
    instance_to_update.name = "changed"
    instance_to_update.save()
    assert global_cache[SimpleRelationModel][child_data2.fk_field.pk].name == "changed"
    instance_to_update.delete()
    assert child_data2.fk_field.pk not in global_cache[SimpleRelationModel]
    SimpleRelationModel.objects.all().delete()
    assert not global_cache[SimpleRelationModel]


@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["shared_cache"], indirect=True)
def test_shared_cache_flush_method(setting_fixture):
    from tests.app.test_module.models import SimpleRelationModel, TestSchema
    from structured.cache import get_global_cache

    global_cache = get_global_cache()
    global_cache.flush()
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(100)]
    )
    model_list = list(SimpleRelationModel.objects.all())
    TestSchema(name="John", age=25, qs_field=model_list)
    for model in model_list:
        assert global_cache[SimpleRelationModel][model.pk] == model
    global_cache.flush([m for m in model_list if m.pk % 2 == 0])
    for model in model_list:
        if model.pk % 2 == 0:
            assert model.pk not in global_cache[SimpleRelationModel]
        else:
            assert global_cache[SimpleRelationModel][model.pk] == model
    global_cache.flush(SimpleRelationModel.objects.filter(pk__gt=50))
    for model in model_list:
        if model.pk > 50 or model.pk % 2 == 0:
            assert model.pk not in global_cache[SimpleRelationModel]
        else:
            assert global_cache[SimpleRelationModel][model.pk] == model
    global_cache.flush(model=SimpleRelationModel)
    assert not global_cache[SimpleRelationModel]


@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["shared_cache"], indirect=True)
def test_cache_set_method(setting_fixture):
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache import get_global_cache

    global_cache = get_global_cache()
    global_cache.flush()
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(100)]
    )
    model_list = list(SimpleRelationModel.objects.all())
    global_cache.set(model_list[0])
    assert global_cache[SimpleRelationModel][model_list[0].pk] == model_list[0]
    global_cache.set(model_list[10:20])
    for i, model in enumerate(model_list):
        if 10 <= i < 20 or model.pk == model_list[0].pk:
            assert global_cache[SimpleRelationModel][model.pk] == model
        else:
            assert model.pk not in global_cache[SimpleRelationModel]


@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["shared_cache"], indirect=True)
def test_shared_cache_signals(setting_fixture):
    from tests.app.test_module.models import SimpleRelationModel
    from structured.cache import get_global_cache

    global_cache = get_global_cache()
    global_cache.flush()
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(100)]
    )
    model = SimpleRelationModel.objects.order_by("?").first()
    global_cache.set(model)
    assert global_cache[SimpleRelationModel][model.pk] == model
    model.name = "changed"
    model.save()
    assert global_cache[SimpleRelationModel][model.pk].name == "changed"
    model.delete()
    assert model.pk not in global_cache[SimpleRelationModel]
    global_cache.set(SimpleRelationModel.objects.all())
    SimpleRelationModel.objects.filter(pk__lt=10).delete()
    for model in SimpleRelationModel.objects.all():
        if model.pk < 10:
            assert model.pk not in global_cache[SimpleRelationModel]
        else:
            assert global_cache[SimpleRelationModel][model.pk] == model
