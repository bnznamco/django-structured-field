from rest_framework import serializers
from structured.contrib.restframework import StructuredModelSerializer
from tests.app.test_module.models import TestModel


class TestModelSerializer(StructuredModelSerializer):
    class Meta:
        model = TestModel
        fields = "__all__"
