import re
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from database.db_connectior import db, players_keys, keys_map

# Defining states for ConversationHandler

selection, player_name, contact, game_type, system, time, price, free_text, search, show_all = range(
    10)


async def start_player_conversation(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()
    reply_keyboard = [
        [
            InlineKeyboardButton("Поиск", callback_data='search'),
            InlineKeyboardButton("Заявка", callback_data='request')
        ]
    ]
    await update.message.reply_text(
        'Привет Игрок! Выбери что ты хочешь?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return selection


async def get_player_selection(update: Update, context: CallbackContext) -> None:
    print(update.message.text)
    if update.message.text == "Заявка":
        await update.message.reply_text(
            'Напиши свое имя.',
        )
        return player_name
    else:
        return search


async def get_player_name(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["player_name"] = update.message.text
    await update.message.reply_text(
        'Как с тобой связаться?',
    )
    return contact


async def get_player_contact(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["contact"] = update.message.text
    question_keyboard = [
        ['Ваншот', 'Кампания', 'Модуль']]
    await update.message.reply_text(
        'Какой тип игры?',
        reply_markup=ReplyKeyboardMarkup(
            question_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return game_type


async def get_game_type(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["game_type"] = update.message.text
    await update.message.reply_text(
        'Какая система?',
    )
    return system


async def get_system_type(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["system"] = update.message.text
    await update.message.reply_text(
        'В какое время тебе предпочтительнее?',
    )
    return time


async def get_time(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["time"] = update.message.text
    await update.message.reply_text(
        'Если есть предпочтения по цене напиши',
    )
    return price


async def get_price(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    context.user_data["price"] = update.message.text
    await update.message.reply_text(
        'Если есть что сказать, скажи',
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
        output_string += players_keys[key] + ": " + value + '\n'
    # Send the summary back to the master
    await update.message.reply_text(
        output_string,
    )

    # Send message with summary to main resiever
    # await context.bot.send_message(chat_id, "Новый анонс получен:\n" + output_string)
    # Insert the data into the database
    query = f"""
            INSERT INTO players_requests (player_name, contact, game_type, system, time, price, free_text)
            VALUES (?,?,?,?,?,?,?)
            """
    try:
        db.execute_query(query, tuple(context.user_data.values()))
    except Exception as e:
        print(e)
    # End the conversation
    return ConversationHandler.END

# Player filter functions


async def get_player_search(update: Update, context: CallbackContext) -> None:
    print(update.message.text)
    reply_keyboard = [
        [
            InlineKeyboardButton("Покажи мне все", callback_data='all'),
            InlineKeyboardButton("Я хочу выбрать", callback_data='filter')
        ]
    ]
    await update.message.reply_text(
        'Выбери что ты хочешь?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return show_all


async def get_show_all(update: Update, context: CallbackContext) -> None:
    if update.message.text == "Покажи мне все":
        list_player = get_game_announcement()
        await update.message.reply_text(
            '\n\n'.join(list_player),
        )
        return ConversationHandler.END
    else:
        return player_filter


# async def start_player_conversation(update: Update, context: CallbackContext) -> None:
#     # Query to get unique game types from the database
#     query = """
#             SELECT DISTINCT game_type FROM games
#             """
#     # Execute the query and get the results
#     result = db.execute_query(query)
#     # Forming a keyboard with game type options
#     keyboard = [item[0] for item in result]
#     question_keyboard = [keyboard]
#     # Sending a message to the user asking them to select a game type
#     await update.message.reply_text(
#         'Привет Игрок! Выбери что ты ищешь?',
#         reply_markup=ReplyKeyboardMarkup(
#             question_keyboard, one_time_keyboard=True, resize_keyboard=True
#         ),
#     )
#     # Move to the next dialog state
#     return game_type


def get_game_announcement() -> None:
    # Query to get games of the selected type from the database
    query = """
            SELECT master_id, players_count, system, setting, game_type, time, cost, experience, free_text FROM games
            """
    # Execute a request with the selected game type parameter
    result = db.execute_query(query)
    list_player = []
    # Generating a list of games to display to the user
    for game in result:
        temp_string = ''
        for i, key in enumerate(keys_map):
            temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
        list_player.append(temp_string)
    print(result)
    # Sending a list of available games to the user
    # Ending the dialogue
    return list_player


async def cancel(update: Update, context: CallbackContext) -> int:
    """End the conversation."""
    await update.message.reply_text('Пока! Надеюсь, скоро снова пообщаемся.')
    return ConversationHandler.END

# Define a dialog handler for the player
player_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(
        '^Игрок'), start_player_conversation)],
    states={
        selection: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_selection)],
        player_name: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_name)],
        contact: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_contact)],
        game_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_game_type)],
        system: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system_type)],
        time: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        price: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
        free_text: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_free_text)],
        search: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_search)],
        show_all: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_show_all)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
