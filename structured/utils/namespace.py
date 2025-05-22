import sys
from typing import Any, Type, Dict, Optional


def merge_cls_and_parent_ns(cls: Type[Any], parent_namespace: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    module_name = getattr(cls, '__module__', None)
    namespace = {}
    if module_name:
        namespace = sys.modules.get(module_name, object()).__dict__.copy()
    if parent_namespace is not None:
        namespace.update(parent_namespace)
    namespace[cls.__name__] = cls
    return namespace
