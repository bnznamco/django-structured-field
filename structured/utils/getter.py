from typing import Any, Union


def safe_getter(instance: Union[dict, object], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary or object."""
    if isinstance(instance, dict):
        return instance.get(key, default)
    return getattr(instance, key, default)


def pointed_getter(instance: Union[dict, object], pointed: str, default: Any = None) -> Any:
    """Get a value from a nested structure using a dotted path."""
    attrs = pointed.split(".", 1)
    data = safe_getter(instance, attrs[0], default)
    if len(attrs) == 2:
        data = pointed_getter(data, attrs[1], default)
    return data
