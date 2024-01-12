from django.http import JsonResponse
from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def search(request):
    if request.method == "GET":
        model = request.GET.get("_m", None)
        search_term = request.GET.get("_q", None)
        if model and search_term:
            model = apps.get_model(*model.split("."))
            if model:
                if search_term == "__all__":
                    results = model.objects.all()
                else:
                    results = model.objects.filter(name__icontains=search_term)[:20]
                json_results = [
                    {"id": result.pk, "name": result.__str__()} for result in results
                ]
                return JsonResponse(json_results, safe=False)
    return JsonResponse([], safe=False)
