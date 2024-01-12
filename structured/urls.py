from structured.views import search
from django.urls import path

urlpatterns = [
    path("structured_field/search_model/", search, name="search"),
]
