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


def flatten_errors(errors: Union[Dict[str, Any], List[Any]], prefix: str = "") -> Dict[str, List[str]]:
    """Flatten nested error dict/list into dot-notation keyed dict."""
    flat: Dict[str, List[str]] = {}
    if isinstance(errors, dict):
        for key, value in errors.items():
            full_key = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, list) and value and isinstance(value[0], str):
                flat[full_key] = value
            else:
                flat.update(flatten_errors(value, full_key))
    elif isinstance(errors, list):
        for i, item in enumerate(errors):
            full_key = f"{prefix}.{i}" if prefix else str(i)
            if isinstance(item, dict):
                flat.update(flatten_errors(item, full_key))
    return flat
