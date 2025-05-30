import pytest
from tests.app.test_module.models import TestModel, SimpleRelationModel
from pydantic import ValidationError


@pytest.mark.django_db
def test_union_schema_direct_assignment():
    rel = SimpleRelationModel.objects.create(name="Rel1")
    # Assign schema1 data directly
    obj = TestModel.objects.create(
        title="Direct Assignment Schema1",
        structured_data_union={
            "data": {
                "type": "schema1",
                "name": "DirectTest",
                "age": 30,
                "qs_field": [rel.pk],
                "fk_field": rel.pk,
            }
        },
        structured_data={"name": "A", "qs_field": [rel.pk], "fk_field": rel.pk},
    )
    obj.refresh_from_db()
    assert obj.structured_data_union.data.name == "DirectTest"
    assert obj.structured_data_union.data.qs_field[0].pk == rel.pk

    # Assign schema2 data directly
    obj.structured_data_union = {
        "data": {
            "type": "schema2",
            "name_2": "DirectTest2",
            "age_2": 99,
            "qs_field_2": [rel.pk],
            "fk_field_2": rel.pk,
        }
    }
    obj.save()
    obj.refresh_from_db()
    assert obj.structured_data_union.data.name_2 == "DirectTest2"
    assert obj.structured_data_union.data.qs_field_2[0].pk == rel.pk


@pytest.mark.django_db
def test_union_schema_direct_assignment_schema1():
    rel = SimpleRelationModel.objects.create(name="Rel1")
    obj = TestModel.objects.create(
        title="Direct Assignment Schema1",
        structured_data_union={
            "data": {
                "type": "schema1",
                "name": "DirectTest",
                "age": 30,
                "qs_field": [rel.pk],
                "fk_field": rel.pk,
            }
        },
        structured_data={"name": "A", "qs_field": [rel.pk], "fk_field": rel.pk},
    )
    obj.refresh_from_db()
    assert obj.structured_data_union.data.name == "DirectTest"
    assert obj.structured_data_union.data.qs_field[0].pk == rel.pk


@pytest.mark.django_db
def test_union_schema_direct_assignment_schema2():
    rel = SimpleRelationModel.objects.create(name="Rel2")
    obj = TestModel.objects.create(
        title="Direct Assignment Schema2",
        structured_data_union={
            "data": {
                "type": "schema2",
                "name_2": "DirectTest2",
                "age_2": 99,
                "qs_field_2": [rel.pk],
                "fk_field_2": rel.pk,
            }
        },
        structured_data={"name": "B", "qs_field": [rel.pk], "fk_field": rel.pk},
    )
    obj.refresh_from_db()
    assert obj.structured_data_union.data.name_2 == "DirectTest2"
    assert obj.structured_data_union.data.qs_field_2[0].pk == rel.pk


@pytest.mark.django_db
def test_union_schema_switch_schema1_to_schema2():
    rel = SimpleRelationModel.objects.create(name="Rel3")
    obj = TestModel.objects.create(
        title="Switch Schema",
        structured_data_union={
            "data": {
                "type": "schema1",
                "name": "FirstSchema",
                "age": 10,
                "qs_field": [rel.pk],
                "fk_field": rel.pk,
            }
        },
        structured_data={"name": "C", "qs_field": [rel.pk], "fk_field": rel.pk},
    )
    obj.refresh_from_db()
    assert obj.structured_data_union.data.name == "FirstSchema"
    # Switch to schema2
    obj.structured_data_union = {
        "data": {
            "type": "schema2",
            "name_2": "SecondSchema",
            "age_2": 20,
            "qs_field_2": [rel.pk],
            "fk_field_2": rel.pk,
        }
    }
    obj.save()
    obj.refresh_from_db()
    assert obj.structured_data_union.data.name_2 == "SecondSchema"
    assert obj.structured_data_union.data.qs_field_2[0].pk == rel.pk


@pytest.mark.django_db
def test_union_schema_nested_data():
    rel = SimpleRelationModel.objects.create(name="Rel4")
    obj = TestModel.objects.create(
        title="Nested Data",
        structured_data_union={
            "data": {
                "type": "schema1",
                "name": "Parent",
                "age": 50,
                "child": {"name": "Child", "age": 5, "qs_field": [], "fk_field": None},
                "childs": [
                    {"name": "Child1", "age": 6, "qs_field": [], "fk_field": None},
                    {"name": "Child2", "age": 7, "qs_field": [], "fk_field": None},
                ],
                "qs_field": [rel.pk],
                "fk_field": rel.pk,
            }
        },
        structured_data={"name": "D", "qs_field": [rel.pk], "fk_field": rel.pk},
    )
    obj.refresh_from_db()
    assert obj.structured_data_union.data.child.name == "Child"
    assert obj.structured_data_union.data.childs[0].name == "Child1"
    assert obj.structured_data_union.data.childs[1].name == "Child2"


@pytest.mark.django_db
def test_union_schema_empty_and_invalid():
    rel = SimpleRelationModel.objects.create(name="Rel5")
    # Empty data
    obj = TestModel(
        title="Empty Data",
        structured_data_union={"data": {}},
        structured_data={"name": "E", "qs_field": [rel.pk], "fk_field": rel.pk},
    )
    with pytest.raises(ValidationError):
        obj.full_clean()
    obj.structured_data_union = {"data": {"type": "unknown"}}
    with pytest.raises(ValidationError):
        obj.full_clean()
