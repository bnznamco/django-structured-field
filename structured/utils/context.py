from pydantic import SerializationInfo


def build_context(info: SerializationInfo) -> dict:
    """Builds a context dictionary for serialization."""
    context = info.context or {}
    context["mode"] = info.mode
    context["__structured_depth"] = context.get("__structured_depth", 0)
    return context


def increase_context_depth(context: dict, step: int = 1) -> dict:
    """Increases the depth in the context dictionary."""
    context = context.copy()
    context["__structured_depth"] = context.get("__structured_depth", 0) + step
    return context
