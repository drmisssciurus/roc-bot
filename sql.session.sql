CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    players_count INTEGER,
    system TEXT,
    setting TEXT,
    game_type TEXT CHECK(game_type IN ('Компания', 'Ваншот', 'Модуль')),
    time TEXT,
    cost INTEGER,
    experience TEXT,
    free_text TEXT,
    master_id TEXT,
    FOREIGN KEY (master_id) REFERENCES masters(telegram_name)
);