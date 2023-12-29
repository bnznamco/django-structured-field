from typing import Callable


def find_and_replace_dict(obj: dict, predicate: Callable):
    result = {}
    for k, v in obj.items():
        v = predicate(key=k, value=v)
        if isinstance(v, dict):
            v = find_and_replace_dict(v, predicate)
        result[k] = v
    return result
