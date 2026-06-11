import pytest
from typing import Literal, Optional, Union


# Regression C11: union variants with same-named relation fields must not
# mis-bind to the wrong Django model. The parent engine used to register the
# FIRST CacheEnabledModel variant and harvest every row's data with it,
# splicing ValueWithCache objects bound to the wrong model — the FK
# from_cache branch then silently resolved the wrong instance.


def _holder():
    from structured.pydantic.models import BaseModel
    from tests.app.test_module.models import SimpleRelationModel, CustomManagerModel

    class VariantA(BaseModel):
        type: Literal["a"] = "a"
        ref: Optional[SimpleRelationModel] = None

    class VariantB(BaseModel):
        type: Literal["b"] = "b"
        ref: Optional[CustomManagerModel] = None

    class UnionHolder(BaseModel):
        data: Union[VariantA, VariantB]

    return UnionHolder, VariantA, VariantB


@pytest.mark.django_db
@pytest.mark.parametrize(
    "cache_setting_fixture",
    ["cache_enabled", "cache_disabled", "shared_cache"],
    indirect=True,
)
def test_union_variants_resolve_relations_against_their_own_model(cache_setting_fixture):
    from tests.app.test_module.models import SimpleRelationModel, CustomManagerModel

    UnionHolder, VariantA, VariantB = _holder()
    simple = SimpleRelationModel.objects.create(name="simple")
    custom = CustomManagerModel.items.create(name="custom")
    # pks of the two rows typically collide (both first rows) — exactly the
    # condition under which the old mis-binding silently resolved the wrong
    # model's instance

    holder_b = UnionHolder.validate_python({"data": {"type": "b", "ref": custom.pk}})
    assert isinstance(holder_b.data, VariantB)
    assert isinstance(holder_b.data.ref, CustomManagerModel)
    assert holder_b.data.ref == custom

    holder_a = UnionHolder.validate_python({"data": {"type": "a", "ref": simple.pk}})
    assert isinstance(holder_a.data, VariantA)
    assert isinstance(holder_a.data.ref, SimpleRelationModel)
    assert holder_a.data.ref == simple


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_relinfo_registration_for_unions(cache_setting_fixture):
    """Multi-variant unions get NO parent RelInfo (each variant's own
    wrap-validator batches per item); single-variant Optional[Nested]
    keeps its RIField."""
    from structured.pydantic.models import BaseModel
    from structured.cache.rel_info import RelInfo
    from tests.app.test_module.models import SimpleRelationModel

    UnionHolder, _, _ = _holder()
    assert "data" not in UnionHolder._cache_engine.__related_fields__

    class Nested(BaseModel):
        ref: Optional[SimpleRelationModel] = None

    class OptionalHolder(BaseModel):
        data: Optional[Nested] = None

    info = OptionalHolder._cache_engine.__related_fields__.get("data")
    assert info is not None and info.type == RelInfo.RIField
