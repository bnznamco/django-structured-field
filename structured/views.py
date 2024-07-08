from django.http import JsonResponse, Http404
from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required


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
        if search_term == "__all__":
            results = model.objects.all()
        if search_term.startswith("_pk="):
            pk = search_term.split("_pk=")[1]
            if not pk.isdigit():
                return JsonResponse([], safe=False)
            results = model.objects.filter(pk=pk)
        if search_term.startswith("_pk__in="):
            pks = search_term.split("_pk__in=")[1].split(",")
            results = model.objects.filter(pk__in=[pk for pk in pks if pk.isdigit()])
        else:
            results = model.objects.filter(name__icontains=search_term)[:100]
        return JsonResponse(
            [
                {"id": r.pk, "name": r.__str__() or f"{model.__name__} ({r.pk})"}
                for r in results
            ],
            safe=False,
        )
    return JsonResponse({"error": "Method Not Allowed"}, status=405)
