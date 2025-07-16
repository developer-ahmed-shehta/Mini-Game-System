from django.test import TestCase
from django.contrib.auth.models import User
from game.services.db import players, buildings
from game.services.building_service import start_building,accelerate_building
import time

class BuildingGameViewTests(TestCase):
    def setUp(self):
        # Clean old test data
        buildings.delete_many({})
        players.delete_many({})
        # Create Django user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Insert building definition into Mongo
        buildings.insert_one({
            "_id": 1,
            "name": "b1",
            "duration": 300,  # 5 mins
            "cost": {"wood": 50, "stone": 50},
            "dependencies": []
        })

        # Insert player data into Mongo
        players.insert_one({
            "user_id": self.user.id,
            "resources": {"wood": 100, "stone": 100},
            "buildings": [
                {"building_id": 1, "status": "idle"}
            ]
        })

    def test_start_building_successfully(self):
        # Call your function
        start_building(self.user.id, 1)

        # Fetch updated player
        player = players.find_one({"user_id": self.user.id})
        building = next(b for b in player["buildings"] if b["building_id"] == 1)

        # Check building status
        self.assertEqual(building["status"], "in_progress")
        self.assertIn("started_at", building)
        self.assertIn("duration", building)
        self.assertIn("end_time", building)
        self.assertIn("task_id", building)

        # Check resources are deducted
        self.assertEqual(player["resources"]["wood"], 50)
        self.assertEqual(player["resources"]["stone"], 50)


class AccelerateBuildingTest(TestCase):
    def setUp(self):
        # Clean old test data
        buildings.delete_many({})
        players.delete_many({})

        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Insert building config
        buildings.insert_one({
            "_id": 1,
            "name": "b1",
            "duration": 300,  # 5 mins
            "cost": {"wood": 50, "stone": 50},
            "dependencies": []
        })

        # Player has resources and idle building
        players.insert_one({
            "user_id": self.user.id,
            "resources": {"wood": 100, "stone": 100},
            "buildings": [
                {"building_id": 1, "status": "idle"}
            ]
        })

    def test_accelerate_building_reduces_time(self):
        # Step 1: Start building
        start_building(self.user.id, 1)
        time.sleep(1)  # Give it 1 sec (simulate time passing)

        # Step 2: Accelerate by 200 seconds
        accelerate_building(self.user.id, 1, reduce_by_secs=200)

        # Step 3: Get updated player
        player = players.find_one({"user_id": self.user.id})
        building = next(b for b in player["buildings"] if b["building_id"] == 1)

        # Check that it's still in progress
        self.assertEqual(building["status"], "in_progress")

        # Check new remaining duration
        now = int(time.time())
        new_end = building["end_time"]
        self.assertLessEqual(new_end - now, 100)  # Should be ~100 seconds left

    def test_accelerate_to_complete(self):
        start_building(self.user.id, 1)
        time.sleep(1)

        # Accelerate by full duration → should complete
        accelerate_building(self.user.id, 1, reduce_by_secs=300)

        player = players.find_one({"user_id": self.user.id})
        building = next(b for b in player["buildings"] if b["building_id"] == 1)

        self.assertEqual(building["status"], "completed")
        self.assertNotIn("end_time", building)
