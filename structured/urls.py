from structured.views import search_view
from django.urls import path

urlpatterns = [
    path("structured_field/search_model/<str:model>/", search_view, name="search"),
]
