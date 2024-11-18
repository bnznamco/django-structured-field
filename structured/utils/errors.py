from pydantic import ValidationError
from typing import Union, Any, List, Dict
from structured.utils.setter import pointed_setter


def map_pydantic_errors(error: ValidationError, many: bool = False) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Convert Pydantic errors to a nested dictionary or list."""
    error_stack: Union[List[Dict[str, Any]], Dict[str, Any]] = [] if many else {}
    for err in error.errors():
        pointed_setter(
            error_stack, ".".join([str(x) for x in err["loc"]]), [err["msg"]]
        )
    return error_stack
