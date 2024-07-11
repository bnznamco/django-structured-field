import pytest, random


# Test structured_field/search_model/<model> endpoint search
@pytest.mark.django_db
def test_search_model(admin_client):
    from tests.app.test_module.models import SimpleRelationModel
    response = admin_client.get(
        "/structured_field/search_model/test_module.SimpleRelationModel/"
    )
    body = response.json()
    assert response.status_code == 200
    assert body == []
    names = ["test1", "test2", "test3", "test4", "test5"]
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in names]
    )
    response = admin_client.get(
        "/structured_field/search_model/test_module.SimpleRelationModel/?_q=test"
    )
    body = response.json()
    assert response.status_code == 200
    assert len(body) == 5


# Test structured_field/search_model/<model> endpoint search with _pk
@pytest.mark.django_db
def test_search_model_pk(admin_client):
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
    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["id"] == model_list[index].pk
    assert body[0]["name"] == model_list[index].name


# Test structured_field/search_model/<model> endpoint search with _pk__in
@pytest.mark.django_db
def test_search_model_pks(admin_client):
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
    assert response.status_code == 200
    assert len(body) == 2
    assert model_list[random_indexes[0]].pk in [item["id"] for item in body]
    assert model_list[random_indexes[1]].pk in [item["id"] for item in body]
    assert model_list[random_indexes[0]].name in [item["name"] for item in body]
    assert model_list[random_indexes[1]].name in [item["name"] for item in body]