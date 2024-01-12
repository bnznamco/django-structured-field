import pytest


# Django admin custom widget is rendered correctly
@pytest.mark.django_db
def test_admin_custom_widget(admin_client):
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
