import pytest, random


# Test structured_field/search_model/<model> endpoint search
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_search_model(setting_fixture, admin_client):
    from tests.app.test_module.models import SimpleRelationModel
    response = admin_client.get(
        "/structured_field/search_model/test_module.SimpleRelationModel/"
    )
    body = response.json()
    items = body.get("items", [])
    assert response.status_code == 200
    assert items == []
    names = ["test1", "test2", "test3", "test4", "test5"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names]
    )
    response = admin_client.get(
        "/structured_field/search_model/test_module.SimpleRelationModel/?_q=test"
    )
    body = response.json()
    items = body.get("items", [])
    assert response.status_code == 200
    assert len(items) == 5


# Test structured_field/search_model/<model> endpoint search with _pk
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_search_model_pk(setting_fixture, admin_client):
    from tests.app.test_module.models import SimpleRelationModel
    names = ["test1", "test2", "test3", "test4", "test5"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names]
    )
    model_list = list(SimpleRelationModel.objects.all())

    index = random.randint(0, len(model_list) - 1)

    response = admin_client.get(
        f"/structured_field/search_model/test_module.SimpleRelationModel/?_q=_pk={model_list[index].pk}"
    )
    body = response.json()
    items = body.get("items", [])
    assert response.status_code == 200
    assert len(items) == 1
    assert items[0]["id"] == model_list[index].pk
    assert items[0]["name"] == model_list[index].name


# Test structured_field/search_model/<model> endpoint search with _pk__in
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_search_model_pks(setting_fixture, admin_client):
    from tests.app.test_module.models import SimpleRelationModel
    names = ["test1", "test2", "test3", "test4", "test5"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names]
    )
    model_list = list(SimpleRelationModel.objects.all())

    random_indexes = random.sample(range(len(model_list)), 2)   

    response = admin_client.get(
        f"/structured_field/search_model/test_module.SimpleRelationModel/?_q=_pk__in={','.join([str(model_list[i].pk) for i in random_indexes])}"
    )
    body = response.json()
    items = body.get("items", [])
    assert response.status_code == 200
    assert len(items) == 2
    assert model_list[random_indexes[0]].pk in [item["id"] for item in items]
    assert model_list[random_indexes[1]].pk in [item["id"] for item in items]
    assert model_list[random_indexes[0]].name in [item["name"] for item in items]
    assert model_list[random_indexes[1]].name in [item["name"] for item in items]
    
    
# Test structured_field/search_model/<model> with __all__ search
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_search_model_all(setting_fixture, admin_client):
    from tests.app.test_module.models import SimpleRelationModel
    names = ["test1", "test2", "test3", "test4", "test5"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names]
    )
    response = admin_client.get(
        f"/structured_field/search_model/test_module.SimpleRelationModel/"
    )
    body = response.json()
    items = body.get("items", [])
    assert response.status_code == 200
    assert len(items) == 5
    assert all([item["name"] in names for item in items])
    assert all([item["id"] in [model.pk for model in SimpleRelationModel.objects.all()] for item in items])


# Test structured_field/search_model/<model> with wrong method
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_search_model_wrong_method(setting_fixture, admin_client):
    response = admin_client.post(
        "/structured_field/search_model/test_module.SimpleRelationModel/"
    )
    body = response.json()
    assert response.status_code == 405
    assert body["error"] == "Method Not Allowed"
    
# Test structured_field/search_model/<model> with wrong model
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_search_model_wrong_model(setting_fixture, admin_client):
    response = admin_client.get(
        "/structured_field/search_model/test_module.SimpleRelationModelWrong/"
    )
    assert response.status_code == 404

