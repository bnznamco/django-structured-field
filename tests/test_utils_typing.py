from typing_extensions import get_args, get_origin
import pytest

# Test structured.utils.typing
@pytest.mark.django_db
@pytest.mark.parametrize("setting_fixture", ["cache_enabled", "cache_disabled", "shared_cache"], indirect=True)
def test_utils_typing(setting_fixture):
    from structured.utils.typing import find_model_type_from_args, get_type
    from tests.app.test_module.models import TestSchema, SimpleRelationModel
    from typing import Union
    from structured.cache.engine import CacheEnabledModel
    names = ["test1", "test2", "test3"]
    SimpleRelationModel.objects.bulk_create([SimpleRelationModel(name=name) for name in names])
    model_instance = TestSchema(name="test", age=20, fk_field=SimpleRelationModel.objects.first(), qs_field=SimpleRelationModel.objects.all())
    for field_name, field in model_instance.model_fields.items():
        annotation = field.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if field_name == "child":
            assert origin == Union
            assert find_model_type_from_args(args, model_instance, CacheEnabledModel) == TestSchema
        elif field_name == "childs":
            assert origin == list
            assert find_model_type_from_args(args, model_instance, CacheEnabledModel) == TestSchema
        elif field_name == "fk_field":
            assert get_type(annotation) == SimpleRelationModel
        elif field_name == "qs_field":
            assert get_type(annotation) == SimpleRelationModel