from django.urls import path
from .views import player_info, build_start, building_list, check_task_status, accelerate_build_view, all_players_buildings_view

urlpatterns = [
    path('player/', player_info, name='player_info'),
    path('build/start/', build_start),
    path('buildings/', building_list),
    path('task-status/', check_task_status),
    path('build/accelerate/', accelerate_build_view),
    path('buildings/all_players/', all_players_buildings_view),
]