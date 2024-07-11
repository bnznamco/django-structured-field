
# test map_pydantic_errors function
def test_map_pydantic_errors():
    from structured.utils.errors import map_pydantic_errors
    from tests.app.test_module.models import TestSchema
    from pydantic import ValidationError

    # test map_pydantic_errors with a simple error
    try:
        TestSchema(age="asdasd")
    except ValidationError as e:
        result = map_pydantic_errors(e)
        assert result == {
            "age": [
                "Input should be a valid integer, unable to parse string as an integer"
            ],
            "name": ["Field required"],
        }

    # test map_pydantic_errors with a nested error
    try:
        TestSchema(age="asdasd", child={"age": "asdasd"})
    except ValidationError as e:
        result = map_pydantic_errors(e)
        assert result == {
            "age": [
                "Input should be a valid integer, unable to parse string as an integer"
            ],
            "name": ["Field required"],
            "child": {
                "age": [
                    "Input should be a valid integer, unable to parse string as an integer"
                ],
                "name": ["Field required"],
            },
        }

    # test map_pydantic_errors with a nested error on childs list
    try:
        TestSchema(
            name="John",
            age=10,
            childs=[
                {},
                {"age": "asdasd"},
            ],
        )
    except ValidationError as e:
        result = map_pydantic_errors(e)
        assert len(result["childs"]) == 2
        assert result["childs"][0] == {"name": ["Field required"]}
        assert result["childs"][1] == {
            "age": [
                "Input should be a valid integer, unable to parse string as an integer"
            ],
            "name": ["Field required"],
        }
        
