from django.core.management import call_command
from django.db import connections
from django.conf import settings
import pytest


# This creates a dummy database for testing purposes in the root directory of the project
# Feel free to drop the database at any time (.name is "test_db.sqlite3")
@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    from django.conf import settings
    db_name = "test_db.sqlite3"
    settings.DATABASES["default"]["NAME"] = db_name
    with django_db_blocker.unblock():
        call_command("sqlflush",)
        call_command("makemigrations", interactive=False)
        call_command("migrate", interactive=False)
    yield
    for connection in connections.all():
        connection.close()

@pytest.fixture
def setting_fixture(request):
    """Fixture to dynamically adjust settings based on parameter."""
    if request.param == "cache_enabled":
         settings.STRUCTURED_FIELD = {"CACHE": {"ENABLED": True}}
    elif request.param == "cache_disabled":
        settings.STRUCTURED_FIELD = {"CACHE": {"ENABLED": False}}
    elif request.param == "shared_cache":
        settings.STRUCTURED_FIELD = {"CACHE": {"SHARED": True, "ENABLED": True}}
    yield
    delattr(settings, "STRUCTURED_FIELD")