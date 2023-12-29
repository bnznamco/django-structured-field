def map_method_aliases(new_cls):
    method_aliases = {
        "validate_python": "model_validate",
        "validate_json": "model_validate_json",
        # "dump_python": "model_dump",
        # "dump_json": "model_dump_json",
        "json_schema": "model_json_schema",
    }
    for alias_name, target_name in method_aliases.items():
        setattr(new_cls, alias_name, getattr(new_cls, target_name))
    return new_cls
