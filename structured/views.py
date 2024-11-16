from django.http import JsonResponse, Http404
from django.apps import apps
from typing import Type
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db import models as django_models
from django.db.models.query import QuerySet
from structured.utils.serializer import minimal_list_serialization
from structured.utils.django import import_abs_model


def create_search_query(model: Type[django_models.Model], query: str):
    search_query = django_models.Q()
    if query:
        for f in model._meta.fields:
            if isinstance(f, (django_models.CharField, django_models.TextField)):
                search_query |= django_models.Q(**{f"{f.name}__icontains": query})
    return search_query


def abstract_model_search(model: Type[django_models.Model], query: str):
    models = [m for m in apps.get_models() if issubclass(m, model) and not m._meta.abstract]
    results = []
    for model in models:
        if query == "__all__":
            results.extend(model.objects.all())
            continue
        search_query = create_search_query(model, query)
        results.extend(model.objects.filter(search_query)[:100])
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
        if model._meta.abstract:
            results = abstract_model_search(model, search_term)
        elif not search_term:
            results = model.objects.all()
        elif search_term.startswith("_pk="):
            pk = search_term.split("_pk=", 1)[1]
            results = model.objects.filter(pk=pk)
        elif search_term.startswith("_pk__in="):
            pks = search_term.split("_pk__in=")[1].split(",")
            results = model.objects.filter(pk__in=[pk for pk in pks if pk.isdigit()])
        else:
            search_vector = create_search_query(model, search_term)
            results = model.objects.filter(search_vector)
        if isinstance(results, QuerySet):
            results = results.order_by("pk")
        paginator = Paginator(results, 50)
        page = request.GET.get("page", 1)
        page_obj = paginator.get_page(page)
        return JsonResponse({
                "items": minimal_list_serialization(page_obj),
                "more": page_obj.has_next(),
            },
            safe=False
        )
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


@staff_member_required
def search_view(request, model):
    return search(request, model)
