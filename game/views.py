from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def start_build(request):
    user = request.user
    # access user.id, use as player_id in Mongo
    return JsonResponse({'status': 'Build started'})