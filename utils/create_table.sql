CREATE TABLE IF NOT EXISTS masters (
    telegram_name TEXT PRIMARY KEY,
    master_name TEXT,
);

CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    players_count INTEGER,
    system TEXT,
    setting TEXT,
    type TEXT CHECK(type IN ('Компания', 'Ваншот', 'Модуль')),
    time TEXT,
    cost INTEGER,
    expirience TEXT,
    free_text,
    master_id TEXT,
    FOREIGN KEY (master_id) REFERENCES masters(telegram_name)
);



