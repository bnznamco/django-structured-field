from inspect import isclass
from typing import Any, ForwardRef, Generic, Type, List, Tuple, Optional
from typing_extensions import TypeVar, get_args
from django.core.exceptions import ImproperlyConfigured


T = TypeVar("T")


class LazyType:
    def __init__(self, path: str):  # pragma: no cover
        self.path = path

    def evaluate(self, base_cls: Type) -> Type:  # pragma: no cover
        module, type_name = self._evaluate_path(self.path, base_cls)
        return self._import(module, type_name)

    def _evaluate_path(self, relative_path: str, base_cls: Type) -> Tuple[str, str]:  # pragma: no cover
        base_module = base_cls.__module__
        modules = self._get_modules(relative_path, base_module)
        type_name = modules.pop()
        module = ".".join(modules)
        if not module:
            module = base_module
        return module, type_name

    def _get_modules(self, relative_path: str, base_module: str) -> List[str]:  # pragma: no cover
        canonical_path = relative_path.lstrip(".")
        canonical_modules = canonical_path.split(".")
        if not relative_path.startswith("."):
            return canonical_modules
        parents_amount = len(relative_path) - len(canonical_path)
        parent_modules = base_module.split(".")
        parents_amount = max(0, parents_amount - 1)
        if parents_amount > len(parent_modules):
            raise ValueError(f"Can't evaluate path '{relative_path}'")
        return parent_modules[: parents_amount * -1] + canonical_modules

    def _import(self, module_name: str, type_name: str) -> Type:  # pragma: no cover
        module = __import__(module_name, fromlist=[type_name])
        try:
            return getattr(module, type_name)
        except AttributeError:
            raise ValueError(f"Can't find type '{module_name}.{type_name}'.")


def get_type(source: Generic[T], raise_exception: bool = True) -> Optional[T]:
    """Retrieve the type from a generic source."""
    try:
        subclass = get_args(source)[0]
        if isinstance(subclass, ForwardRef):
            try:
                return subclass._evaluate(globals(), locals(), frozenset())
            except TypeError:
                return subclass._evaluate(globals(), locals())
        return subclass
    except IndexError:
        if raise_exception:
            raise ImproperlyConfigured("Must provide a Model class for ForeignKey fields.")
        return None


def get_type_eval(source: Generic[T], model: Any, raise_exception: bool = True) -> Optional[T]:  # pragma: no cover
    """Evaluate and retrieve the type from a generic source."""
    type_ = get_type(source, raise_exception)
    if isinstance(type_, str):
        return LazyType(type_).evaluate(model)
    return type_


def find_model_type_from_args(args: List[Any], base_model: Type, model_type: Type) -> Optional[Type]:
    """Find and return the model type from the provided arguments."""
    lazy_types = [
        LazyType(arg).evaluate(base_model) for arg in args if isinstance(arg, str)
    ]
    return next(
        (
            c
            for c in list(args) + lazy_types
            if isclass(c) and issubclass(c, model_type)
        ),
        None,
    )
