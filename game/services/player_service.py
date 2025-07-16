from .db import players

def get_or_create_player(user_id):
    player = players.find_one({"user_id": user_id})
    if not player:
        buildings = [{"building_id": i, "status": "idle"} for i in range(1, 7)]
        player = {
            "user_id": user_id,
            "resources": {"wood": 500, "stone": 500},
            "buildings": buildings
        }
        players.insert_one(player)
    return player