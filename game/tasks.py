from celery import shared_task
from .services.db import players

@shared_task
def finish_building(user_id, building_id):
    player = players.find_one({"user_id": user_id})



    if not player:
        return

    print(player)
    # Find this building
    building = None
    for b in player["buildings"]:
        if b["building_id"] == building_id:
            player_building = b
            break

    if not building:
        return

    print(building)
    # Only finish if still in progress
    if building.get("status") != "in_progress":
        return

    players.update_one(
        {"user_id": user_id, "buildings.building_id": building_id},
        {
            "$set": {"buildings.$.status": "completed"},
            "$unset": {
                "buildings.$.end_time": "",
                "buildings.$.task_id": "",
                "buildings.$.started_at": "",
                "buildings.$.duration": ""
            }
        }
    )
