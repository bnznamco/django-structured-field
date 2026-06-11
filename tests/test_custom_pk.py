import json
import pytest
from typing import Optional


# Regression F7: models with a custom-NAMED primary key must round-trip.
# The persisted wire format always keys relations as {'id', 'name', 'model'}
# (utils/serializer.py, search API, widget items), while validators read the
# pk attname — readers must accept BOTH keys.


def _schema():
    from structured.pydantic.models import BaseModel
    from structured.pydantic.fields import QuerySet
    from tests.app.test_module.models import CustomPKModel

    class CustomPKSchema(BaseModel):
        fk_field: Optional[CustomPKModel] = None
        qs_field: QuerySet[CustomPKModel]

    return CustomPKSchema


@pytest.mark.django_db
@pytest.mark.parametrize(
    "cache_setting_fixture",
    ["cache_enabled", "cache_disabled", "shared_cache"],
    indirect=True,
)
def test_custom_pk_wire_format_round_trip(cache_setting_fixture):
    """model_dump_json output (the persisted format) must re-validate."""
    from tests.app.test_module.models import CustomPKModel

    CustomPKSchema = _schema()
    a = CustomPKModel.objects.create(code="alpha", name="A")
    b = CustomPKModel.objects.create(code="beta", name="B")

    inst = CustomPKSchema.validate_python({"fk_field": a, "qs_field": [a, b]})
    wire = inst.model_dump(mode="json")
    # the wire format keys the pk as the literal 'id'
    assert wire["fk_field"]["id"] == "alpha"
    assert {item["id"] for item in wire["qs_field"]} == {"alpha", "beta"}

    # round-trip from the dumped wire format (previously KeyError/TypeError)
    restored = CustomPKSchema.validate_python(json.loads(json.dumps(wire)))
    assert restored.fk_field == a
    assert {m.pk for m in restored.qs_field} == {"alpha", "beta"}

    # json-mode string round-trip too
    restored2 = CustomPKSchema.validate_json(inst.model_dump_json())
    assert restored2.fk_field == a


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_custom_pk_attname_keyed_dicts_accepted(cache_setting_fixture):
    """Dicts keyed by the real attname (python-mode dumps) must also work."""
    from tests.app.test_module.models import CustomPKModel

    CustomPKSchema = _schema()
    a = CustomPKModel.objects.create(code="alpha", name="A")

    inst = CustomPKSchema.validate_python(
        {"fk_field": {"code": "alpha"}, "qs_field": [{"code": "alpha"}]}
    )
    assert inst.fk_field == a
    assert [m.pk for m in inst.qs_field] == ["alpha"]


@pytest.mark.django_db
@pytest.mark.parametrize("cache_setting_fixture", ["cache_enabled"], indirect=True)
def test_custom_pk_malformed_dict_raises_validation_error(cache_setting_fixture):
    """A relation dict with neither attname nor 'id' must produce a proper
    pydantic ValidationError, not an escaping KeyError/TypeError."""
    from pydantic import ValidationError as PydanticValidationError

    CustomPKSchema = _schema()
    with pytest.raises(PydanticValidationError):
        CustomPKSchema.validate_python({"fk_field": {"name": "no-pk-here"}})
    with pytest.raises(PydanticValidationError):
        CustomPKSchema.validate_python({"qs_field": [{"name": "no-pk-here"}]})
