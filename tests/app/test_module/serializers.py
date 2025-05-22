from rest_framework import serializers
from structured.contrib.restframework import StructuredModelSerializer
from tests.app.test_module.models import TestModel


class TestModelSerializer(StructuredModelSerializer):
    class Meta:
        model = TestModel
        fields = ["id", "title", "structured_data", "structured_data_list"]
