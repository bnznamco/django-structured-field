# TODO: get settings from django.conf.settings
from django.conf import settings
from structured.utils.getter import pointed_getter

GENERAL_SETTINGS = getattr(settings, "STRUCTURED_FIELD", {})
STRUCTURED_FIELD_CACHE_ENABLED = pointed_getter(GENERAL_SETTINGS, "CACHE.ENABLED", True)
STRUCTURED_FIELD_SHARED_CACHE = pointed_getter(GENERAL_SETTINGS, "CACHE.SHARED", False)
