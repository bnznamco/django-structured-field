# TODO: get settings from django.conf.settings
from django.conf import settings as django_settings
from structured.utils.getter import pointed_getter


class Settings:
    def get_settings(self):
        return getattr(django_settings, "STRUCTURED_FIELD", {})

    @property
    def STRUCTURED_FIELD_CACHE_ENABLED(self):
        return pointed_getter(self.get_settings(), "CACHE.ENABLED", True)

    @property
    def STRUCTURED_FIELD_SHARED_CACHE(self):
        return pointed_getter(self.get_settings(), "CACHE.SHARED", False)


settings = Settings()
