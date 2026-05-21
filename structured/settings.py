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

    @property
    def STRUCTURED_SERIALIZATION_MAX_DEPTH(self):
        return pointed_getter(self.get_settings(), "SERIALIZATION.MAX_DEPTH", 2)

    @property
    def STRUCTURED_AUTO_INSTALL_MANAGER(self):
        """
        When True (default), any model owning a ``StructuredJSONField`` has
        its managers' queryset classes auto-promoted to a structured-aware
        variant. Disable for fine-grained opt-in.
        """
        return pointed_getter(self.get_settings(), "AUTO_INSTALL_MANAGER", True)


settings = Settings()
