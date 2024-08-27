CREATE TABLE IF NOT EXISTS masters (
    telegram_name TEXT PRIMARY KEY,
    master_name TEXT,
    master_nickname TEXT
);

CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT CHECK(type IN ('rpg', 'board')),  -- Enum-like constraint
    genre TEXT,
    setting TEXT,
    system TEXT,
    location TEXT,
    cost INTEGER,
    time TEXT,
    master_id TEXT,
    FOREIGN KEY (master_id) REFERENCES masters(telegram_name)
);