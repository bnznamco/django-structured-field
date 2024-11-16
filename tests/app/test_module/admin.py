from django.contrib import admin
from .models import TestModel, ChildModel1, ChildModel2, SimpleRelationModel


class TestModelAdmin(admin.ModelAdmin):
    pass


class ChildModel1Admin(admin.ModelAdmin):
    pass


class ChildModel2Admin(admin.ModelAdmin):
    pass


class SimpleRelationModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(TestModel, TestModelAdmin)
admin.site.register(ChildModel1, ChildModel1Admin)
admin.site.register(ChildModel2, ChildModel2Admin)
admin.site.register(SimpleRelationModel, SimpleRelationModelAdmin)
