import pytest


@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_custom_serializer_field(setting_fixture):
    from tests.app.test_module.models import TestModel, SimpleRelationModel
    rel_models = SimpleRelationModel.objects.bulk_create(
        [SimpleRelationModel(name=name) for name in ["test1", "test2"]]
    )
    instance = TestModel.objects.create(
        title="test", structured_data={"name": "John", "age": 42, "custom_serializer_fk": rel_models[0], "custom_serializer_qs": rel_models}
    )
    serialized_data = instance.structured_data.model_dump()
    assert serialized_data["custom_serializer_fk"]["id"] == 1
    assert serialized_data["custom_serializer_fk"]["custom"] == "👻 I'm custom!"
    assert len(serialized_data["custom_serializer_qs"]) == 2
    assert serialized_data["custom_serializer_qs"][0]["id"] == 1
    assert serialized_data["custom_serializer_qs"][0]["custom"] == "👻 I'm custom!"
    assert serialized_data["custom_serializer_qs"][1]["id"] == 2
    assert serialized_data["custom_serializer_qs"][1]["custom"] == "👻 I'm custom!"