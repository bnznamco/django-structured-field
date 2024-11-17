import pytest


# Heavy nested TestSchema object with a ForeignKey field hits database only once
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_heavy_nested_foreign_key_field(setting_fixture, django_assert_num_queries):
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    from structured.settings import settings
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        from structured.cache import get_global_cache
        get_global_cache().flush()
    
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(100)]
    )

    model_list = list(SimpleRelationModel.objects.all().order_by("name"))

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
        instance = TestModel.objects.first()
    n_query = 0 if settings.STRUCTURED_FIELD_SHARED_CACHE else 1
    if not settings.STRUCTURED_FIELD_CACHE_ENABLED:
        n_query = 6
    with django_assert_num_queries(n_query) as operation:
        assert instance.structured_data.fk_field.name == "test0000"
        assert instance.structured_data.child.fk_field.name == "test0099"
        assert instance.structured_data.child.child.fk_field.name == "test0077"
        assert instance.structured_data.child.child.child.fk_field.name == "test0051"
        assert (
            instance.structured_data.child.child.child.child.fk_field.name == "test0023"
        )
        assert (
            instance.structured_data.child.child.child.child.child.fk_field.name
            == "test0010"
        )
        if n_query == 1:
            assert (
                'SELECT "test_module_simplerelationmodel"'
                in operation.captured_queries[0]["sql"]
            )

# Heavy nested TestSchema object with a Queryset field hits database only once
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_heavy_nested_queryset_field(setting_fixture, django_assert_num_queries):
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    from structured.settings import settings
    
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        from structured.cache import get_global_cache
        get_global_cache().flush()

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(100)]
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

    with django_assert_num_queries(1):
        instance = TestModel.objects.first()
    n_query = 0 if settings.STRUCTURED_FIELD_SHARED_CACHE else 1
    if not settings.STRUCTURED_FIELD_CACHE_ENABLED:
        n_query = 6
    with django_assert_num_queries(n_query) as operation:
        assert instance.structured_data.qs_field.count() == 10
        assert instance.structured_data.child.qs_field.count() == 10
        assert instance.structured_data.child.child.qs_field.count() == 10
        assert instance.structured_data.child.child.child.qs_field.count() == 10
        assert instance.structured_data.child.child.child.child.qs_field.count() == 10
        assert (
            instance.structured_data.child.child.child.child.child.qs_field.count()
            == 10
        )
        if n_query == 1:
            assert (
                'SELECT "test_module_simplerelationmodel"'
                in operation.captured_queries[0]["sql"]
            )


@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_sequence_child(setting_fixture, django_assert_num_queries):
    from tests.app.test_module.models import SimpleRelationModel, TestModel, TestSchema
    from structured.settings import settings
    
    if settings.STRUCTURED_FIELD_SHARED_CACHE:
        from structured.cache import get_global_cache
        get_global_cache().flush()

    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=f"test{i:04d}") for i in range(100)]
    )
    model_list = list(SimpleRelationModel.objects.all())
    
    child_data1 = TestSchema(name="John1", age=25, fk_field=model_list[22])
    child_data2 = TestSchema(name="John2", age=25, fk_field=model_list[33])
    child_data3 = TestSchema(name="John3", age=25, fk_field=model_list[44])
    child_data4 = TestSchema(name="John4", age=25, fk_field=model_list[55])
    child_data5 = TestSchema(name="John5", age=25, fk_field=model_list[66])
    data = TestSchema(name="Alice", age=10, fk_field=model_list[0], childs=[child_data1, child_data2, child_data3, child_data4, child_data5])
    
    TestModel.objects.create(title="test", structured_data=data)
    with django_assert_num_queries(1):
        instance = TestModel.objects.first()
    n_query = 0 if settings.STRUCTURED_FIELD_SHARED_CACHE else 1
    if not settings.STRUCTURED_FIELD_CACHE_ENABLED:
        n_query = 6
    with django_assert_num_queries(n_query) as operation:
        assert instance.structured_data.fk_field.name == "test0000"
        assert instance.structured_data.childs[0].fk_field.name == "test0022"
        assert instance.structured_data.childs[1].fk_field.name == "test0033"
        assert instance.structured_data.childs[2].fk_field.name == "test0044"
        assert instance.structured_data.childs[3].fk_field.name == "test0055"
        assert instance.structured_data.childs[4].fk_field.name == "test0066"
        if n_query == 1:
            assert (
                'SELECT "test_module_simplerelationmodel"'
                in operation.captured_queries[0]["sql"]
            )