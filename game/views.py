from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from .services.player_service import get_or_create_player
from .services.building_service import start_building,accelerate_building
from .services.db import buildings

@login_required
def player_info(request):
    player = get_or_create_player(request.user.id)
    return JsonResponse({
        "resources": player["resources"],
        "buildings": player["buildings"]
    })


@csrf_exempt
@login_required
def build_start(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            building_id = int(data.get('building_id'))
            # print(building_id)
            start_building(request.user.id, building_id)
            return JsonResponse({"status": "Building started"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@login_required
def accelerate_build_view(request):
    if request.method == 'POST':
        building_id = int(request.POST.get("building_id"))
        reduce_by = int(request.POST.get("reduce_by", 60))  # Default: reduce 60s
        try:
            accelerate_building(request.user.id, building_id, reduce_by)
            return JsonResponse({"status": "Building accelerated by seconds", "reduced": reduce_by})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@login_required
def building_list(request):
    all_buildings = list(buildings.find({}, {"_id": 1, "name": 1, "duration": 1}))
    return JsonResponse({"buildings": all_buildings})



from celery.result import AsyncResult
from main.celery_app import app

def check_task_status(request):
    task_id = request.GET.get("task_id")
    if not task_id:
        return JsonResponse({"error": "Missing task_id"}, status=400)

    result = AsyncResult(task_id, app=app)
    task_meta = result._get_task_meta()  # all backend-stored info

    return JsonResponse({
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
        "result": str(result.result),
        "traceback": str(task_meta.get("traceback")),
        "date_done": str(task_meta.get("date_done")),
        "children": str(task_meta.get("children")),
        "meta_raw": task_meta  # raw meta (optional)
    })
