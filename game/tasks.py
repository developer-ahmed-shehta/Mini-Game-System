from celery import shared_task
from .services.db import players  # adjust path if needed

@shared_task
def finish_building(user_id, building_id):
    # Get the player document
    player = players.find_one({"user_id": user_id})
    if not player:
        return

    # Find the matching building in player's data
    player_building = None
    for b in player["buildings"]:
        if b["building_id"] == building_id:
            player_building = b
            break

    # If building not found or already completed, do nothing
    if not player_building:
        return

    if player_building.get("status") != "in_progress":
        return

    # Mark the building as completed and clean up timing info
    players.update_one(
        {"user_id": user_id, "buildings.building_id": building_id},
        {
            "$set": {
                "buildings.$.status": "completed"
            },
            "$unset": {
                "buildings.$.end_time": "",
                "buildings.$.task_id": "",
                "buildings.$.started_at": "",
                "buildings.$.duration": ""
            }
        }
    )
