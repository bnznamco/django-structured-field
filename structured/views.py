from django.http import JsonResponse, Http404
from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models as django_models


@staff_member_required
def search(request, model):
    if request.method == "GET":
        try:
            model = apps.get_model(*model.rsplit(".", 1))
        except (LookupError, ValueError):
            raise Http404(f'No model matches the given name "{model}".')
        search_term = request.GET.get("_q", None)
        if not search_term:
            return JsonResponse([], safe=False)
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
            search_vector = django_models.Q()
            for f in model._meta.fields:
                if isinstance(f, (django_models.CharField, django_models.TextField)):
                    search_vector |= django_models.Q(**{f"{f.name}__icontains": search_term})
            results = model.objects.filter(search_vector)[:100]
        return JsonResponse(
            [
                {"id": r.pk, "name": r.__str__() or f"{model.__name__} ({r.pk})"}
                for r in results
            ],
            safe=False,
        )
    return JsonResponse({"error": "Method Not Allowed"}, status=405)
