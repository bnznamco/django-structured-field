import pytest


class TestCastToPython:
    def test_cast_string_json_to_python(self):
        from structured.utils.cast import cast_to_python
        result = cast_to_python('{"name": "John", "age": 42}')
        assert result == {"name": "John", "age": 42}

    def test_cast_invalid_string_to_python(self):
        from structured.utils.cast import cast_to_python
        with pytest.raises(ValueError, match="Invalid JSON string"):
            cast_to_python("{invalid json")

    def test_cast_list_to_python(self):
        from structured.utils.cast import cast_to_python
        from tests.app.test_module.models import TestSchema
        schema = TestSchema(name="John", age=25)
        result = cast_to_python([schema])
        assert isinstance(result, list)
        assert result[0]["name"] == "John"


class TestCastToModel:
    def test_cast_dict_to_model(self):
        from structured.utils.cast import cast_to_model
        from tests.app.test_module.models import TestSchema
        result = cast_to_model({"name": "John", "age": 42}, TestSchema)
        assert isinstance(result, TestSchema)
        assert result.name == "John"

    def test_cast_string_json_to_model(self):
        from structured.utils.cast import cast_to_model
        from tests.app.test_module.models import TestSchema
        result = cast_to_model('{"name": "John", "age": 42}', TestSchema)
        assert isinstance(result, TestSchema)
        assert result.name == "John"

    def test_cast_invalid_string_to_model(self):
        from structured.utils.cast import cast_to_model
        from tests.app.test_module.models import TestSchema
        with pytest.raises(ValueError, match="Invalid JSON string"):
            cast_to_model("{invalid json", TestSchema)

    def test_cast_list_to_model(self):
        from structured.utils.cast import cast_to_model
        from tests.app.test_module.models import TestSchema
        result = cast_to_model(
            [{"name": "John", "age": 42}, {"name": "Jane", "age": 30}],
            TestSchema,
        )
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].name == "John"
        assert result[1].name == "Jane"
