# ROC Bot — TTRPG Game Finder

A Telegram bot that connects tabletop RPG game masters with players. Masters post game announcements; players search and apply. Built in Python using `python-telegram-bot`.

---

## Features

### For Game Masters
- Create game announcements with 11 fields: title, player count, system, setting, type, schedule, cost, experience requirements, description, and a cover image
- Edit or delete existing announcements at any time
- View player applications submitted through the bot

### For Players
- Browse all available games or filter by game type, system, or price
- View full game details with cover images
- Submit a player profile (name, contact, preferences, experience)

### Admin
- Three configurable admin accounts receive automatic Telegram notifications whenever a game is created or updated

---

## Tech Stack

| Layer | Technology |
|---|---|
| Bot framework | `python-telegram-bot` 21.5 |
| Database | MySQL (`mysql-connector-python`) |
| Image storage | Google Cloud Storage |
| Config | `python-dotenv` |
| Language | Python 3.11+ (async/await) |

---

## Project Structure

```
roc-bot/
├── main.py              # Bot entry point, command registration, ConversationHandler
├── conversation.py      # All conversation state handlers (~1300 lines)
├── states.py            # Integer constants for each conversation state (28 states)
├── formatters.py        # Formats database rows into human-readable text
├── utils.py             # Keyboard builder, SHA256 IDs, GCS upload/download
├── logger.py            # Logging setup
├── database/
│   ├── db_connectior.py # MySQL connection + query wrapper
│   └── models.py        # Game and Master data model classes
├── tests/
│   ├── test_handlers.py
│   └── handlers/test_start.py
├── logs/error.log
└── requirements.txt
```

---

## Conversation Flow

The bot has two top-level branches selected at `/start`:

```
/start
├── 🧙 Мастер (Game Master)
│   ├── Create new game  →  11 input steps  →  saved to DB + admin notified
│   ├── View my games
│   │   └── Select game  →  Edit field / Delete
│   └── (back to role select)
│
└── 🗺 Игрок (Player)
    ├── Submit application  →  7 input steps  →  saved to DB
    └── Search games
        ├── Show all
        └── Filter by type / system / cost  →  paginated game cards
```

Conversations time out after **12 hours** of inactivity.

---

## Database Schema

### `games`
| Column | Type | Notes |
|---|---|---|
| `game_id` | INT PK AUTO | |
| `master_id` | VARCHAR | Telegram username |
| `game_name` | VARCHAR(100) | |
| `players_count` | VARCHAR(10) | |
| `system_name` | VARCHAR(100) | |
| `setting` | VARCHAR(100) | |
| `game_type` | VARCHAR | Ваншот / Кампания / Модуль |
| `game_time` | VARCHAR(50) | |
| `cost` | VARCHAR(50) | |
| `experience` | VARCHAR(100) | |
| `free_text` | TEXT(3500) | Full description |
| `image_url` | VARCHAR | GCS blob name |
| `created_at` | TIMESTAMP | |

### `players_requests`
| Column | Type | Notes |
|---|---|---|
| `request_id` | VARCHAR PK | SHA256 hash of player data |
| `player_name` | VARCHAR | |
| `contact` | VARCHAR | |
| `game_type` | VARCHAR | |
| `system_name` | VARCHAR | |
| `game_time` | VARCHAR | |
| `price` | VARCHAR | |
| `free_text` | TEXT | Experience & preferences |
| `created_at` | TIMESTAMP | |

---

## Configuration

The bot reads secrets from `config.py` (not committed). Create it with the following variables:

```python
# Telegram
BOT_TOKEN = "your-bot-token"
CHAT_ID   = "your-local-test-chat-id"

# Admin Telegram user IDs
dadjezz_id        = 123456789
igor_krivic_id    = 123456789
evgeniya_tiamat_id = 123456789

# MySQL
db_host     = "localhost"
db_port     = 3306
db_name     = "roc_bot"
db_user     = "root"
db_password = "secret"
```

Set the `IS_LOCAL` environment variable to `true` when running locally (controls GCS vs. local image paths).

Google Cloud credentials must be available via `GOOGLE_APPLICATION_CREDENTIALS` or Application Default Credentials. The bot uses bucket `roc_images` in project `articulate-bird-464515-n5`.

---

## Setup

```bash
# 1. Clone and create a virtual environment
git clone <repo-url>
cd roc-bot
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create config.py (see Configuration section above)

# 4. Run the bot
python main.py
```

---

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Launch the bot and pick a role |
| `/help` | Usage instructions |
| `/faq` | Field character limits and system info |
| `/cancel` | Cancel the current action |

---

## Running Tests

```bash
pytest tests/
```

Tests use `unittest.mock` and `pytest-asyncio` to unit-test conversation handlers without a live bot connection.
