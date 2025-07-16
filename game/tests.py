from django.test import TestCase, Client
from django.contrib.auth.models import User
from pymongo import MongoClient
from bson import ObjectId


class BuildingGameViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mongo = MongoClient("mongodb://localhost:27017/")
        cls.db = cls.mongo["game_db"]  # Adjust to your actual DB name
        cls.players = cls.db["players"]
        cls.buildings = cls.db["buildings"]

    def setUp(self):
        self.client_django = Client()
        self.user = User.objects.create_user(username="testuser", password="123456")
        self.client_django.login(username="testuser", password="123456")

        # Insert test player
        self.players.insert_one({
            "user_id": self.user.id,
            "resources": {"wood": 200, "stone": 200},
            "buildings": []
        })

        # Insert one building in the MongoDB
        self.building_id = self.buildings.insert_one({
            "name": "b1",
            "duration": 300,
            "cost": {"wood": 50, "stone": 50}
        }).inserted_id

    def tearDown(self):
        self.players.delete_many({})
        self.buildings.delete_many({})

    def test_player_info(self):
        response = self.client_django.get("/game/player/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("resources", data)
        self.assertIn("buildings", data)

    def test_build_start_success(self):
        response = self.client_django.post(
            "/game/build/start/",
            data={"building_id": str(self.building_id)}
        )
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "Building started")

        player = self.players.find_one({"user_id": self.user.id})
        self.assertEqual(len(player["buildings"]), 1)
        self.assertEqual(player["resources"]["wood"], 150)
        self.assertEqual(player["resources"]["stone"], 150)

    # def test_build_start_insufficient_resources(self):
    #     self.players.update_one(
    #         {"user_id": self.user.id},
    #         {"$set": {"resources": {"wood": 10, "stone": 10}}}
    #     )
    #
    #     response = self.client_django.post(
    #         "/build/start/",
    #         data={"building_id": str(self.building_id)}
    #     )
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("error", response.json())
    #
    #     player = self.players.find_one({"user_id": self.user.id})
    #     self.assertEqual(len(player["buildings"]), 0)
    #
    # def test_buildings_list(self):
    #     response = self.client_django.get("/buildings/")
    #     self.assertEqual(response.status_code, 200)
    #     data = response.json()
    #     self.assertIn("buildings", data)
    #     self.assertEqual(len(data["buildings"]), 1)
