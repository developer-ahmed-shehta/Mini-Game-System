import time
from .db import players, buildings
from ..tasks import finish_building
from main.celery_app import app

# def get_build(player, building_id):
#     return next((b for b in player["buildings"] if b["building_id"] == building_id), None)


def get_build(player, building_id):
    for building in player["buildings"]:
        if building["building_id"] == building_id:
            return building
    return None

def has_enough_resources(player, cost):
    return all(player["resources"].get(r, 0) >= cost[r] for r in cost)

def deduct_resources(player, cost):
    for r in cost:
        player["resources"][r] -= cost[r]



def start_building(user_id, building_id):
    player = players.find_one({"user_id": user_id})
    building_data = buildings.find_one({"_id": building_id})
    player_building = next((b for b in player["buildings"] if b["building_id"] == building_id), None)

    if not player_building or player_building["status"] != "idle":
        raise Exception("Building already started or completed")

    # Check dependencies
    required = building_data.get("dependencies", [])
    completed = [b["building_id"] for b in player["buildings"] if b["status"] == "completed"]
    if not all(b in completed for b in required):
        raise Exception("Dependencies not met")

    # Check resources
    if not all(player["resources"].get(k, 0) >= building_data["cost"][k] for k in building_data["cost"]):
        raise Exception("Not enough resources")

    # Deduct resources
    for r in building_data["cost"]:
        player["resources"][r] -= building_data["cost"][r]

    # Schedule building
    now = int(time.time())
    duration = building_data["duration"]
    end_time = now + duration

    # Start Celery task and store task_id
    result = finish_building.apply_async(args=[user_id, building_id], countdown=duration)
    task_id = result.id

    players.update_one(
        {"user_id": user_id, "buildings.building_id": building_id},
        {
            "$set": {
                "resources": player["resources"],
                "buildings.$.status": "in_progress",
                "buildings.$.started_at": now,
                "buildings.$.duration": duration,
                "buildings.$.end_time": end_time,
                "buildings.$.task_id": task_id
            }
        }
    )




def accelerate_building(user_id, building_id, reduce_by_secs):
    player = players.find_one({"user_id": user_id})
    building = next((b for b in player["buildings"] if b["building_id"] == building_id), None)

    if not building or building["status"] != "in_progress":
        raise Exception("Building not in progress")

    now = int(time.time())
    started_at = building.get("started_at")
    duration = building.get("duration")
    old_task_id = building.get("task_id")

    if not started_at or not duration:
        raise Exception("Missing timing data")

    time_passed = now - started_at
    time_remaining = duration - time_passed

    new_remaining = max(0, time_remaining - reduce_by_secs)

    if old_task_id:
        app.control.revoke(old_task_id, terminate=True)

    if new_remaining == 0:
        # Instantly complete
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
    else:
        new_end_time = now + new_remaining
        res = finish_building.apply_async(args=[user_id, building_id], countdown=new_remaining)

        players.update_one(
            {"user_id": user_id, "buildings.building_id": building_id},
            {
                "$set": {
                    "buildings.$.task_id": res.id,
                    "buildings.$.started_at": now,
                    "buildings.$.duration": new_remaining,
                    "buildings.$.end_time": new_end_time
                }
            }
        )