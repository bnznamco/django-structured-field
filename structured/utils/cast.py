import json
from typing import Any, Union, List, Type
from structured.pydantic.models import BaseModel


def cast_to_python(value: Any) -> Union[List[Type[BaseModel]], Type[BaseModel]]:
    if isinstance(value, list):
        value = [cast_to_python(v) for v in value]
    elif isinstance(value, BaseModel):
        value = value.model_dump(mode="python", exclude_unset=True)
    elif isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {value}") from e
    return value


def cast_to_model(
    value: Any, schema: Type[BaseModel]
) -> Union[List[Type[BaseModel]], Type[BaseModel]]:
    if isinstance(value, list):
        value = [cast_to_model(v, schema) for v in value]
    elif isinstance(value, dict):
        value = schema.validate_python(value)
    elif isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {value}") from e
        value = schema.validate_python(value)
    return value
