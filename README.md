
#  Mini Game Backend System

This is a backend for a building-style strategy game, built with Django, Celery, Redis, and MongoDB.

Players can:
 Start buildings
Accelerate building timers
 Consume resources (e.g., wood, stone)
 Handle building dependencies (e.g., Building 4 requires 2 and 3)

---

##  Tech Stack

- **Python 3.10+**
- **Django** – Main backend framework
- **MongoDB** – Stores player and building data
- **Celery** – Manages timers for building completion
- **Redis** – Celery broker and caching layer
- **Django Sessions** – Used for authentication

---

##  Quick Start

### 1. Clone the Project

```bash
git clone https://github.com/your-username/mini-game-system.git
cd mini-game-system
```

### 2. Install Dependencies

>  It's recommended to use a virtual environment

```bash
pip install -r requirements.txt
```

### 3. Start MongoDB & Redis

Make sure Redis and MongoDB are running:

```bash
# For Ubuntu/Debian
sudo service redis-server start
sudo service mongod start
```

---

##  Configuration

Edit or create `.env` or update settings manually:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=game_db
REDIS_URL=redis://localhost:6379
```

Set up your database clients inside:
- `game/services/db.py`
- `main/celery.py`

---

##  Run Tests

```bash
python manage.py test
```

---

## Running the App

### Start Django server:

```bash
python manage.py runserver
```

### Start Celery worker:
 for linux
```bash
celery -A main worker --loglevel=info
```
for windows 

```bash
celery -A main worker --pool=solo -l info
```

---

## API Overview

| Endpoint                                 | Method | Description                                |
|------------------------------------------|--------|--------------------------------------------|
| `/accounts/login/`                       | POST   | Login using username and password          |
| `/accounts/logout/`                      | GET    | Logout the current user                    |
| `/api/player/`                           | GET    | Get the current player's profile           |
| `/game/buildings/`                       | GET    | List all available buildings (assets)      |
| `/api/build/start/`                      | POST   | Start building construction                |
| `/game/build/accelerate/`                | POST   | Accelerate building time (`building_id`, `reduce_by`) |
| `/game/task-status/?task_id=...`         | GET    | Check status of a specific Celery task     |
| `/game/buildings/all_players/`           | GET    | List all players with their buildings      |

---

## 🧠 Player Logic Summary

- Each player has 6 buildings (IDs 1 to 6)
- Buildings 1–3 are open; 4–6 require dependencies
- Each building has:
  - `status`: idle / in_progress / completed
  - `started_at`, `duration`, `end_time`, `task_id`

