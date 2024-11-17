import pytest


# Django admin custom widget is rendered correctly
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget(setting_fixture, admin_client):
    response = admin_client.get("/admin/test_module/testmodel/add/")
    assert response.status_code == 200
    assert "structured_data_editor" in str(response.content)
    assert "id_structured_data" in str(response.content)
    resources = [
        "libs/fontawesome/css/all.min.css",
        "css/structured-field-form.min.css",
        "libs/jsoneditor/jsoneditor.js",
        "js/structured-field-form.js",
    ]
    for resource in resources:
        assert resource in str(response.content)


# Django admin custom widget can create simple data (name, age fields)
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_create_simple_data(setting_fixture, admin_client):
    response = admin_client.post(
        "/admin/test_module/testmodel/add/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30}',
            "structured_data_list": '[{"name": "John Doe", "age": 30}]',
        },
    )
    assert response.status_code == 302
    assert response.url == "/admin/test_module/testmodel/"
    response = admin_client.get("/admin/test_module/testmodel/1/change/")
    assert response.status_code == 200
    assert "John Doe" in str(response.content)
    assert "30" in str(response.content)


# Django admin custom widget can create nested data (name, age, child fields)
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_create_nested_data(setting_fixture, admin_client):
    response = admin_client.post(
        "/admin/test_module/testmodel/add/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25}}',
            "structured_data_list": '[{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25}}]',
        },
    )
    assert response.status_code == 302
    assert response.url == "/admin/test_module/testmodel/"
    response = admin_client.get("/admin/test_module/testmodel/1/change/")
    assert response.status_code == 200
    assert "John Doe" in str(response.content)
    assert "30" in str(response.content)
    assert "Jane Doe" in str(response.content)
    assert "25" in str(response.content)


# Django admin custom widget can create and then update data (name, age, child fields)
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_update_nested_data(setting_fixture, admin_client):
    response = admin_client.post(
        "/admin/test_module/testmodel/add/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25}}',
            "structured_data_list": '[{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25}}]',
        },
    )
    assert response.status_code == 302
    assert response.url == "/admin/test_module/testmodel/"
    response = admin_client.get("/admin/test_module/testmodel/1/change/")
    assert response.status_code == 200
    assert "John Doe" in str(response.content)
    assert "30" in str(response.content)
    assert "Jane Doe" in str(response.content)
    assert "25" in str(response.content)
    response = admin_client.post(
        "/admin/test_module/testmodel/1/change/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 26}}',
            "structured_data_list": '[{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 26}}]',
        },
    )
    assert response.status_code == 302
    assert response.url == "/admin/test_module/testmodel/"
    response = admin_client.get("/admin/test_module/testmodel/1/change/")
    assert response.status_code == 200
    assert "John Doe" in str(response.content)
    assert "30" in str(response.content)
    assert "Jane Doe" in str(response.content)
    assert "26" in str(response.content)


# Django admin custom widget can create fk and qs fields
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_create_fk_qs_fields(setting_fixture, admin_client):
    from tests.app.test_module.models import SimpleRelationModel
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in ["test1", "test2"]]
    )
    response = admin_client.post(
        "/admin/test_module/testmodel/add/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30, "fk_field": 1, "qs_field": [1, 2]}',
            "structured_data_list": '[{"name": "John Doe", "age": 30, "fk_field": 1, "qs_field": [1, 2]}]',
        },
    )
    assert response.status_code == 302
    assert response.url == "/admin/test_module/testmodel/"
    response = admin_client.get("/admin/test_module/testmodel/1/change/")
    assert response.status_code == 200
    assert "John Doe" in str(response.content)
    assert "30" in str(response.content)
    assert "test1" in str(response.content)
    assert "test2" in str(response.content)


# Django admin custom widget can create nested data with fk and qs fields
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_create_nested_fk_qs_fields(setting_fixture, admin_client):
    from tests.app.test_module.models import SimpleRelationModel
    SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in ["test1", "test2"]]
    )
    response = admin_client.post(
        "/admin/test_module/testmodel/add/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25, "fk_field": 1, "qs_field": [1, 2]}}',
            "structured_data_list": '[{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25, "fk_field": 1, "qs_field": [1, 2]}}]',
        },
    )
    assert response.status_code == 302
    assert response.url == "/admin/test_module/testmodel/"
    response = admin_client.get("/admin/test_module/testmodel/1/change/")
    assert response.status_code == 200
    assert "John Doe" in str(response.content)
    assert "30" in str(response.content)
    assert "Jane Doe" in str(response.content)
    assert "25" in str(response.content)
    assert "test1" in str(response.content)
    assert "test2" in str(response.content)
