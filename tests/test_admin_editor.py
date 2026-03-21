import pytest
import json


# Django admin custom widget is rendered correctly
@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget(cache_setting_fixture, admin_client):
    response = admin_client.get("/admin/test_module/testmodel/add/")
    assert response.status_code == 200
    assert "structured_data_editor" in str(response.content)
    assert "id_structured_data" in str(response.content)
    resources = [
        "https://bnznamco.github.io/structured-widget-editor/latest/structured-widget-editor.iife.js",
        "js/structured-field-init.js",
    ]
    for resource in resources:
        assert resource in str(response.content)


# Django admin custom widget can create simple data (name, age fields)
@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_create_simple_data(cache_setting_fixture, admin_client):
    response = admin_client.post(
        "/admin/test_module/testmodel/add/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30}',
            "structured_data_list": '[{"name": "John Doe", "age": 30}]',
            "structured_data_union": '{"data": {"name": "John Doe", "age": 30, "type": "schema1"}}',
            "structured_data_recursive": '{"child_model": null}',
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
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_create_nested_data(cache_setting_fixture, admin_client):
    response = admin_client.post(
        "/admin/test_module/testmodel/add/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25}}',
            "structured_data_list": '[{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25}}]',
            "structured_data_union": '{"data": {"name": "John Doe", "age": 30, "type": "schema1"}}',
            "structured_data_recursive": '{"child_model": null}',
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
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_update_nested_data(cache_setting_fixture, admin_client):
    response = admin_client.post(
        "/admin/test_module/testmodel/add/",
        {
            "title": "Content",
            "structured_data": '{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25}}',
            "structured_data_list": '[{"name": "John Doe", "age": 30, "child": {"name": "Jane Doe", "age": 25}}]',
            "structured_data_union": '{"data": {"name": "John Doe", "age": 30, "type": "schema1"}}',
            "structured_data_recursive": '{"child_model": null}',
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
            "structured_data_union": '{"data": {"name": "John Doe", "age": 30, "type": "schema1"}}',
            "structured_data_recursive": '{"child_model": null}',
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
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_create_fk_qs_fields(cache_setting_fixture, admin_client):
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
            "structured_data_union": '{"data": {"name": "John Doe", "age": 30, "fk_field": 1, "qs_field": [1, 2], "type": "schema1"}}',
            "structured_data_recursive": '{"child_model": null}',
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
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_admin_custom_widget_create_nested_fk_qs_fields(cache_setting_fixture, admin_client):
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
            "structured_data_union": '{"data": {"name": "John Doe", "age": 30, "fk_field": 1, "qs_field": [1, 2], "type": "schema1"}}',
            "structured_data_recursive": '{"child_model": null}',
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


# --- StructuredJSONFormField coverage ---

@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_form_field_validate_schema_invalid(cache_setting_fixture):
    """StructuredJSONFormField.validate_schema should raise ValidationError on invalid data."""
    from django.forms import ValidationError
    from structured.widget.fields import StructuredJSONFormField
    from tests.app.test_module.models import TestSchema

    form_field = StructuredJSONFormField(schema=TestSchema)
    with pytest.raises(ValidationError):
        form_field.validate_schema({"name": 123, "age": "invalid"})


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_form_field_validate_schema_none(cache_setting_fixture):
    """StructuredJSONFormField.validate_schema should return None for None."""
    from structured.widget.fields import StructuredJSONFormField
    from tests.app.test_module.models import TestSchema

    form_field = StructuredJSONFormField(schema=TestSchema)
    result = form_field.validate_schema(None)
    assert result is None


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_form_field_prepare_value_list(cache_setting_fixture):
    """StructuredJSONFormField.prepare_value should handle list of models."""
    from structured.widget.fields import StructuredJSONFormField
    from tests.app.test_module.models import TestSchema

    form_field = StructuredJSONFormField(schema=TestSchema)
    schemas = [TestSchema(name="A", age=1), TestSchema(name="B", age=2)]
    result = form_field.prepare_value(schemas)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "A"
