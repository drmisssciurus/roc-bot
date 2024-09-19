import re
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ContextTypes
from database.db_connectior import db, keys_map

# Define conversation states

master_id, players_count, system, setting, game_type, time, cost, experience, free_text = range(
    9)


async def start_master_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Start the conversation by asking for the master's Telegram nickname

    await update.message.reply_text(
        'Привет Мастер! Напиши свой никнейм в телеграмме с @?',
    )
    return master_id


async def get_master_id(update: Update, context: CallbackContext) -> None:
    # Retrieve and validate the master's nickname
    print(update.message.text)
    if not update.message.text.startswith('@'):
        await update.message.reply_text(
            'Неверное имя пользователя, начните писать с @',
        )
        return master_id
    if not re.match(r'^@[A-Za-z0-9_]{5,}$', update.message.text):
        await update.message.reply_text(
            'Неверное имя пользователя, используйте латиницу',
        )
        return master_id
    context.user_data["master_id"] = update.message.text
    await update.message.reply_text(
        'Сколько игроков тебе нужно?',
    )
    return players_count


async def get_players_count(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    if not re.match(r'^\s*\d+(-\d+)?$', update.message.text):
        await update.message.reply_text(
            'Только цифры, например 4-5 и тд.',
        )
        return players_count
    # Save the players_count
    context.user_data["players_count"] = update.message.text

    await update.message.reply_text(
        'Какая у тебя система?',
    )
    return system


async def get_system(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["system"] = update.message.text
    await update.message.reply_text(
        'Какой у тебя сеттинг?',
    )
    return setting


async def get_setting(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["setting"] = update.message.text
    question_keyboard = [
        ['Ваншот', 'Кампания', 'Модуль']]
    await update.message.reply_text(
        'Какой у тебя вид игры?',
        reply_markup=ReplyKeyboardMarkup(
            question_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return game_type


async def get_game_type(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["game_type"] = update.message.text
    # Чекнуть возможность добавить выбор даты
    await update.message.reply_text(
        'Выбери время и место (дату напиши в формате ДД.ММ.ГГ)',
    )
    return time


async def get_time(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["time"] = update.message.text
    await update.message.reply_text(
        'Выбери стоимость своей игры',
    )
    return cost


async def get_cost(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["cost"] = update.message.text
    await update.message.reply_text(
        'Важен ли тебе опыт игроков',
    )
    return experience


async def get_experience(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["experience"] = update.message.text
    await update.message.reply_text(
        'Напиши описание своего сеттинга если есть',
    )
    return free_text


async def get_free_text(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["free_text"] = update.message.text
    await update.message.reply_text(
        'Спасибо! Ваш анонс принят.',
    )

    # Prepare a summary of the collected data
    output_string = ''
    for key, value in context.user_data.items():  # ("key", "value")
        output_string += keys_map[key] + ": " + value + '\n'
    # Send the summary back to the master
    await update.message.reply_text(
        output_string,
    )
    # Insert the data into the database
    query = f"""
            INSERT INTO games (master_id,  players_count, system, setting, game_type, time, cost, experience, free_text)
            VALUES (?,?,?,?,?,?,?,?,?)
            """
    try:
        db.execute_query(query, tuple(context.user_data.values()))
    except Exception as e:
        print(e)
    # End the conversation
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """End the conversation."""
    await update.message.reply_text('Пока! Надеюсь, скоро снова пообщаемся.')
    return ConversationHandler.END


master_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^Мастер'), start_master_conversation)],

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
