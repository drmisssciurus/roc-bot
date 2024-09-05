import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackContext
from db_connectior import DBConnector

db = DBConnector()

#  States

master_id, players_count, system, setting, game_type, time, cost, experience, free_text = range(
    9)

# Keys map

keys_map = {
    'master_id': 'Никнейм мастера',
    'players_count': 'Количество игроков',
    'system': 'Система',
    'setting': 'Сеттинг',
    'game_type': 'Тип игры',
    'time': 'Время',
    'cost': 'Стоимость',
    'experience': 'Опыт игроков',
    'free_text': '\n'
}

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция обработки команды /start


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет Мастер! Напиши свой никнейм в телеграмме с @?',
    )
    return master_id


async def get_master_id(update: Update, context: CallbackContext) -> None:
    context.user_data["master_id"] = update.message.text
    if not update.message.text.startswith('@'):
        await update.message.reply_text(
            'Неверное имя пользователя, начните писать с @',
        )
        return master_id
    await update.message.reply_text(
        'Сколько игроков тебе нужно?',
    )
    return players_count


async def get_players_count(update: Update, context: CallbackContext) -> None:
    context.user_data["players_count"] = update.message.text
    await update.message.reply_text(
        'Какая у тебя система?',
    )
    return system


async def get_system(update: Update, context: CallbackContext) -> None:
    context.user_data["system"] = update.message.text
    await update.message.reply_text(
        'Какой у тебя сеттинг?',
    )
    return setting


async def get_setting(update: Update, context: CallbackContext) -> None:
    context.user_data["setting"] = update.message.text
    # добавить кнопки!!!
    await update.message.reply_text(
        'Какой у тебя вид игры?',
    )
    return game_type


async def get_game_type(update: Update, context: CallbackContext) -> None:
    context.user_data["game_type"] = update.message.text
    # Чекнуть возможность добавить выбор даты
    await update.message.reply_text(
        'Выбери время и место',
    )
    return time


async def get_time(update: Update, context: CallbackContext) -> None:
    context.user_data["time"] = update.message.text
    await update.message.reply_text(
        'Выбери стоимость своей игры',
    )
    return cost


async def get_cost(update: Update, context: CallbackContext) -> None:
    context.user_data["cost"] = update.message.text
    await update.message.reply_text(
        'Важен ли тебе опыт игроков',
    )
    return experience


async def get_experience(update: Update, context: CallbackContext) -> None:
    context.user_data["experience"] = update.message.text
    await update.message.reply_text(
        'Если есть что сказать скажи сейчас или замолчи навсегда',
    )
    return free_text


async def get_free_text(update: Update, context: CallbackContext) -> None:
    context.user_data["free_text"] = update.message.text
    await update.message.reply_text(
        'Спасибо!',
    )
    output_string = ''
    for key, value in context.user_data.items():  # ("key", "value")
        output_string += keys_map[key] + ": " + value + '\n'
    await update.message.reply_text(
        output_string,
    )
    query = f"""
            INSERT INTO games (master_id,  players_count, system, setting, game_type, time, cost, experience, free_text)
            VALUES (?,?,?,?,?,?,?,?,?)
            """
    try:
        db.execute_query(query, tuple(context.user_data.values()))
    except Exception as e:
        print(e)

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """End the conversation."""
    update.message.reply_text('Bye! Hope to talk to you again soon.')
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(
        "PUT THERE CODE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            master_id: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_master_id)],
            players_count: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_players_count)],
            system: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system)],
            setting: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_setting)],
            game_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_game_type)],
            time: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            cost: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cost)],
            experience: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            free_text: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_free_text)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
