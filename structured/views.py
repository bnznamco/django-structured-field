from django.http import JsonResponse, Http404
from django.apps import apps
from typing import Type
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models as django_models
from structured.utils.serializer import minimal_list_serialization
from structured.utils.django import import_abs_model


def create_search_vector(model: Type[django_models.Model], query: str):
    search_vector = django_models.Q()
    for f in model._meta.fields:
        if isinstance(f, (django_models.CharField, django_models.TextField)):
            search_vector |= django_models.Q(**{f"{f.name}__icontains": query})
    return search_vector


def abstract_model_search(model: Type[django_models.Model], query: str):
    models = [m for m in apps.get_models() if issubclass(m, model)]
    results = []
    for model in models:
        if query == "__all__":
            results.extend(model.objects.all())
            continue
        search_vector = create_search_vector(model, query)
        results.extend(model.objects.filter(search_vector)[:100])
    return results


def search(request, model):
    if request.method == "GET":
        try:
            model = apps.get_model(*model.rsplit(".", 1))
        except (LookupError, ValueError):
            model = import_abs_model(*model.rsplit(".", 1))
            if not model:
                raise Http404(f'No model matches the given name "{model}".')
        search_term = request.GET.get("_q", None)
        if not search_term:
            return JsonResponse([], safe=False)
        elif model._meta.abstract:
            results = abstract_model_search(model, search_term)
        elif search_term == "__all__":
            results = model.objects.all()
        elif search_term.startswith("_pk="):
            pk = search_term.split("_pk=", 1)[1]
            if not pk.isdigit():
                return JsonResponse([], safe=False)
            results = model.objects.filter(pk=pk)
        elif search_term.startswith("_pk__in="):
            pks = search_term.split("_pk__in=")[1].split(",")
            results = model.objects.filter(pk__in=[pk for pk in pks if pk.isdigit()])
        else:
            search_vector = create_search_vector(model, search_term)
            results = model.objects.filter(search_vector)[:100]
        return JsonResponse(minimal_list_serialization(results), safe=False)
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


@staff_member_required
def search_view(request, model):
    return search(request, model)
