# Code Review — Improvement Plan

Bot: Telegram TTRPG Game Finder  
Review scope: full codebase (clean working tree, no uncommitted changes)

---

## Summary

8 issues found across 4 files. 2 are security/correctness bugs that will cause real failures in production. 4 are bugs that affect specific user flows. 2 are dead code or configuration problems.

---

## Issues

### 1. SQL Injection via Column Name (CRITICAL)

**File:** [conversation.py:365](conversation.py#L365)

```python
query = f"""
        UPDATE games
        SET {context.user_data['value_to_edit']} = %s
        WHERE game_id = %s;
        """
```

**What's wrong:** The column name is taken from `context.user_data['value_to_edit']`, which was set directly from `update.callback_query.data` (line 339). Telegram's callback data is sent from the user's client — a technically savvy user can send crafted callback data like `cost = 0; DROP TABLE games; --`. The column name is interpolated into the f-string before the parameterized `%s` binding runs, so it bypasses MySQL's parameter escaping entirely.

**Fix:** Validate `value_to_edit` against an explicit allowlist of column names before building the query.

```python
ALLOWED_EDIT_COLUMNS = {
    'game_name', 'players_count', 'system_name', 'setting',
    'game_type', 'game_time', 'cost', 'experience', 'image_url', 'free_text'
}

col = context.user_data['value_to_edit']
if col not in ALLOWED_EDIT_COLUMNS:
    await update.effective_message.reply_text("Неверное поле.")
    return ConversationHandler.END
```

---

### 2. Missing `await` on `query.answer()` (HIGH)

**File:** [conversation.py:824](conversation.py#L824)

```python
query = update.callback_query
query.answer()   # <-- coroutine created but never awaited
```

**What's wrong:** `query.answer()` is an async method that returns a coroutine. Without `await`, the coroutine is created and immediately discarded. Telegram never receives the acknowledgement, so the inline button shows a spinning loading indicator indefinitely for any user who taps "Заявка". Python may emit a `RuntimeWarning: coroutine was never awaited` in logs.

**Fix:**
```python
await query.answer()
```

---

### 3. `time.sleep()` Blocks the Async Event Loop (HIGH)

**Files:** [conversation.py:188](conversation.py#L188), [conversation.py:283](conversation.py#L283)

```python
time.sleep(3)   # line 188 — inside async def get_master_select
time.sleep(1)   # line 283 — inside async def show_master_application
```

**What's wrong:** `time.sleep()` is the synchronous standard-library call. Inside an `async def` function it does not yield control back to the event loop — it freezes the entire asyncio runtime for every user connected to the bot. While one master has no applications, every other user's button press or message sits frozen for 3 seconds.

**Fix:** Replace both with the async equivalent:
```python
await asyncio.sleep(3)   # requires: import asyncio at top of file
await asyncio.sleep(1)
```

---

### 4. `get_search_price` Has No Return in the Success Path (HIGH)

**File:** [conversation.py:1295](conversation.py#L1295)

```python
async def get_search_price(update: Update, context: CallbackContext) -> int:
    try:
        ...
        for game in result:
            ...
            os.remove(image_url)
        # function falls off here — returns None
    except (Exception) as e:
        ...
        return ConversationHandler.END
```

**What's wrong:** The `return ConversationHandler.END` was commented out (line 1296-1297). When the success path completes, Python returns `None`. `python-telegram-bot` interprets `None` as "no state change", so the conversation stays frozen in the current state and re-processes all future input through `get_search_price` indefinitely. The "← Назад" button is never shown to navigate back.

**Fix:** Add an explicit return after the for-loop:
```python
        for game in result:
            ...
            os.remove(image_url)
        return ConversationHandler.END
```
Or if the "Back" button with `reply_markup` was intended to be shown, add it and return the appropriate state.

---

### 5. INSERT Uses `user_data.values()` Directly — Fragile Column Order (MEDIUM)

**File:** [conversation.py:759](conversation.py#L759)

```python
db.execute_query(query, tuple(context.user_data.values()))
```

The INSERT query expects 11 values in this exact order:
`master_id, game_name, players_count, system_name, setting, game_type, game_time, cost, experience, image_url, free_text`

**What's wrong:** `context.user_data` is a plain dict built up across 11 handler calls. If the user ever went through the editing flow first (which sets `game_to_edit`, `value_to_edit`), those extra keys persist when a master starts creating a new game. The tuple will have 13 values instead of 11, the query fails with a parameter count mismatch, and the `except` at line 760 silently swallows it with a `print()` — the bot tells the user the game was created when it was not.

**Fix:** Build the tuple explicitly from named keys:
```python
values = (
    context.user_data["master_id"],
    context.user_data["game_name"],
    context.user_data["players_count"],
    context.user_data["system_name"],
    context.user_data["setting"],
    context.user_data["game_type"],
    context.user_data["game_time"],
    context.user_data["cost"],
    context.user_data["experience"],
    context.user_data["image_url"],
    context.user_data["free_text"],
)
db.execute_query(query, values)
```

Also call `context.user_data.clear()` at the start of the new-game flow (`new_master_application` branch in `get_master_select`).

---

### 6. `set_bot_commands` Is Never Actually Called (MEDIUM)

**File:** [main.py:97](main.py#L97)

```python
application.bot_data["on_startup"] = lambda: application.loop.create_task(set_bot_commands(application))
```

**What's wrong:** `python-telegram-bot` v21 does not call `bot_data["on_startup"]` automatically — this is not a recognized framework lifecycle hook. The lambda is stored but never invoked, so `/start`, `/help`, `/faq`, and `/cancel` are never registered with Telegram via `set_my_commands`. Users do not see these commands in the Telegram command menu.

Additionally, `Application` in PTB v21 has no `.loop` attribute, so if the lambda were ever called it would crash with `AttributeError`.

**Fix:** Use the supported `post_init` callback:
```python
async def post_init(application: Application) -> None:
    await set_bot_commands(application)

application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
```
Remove the `bot_data["on_startup"]` line.

---

### 7. `get_game_announcement()` in `utils.py` References Undefined Names (LOW)

**File:** [utils.py:31](utils.py#L31)

```python
def get_game_announcement() -> list:
    result = db.execute_query(query)    # db not imported in utils.py
    for game in result:
        for i, key in enumerate(keys_map):  # keys_map not imported in utils.py
```

**What's wrong:** `db` and `keys_map` are defined in `database/db_connectior.py`, not in `utils.py`. Calling this function raises `NameError` immediately. The function duplicates game-list logic that already exists in `conversation.py`, and appears to be leftover code that was not cleaned up.

**Fix:** Delete the function from `utils.py`. It is not called anywhere.

---

### 8. FAQ Character Limits Don't Match the Code (LOW)

**File:** [main.py:74](main.py#L74)

```
# Количество игроков: 3
# System - 20 
# Сеттинг - 20 
# Время - 32
# Стоимость: 20
```

**What's wrong:** Actual limits enforced in the handlers are: system=100 chars, setting=100 chars, time=50 chars, cost=50 chars. The FAQ shows outdated values from an earlier version. Users who rely on the FAQ to understand limits may be confused when input that should be fine is rejected, or vice versa.

**Fix:** Update the FAQ to match the actual validation in `conversation.py`:
```
# Название игры: 100
# Количество игроков: 10
# Система: 100
# Сеттинг: 100
# Время: 50
# Стоимость: 50
# Опыт игроков: 100
# Описание: 3500
```

---

## Priority Order

| # | Severity | File | Description |
|---|---|---|---|
| 1 | CRITICAL | conversation.py:365 | SQL injection via column name f-string |
| 2 | HIGH | conversation.py:824 | Missing `await` on `query.answer()` |
| 3 | HIGH | conversation.py:188, 283 | `time.sleep()` blocking async event loop |
| 4 | HIGH | conversation.py:1295 | `get_search_price` missing return — conversation freezes |
| 5 | MEDIUM | conversation.py:759 | INSERT built from `user_data.values()` — wrong order/count |
| 6 | MEDIUM | main.py:97 | `set_bot_commands` never called; `application.loop` doesn't exist |
| 7 | LOW | utils.py:31 | Dead function references undefined `db` and `keys_map` |
| 8 | LOW | main.py:74 | FAQ shows wrong character limits |

---

## Quick Wins (can fix in one sitting)

Issues 2, 3, 4, 7, 8 require only 1–3 line changes each. Fix those first — they're safe, contained, and have no side effects.

Issue 1 (SQL injection) and Issue 6 (post_init) require slightly more restructuring but are also straightforward.

Issue 5 (INSERT column ordering) is the most careful change — it touches the happy path of the master game creation flow and should be tested end-to-end after.
