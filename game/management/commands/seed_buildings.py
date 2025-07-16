from django.core.management.base import BaseCommand
from game.services.db import buildings

class Command(BaseCommand):
    help = 'Seed buildings data into MongoDB'

    def handle(self, *args, **kwargs):
        data = [
            {"_id": 1, "name": "b1", "duration": 10, "cost": {"wood": 50, "stone": 50}, "dependencies": []},
            {"_id": 2, "name": "b2", "duration": 20, "cost": {"wood": 100, "stone": 100}, "dependencies": []},
            {"_id": 3, "name": "b3", "duration": 30, "cost": {"wood": 150, "stone": 150}, "dependencies": []},
            {"_id": 4, "name": "b4", "duration": 1000, "cost": {"wood": 200, "stone": 200}, "dependencies": [1, 2, 3]},
            {"_id": 5, "name": "b5", "duration": 50, "cost": {"wood": 250, "stone": 250}, "dependencies": [1, 2, 3, 4]},
            {"_id": 6, "name": "b6", "duration": 60, "cost": {"wood": 300, "stone": 300}, "dependencies": [1, 2, 3, 4, 5]},
        ]
        buildings.delete_many({})
        buildings.insert_many(data)
        self.stdout.write(self.style.SUCCESS("Buildings seeded!"))
