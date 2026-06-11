import pytest
from typing import Optional


# Regression: subclassing a schema must keep inherited defaults
def test_subclass_keeps_inherited_defaults():
    from structured.pydantic.models import BaseModel

    class Parent(BaseModel):
        a: int = 5
        name: str = "x"

    class Child(Parent):
        b: str = "y"

    assert not Child.model_fields["a"].is_required()
    obj = Child()
    assert obj.a == 5
    assert obj.name == "x"
    assert obj.b == "y"


# Regression: a subclass re-declaring a field must win over the parent
def test_subclass_annotation_overrides_parent():
    from structured.pydantic.models import BaseModel

    class Parent(BaseModel):
        x: int = 0

    class Child(Parent):
        x: str = "redeclared"

    assert Child.model_fields["x"].annotation is str
    assert Child().x == "redeclared"
    assert Child(x="hello").x == "hello"


# Regression: in multi-level hierarchies the NEAREST declaration wins
def test_multilevel_override_nearest_wins():
    from structured.pydantic.models import BaseModel

    class GrandParent(BaseModel):
        z: int = 1

    class Parent(GrandParent):
        z: float = 1.5

    class Child(Parent):
        pass

    assert Child.model_fields["z"].annotation is float
    assert Child().z == 1.5


# Plain (non-pydantic) mixin annotations must still be collected, with defaults
def test_plain_mixin_annotations_collected():
    from structured.pydantic.models import BaseModel

    class Mixin:
        tag: str = "default-tag"

    class WithMixin(Mixin, BaseModel):
        own: int = 1

    assert "tag" in WithMixin.model_fields
    assert WithMixin().tag == "default-tag"
    assert WithMixin(tag="custom").tag == "custom"


# Inherited relation fields keep working (annotation patching + cache engine)
@pytest.mark.django_db
@pytest.mark.parametrize(
    "cache_setting_fixture",
    ["cache_enabled", "cache_disabled"],
    indirect=True,
)
def test_subclass_inherits_relation_fields(cache_setting_fixture):
    from structured.pydantic.models import BaseModel
    from structured.cache.rel_info import RelInfo
    from tests.app.test_module.models import SimpleRelationModel

    class ParentSchema(BaseModel):
        name: str = ""
        fk_field: Optional[SimpleRelationModel] = None

    class ChildSchema(ParentSchema):
        extra: str = ""

    rel = SimpleRelationModel.objects.create(name="rel")
    inst = ChildSchema.validate_python({"name": "n", "fk_field": rel.pk})
    assert inst.fk_field == rel
    assert inst.extra == ""
    rel_info = ChildSchema._cache_engine.__related_fields__.get("fk_field")
    assert rel_info is not None and rel_info.type == RelInfo.FKField
