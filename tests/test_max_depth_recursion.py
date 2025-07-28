import pytest
from typing import Dict


def recursive_get_child_model(instance: Dict, depth: int):
    if depth == 0:
        return instance or {}
    child_instance = instance.get("child_model", {}).get(
        "structured_data_recursive", None
    )
    return recursive_get_child_model(child_instance, depth - 1)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "recursion_depth_setting_fixture", [0, 1, 2, 3, 4, 5], indirect=True
)
def test_recursion_depth(recursion_depth_setting_fixture):
    from tests.app.test_module.models import TestModel
    from structured.settings import settings

    child4_instance = TestModel.objects.create(
        title="child4", structured_data={"name": "Child 4", "age": 8}
    )
    child3_instance = TestModel.objects.create(
        title="child3",
        structured_data={"name": "Child 3", "age": 8},
        structured_data_recursive={"child_model": child4_instance},
    )
    child2_instance = TestModel.objects.create(
        title="child2",
        structured_data={"name": "Child 2", "age": 12},
        structured_data_recursive={"child_model": child3_instance},
    )
    child1_instance = TestModel.objects.create(
        title="child1",
        structured_data={"name": "Child 1", "age": 10},
        structured_data_recursive={"child_model": child2_instance},
    )
    instance = TestModel.objects.create(
        title="test",
        structured_data={"name": "John", "age": 42},
        structured_data_recursive={"child_model": child1_instance},
    )

    dumped_data = instance.structured_data_recursive.model_dump()
    child_model_data = recursive_get_child_model(
        dumped_data, settings.STRUCTURED_SERIALIZATION_MAX_DEPTH
    )
    assert "structured_data_recursive" not in child_model_data
