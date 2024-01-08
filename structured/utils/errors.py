from pydantic import ValidationError
from typing import Union, Any
from structured.utils.setter import pointed_setter


def map_pydantic_errors(
    error: ValidationError, many: bool = False
) -> Union[dict, list]:
    """Converts Pydantic errors to a nested dictionary."""
    error_stack: Union[list, dict[str, Any]] = [] if many else {}
    for error in error.errors():
        pointed_setter(
            error_stack, ".".join([str(x) for x in error["loc"]]), [error["msg"]]
        )
    return error_stack
