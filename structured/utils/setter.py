from typing import Sequence, Any, Union
from .getter import pointed_getter


def set_key(data: Union[Sequence, dict, object], key: Union[int, str], val: Any) -> Union[Sequence, dict, object]:
    """Set a value in a sequence, dictionary, or object."""
    if isinstance(data, Sequence):
        key = int(key)
        if key < len(data):
            data[key] = val
        else:
            data.append(val)
        return data
    elif isinstance(data, dict):
        data[key] = val
    else:
        setattr(data, key, val)
    return data


def get_key(data: Union[Sequence, dict, object], key: Union[int, str], default: Any) -> Any:
    """Get a value from a sequence, dictionary, or object."""
    if isinstance(data, Sequence):
        try:
            return data[int(key)]
        except IndexError:
            return default
    return pointed_getter(data, key, default)


def pointed_setter(data: Union[Sequence, dict, object], path: str, value: Any) -> Union[Sequence, dict, object]:
    """Set a value in a nested structure using a dotted path."""
    path_parts = path.split(".")
    key = path_parts.pop(0)
    if not path_parts:
        return set_key(data, key, value)
    default = [] if path_parts[0].isdigit() else {}
    return set_key(
        data, key, pointed_setter(get_key(data, key, default), ".".join(path_parts), value)
    )
