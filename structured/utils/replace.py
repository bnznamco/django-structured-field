from typing import Callable, Any, Dict


def find_and_replace_dict(obj: Dict[str, Any], predicate: Callable[[str, Any], Any]) -> Dict[str, Any]:
    """Recursively find and replace values in a dictionary based on a predicate."""
    result = {}
    for k, v in obj.items():
        v = predicate(key=k, value=v)
        if isinstance(v, dict):
            v = find_and_replace_dict(v, predicate)
        result[k] = v
    return result
