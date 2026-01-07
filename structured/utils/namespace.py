import sys
from typing import Any, Type, Dict, Optional

try:
    from pydantic._internal._model_construction import unpack_lenient_weakvaluedict
except ImportError:
    def unpack_lenient_weakvaluedict(d: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return d


def merge_cls_and_parent_ns(cls: Type[Any], parent_namespace: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    module_name = getattr(cls, '__module__', None)
    namespace = {}
    if module_name:
        namespace = sys.modules.get(module_name, object()).__dict__.copy()
    if parent_namespace is not None:
        # Unpack weak references if the namespace was built using build_lenient_weakvaluedict
        unpacked_ns = unpack_lenient_weakvaluedict(parent_namespace)
        if unpacked_ns is not None:
            namespace.update(unpacked_ns)
    namespace[cls.__name__] = cls
    return namespace
