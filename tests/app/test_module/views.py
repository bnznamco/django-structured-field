from rest_framework import viewsets
from tests.app.test_module.models import TestModel
from tests.app.test_module.serializers import TestModelSerializer


class TestModelViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer