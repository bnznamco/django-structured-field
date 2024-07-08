from django.http import JsonResponse
from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def search(request, model):
    if request.method == "GET":
        search_term = request.GET.get("_q", None)
        if search_term:
            model = apps.get_model(*model.split("."))
            if model:
                if search_term == "__all__":
                    results = model.objects.all()
                if search_term.startswith("_pk="):
                    results = model.objects.filter(pk=search_term.split("_pk=")[1])
                if search_term.startswith("_pk__in="):
                    pks = search_term.split("_pk__in=")[1].split(",")
                    results = model.objects.filter(pk__in=pks)
                else:
                    results = model.objects.filter(name__icontains=search_term)[:20]
                json_results = [
                    {"id": result.pk, "name": result.__str__() or f"{model.__name__} ({result.pk})"} for result in results
                ]
                return JsonResponse(json_results, safe=False)
    return JsonResponse([], safe=False)
