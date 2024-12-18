import asyncio
import re
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from database.db_connectior import db, players_keys, keys_map

# Defining states for Application
player_name, contact, game_type, system, time, price, free_text = range(
    7)

# Define player search states
player_selection, search_type, search_system, search_price = range(4)


async def start_player_application(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    print("start_player_conversation() called")
    context.user_data.clear()
    await update.message.reply_text(
        "Как тебя зовут?"
    )

    return player_name


async def get_player_name(update: Update, context: CallbackContext) -> None:
    print("get_player_name() called")

    print(update.message.text)

    context.user_data["player_name"] = update.message.text
    await update.message.reply_text(
        'Как с тобой связаться?',
    )
    return contact


async def get_player_contact(update: Update, context: CallbackContext) -> None:
    print("get_player_contact() called")
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
    print("get_game_type() called")

    print(update.message.text)

    context.user_data["game_type"] = update.message.text
    await update.message.reply_text(
        'Какая система?',
    )
    return system


async def get_system_type(update: Update, context: CallbackContext) -> None:
    print("get_system_type() called")

    print(update.message.text)

    context.user_data["system"] = update.message.text
    await update.message.reply_text(
        'В какое время тебе предпочтительнее?',
    )
    return time


async def get_time(update: Update, context: CallbackContext) -> None:
    print("get_time() called")

    print(update.message.text)

    context.user_data["time"] = update.message.text
    await update.message.reply_text(
        'Если есть предпочтения по цене напиши',
    )
    return price


async def get_price(update: Update, context: CallbackContext) -> None:
    print("get_price() called")

    print(update.message.text)

    context.user_data["price"] = update.message.text
    await update.message.reply_text(
        'Если есть какие-то пожелания, напиши',
    )
    return free_text


async def get_free_text(update: Update, context: CallbackContext) -> None:
    print("get_free_text() called")

    print(update.message.text)

    context.user_data["free_text"] = update.message.text
    await update.message.reply_text(
        'Спасибо! Ваша заявка принята.',
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


async def get_show_all(update: Update, context: CallbackContext) -> None:
    print("get_show_all() called")

    if update.message.text == "Покажи мне все":
        list_player = get_game_announcement()
        await update.message.reply_text(
            '\n\n'.join(list_player),
        )
        return ConversationHandler.END
    # else:
    #     return ConversationHandler.END
    return None


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


async def start_search_conversation(update: Update, context: CallbackContext) -> None:
    print("start_search_conversation")
    question_keyboard = [
        ['Покажи мне все игры', 'Я хочу выбрать по фильтру']]
    await update.message.reply_text(
        'Выбери вариант:',
        reply_markup=ReplyKeyboardMarkup(
            question_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return player_selection


async def get_selection(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    if update.message.text == "Покажи мне все игры":
        list_player = get_game_announcement()
        await update.message.reply_text(
            '\n\n'.join(list_player),
        )
        return ConversationHandler.END
    else:
        question_keyboard = [
            ['Ваншот', 'Кампания', 'Модуль']]
        await update.message.reply_text(
            "Выбери тип игры:",
            reply_markup=ReplyKeyboardMarkup(
                question_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return search_type


async def get_search_type(update: Update, context: CallbackContext) -> None:
    print(update.message.text)
    context.user_data["game_type"] = player_choise_type = update.message.text
    query = """
            SELECT DISTINCT system FROM games WHERE game_type=?
            """
    result = db.execute_query(query, (player_choise_type,))

    if not result:
        await update.message.reply_text(
            "Ничего не найдено по указанным параметрам. Попробуйте изменить фильтр."
        )
        return ConversationHandler.END

    buttons = []
    for system in result:
        buttons.append(system[0])
    print(buttons)
    question_keyboard = [buttons]
    await update.message.reply_text(
        "Какая система?",
        reply_markup=ReplyKeyboardMarkup(
            question_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return search_system


async def get_search_system(update: Update, context: CallbackContext) -> None:
    print(update.message.text)
    context.user_data["game_system"] = player_choise_system = update.message.text
    query = """
            SELECT DISTINCT cost FROM games WHERE game_type=? AND system=? ORDER BY cost ASC;
            """
    result = db.execute_query(
        query, (context.user_data["game_type"], player_choise_system))
    print(result)

    buttons = []
    for cost in result:
        buttons.append(str(cost[0]))
    print(buttons)
    question_keyboard = [buttons]
    await update.message.reply_text(
        "Какая стоимость?",
        reply_markup=ReplyKeyboardMarkup(
            question_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return search_price


async def get_search_price(update: Update, context: CallbackContext) -> None:
    print("get_search_price: " + update.message.text)
    player_choise_price = update.message.text
    query = """
            SELECT master_id, players_count, system, setting, game_type, time, cost, experience, free_text FROM games WHERE game_type=? AND system=? AND cost=?;
            """
    result = db.execute_query(
        query, (context.user_data["game_type"], context.user_data["game_system"], player_choise_price))
    print(result)

    list_player = []
    for game in result:
        temp_string = ''
        for i, key in enumerate(keys_map):
            temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
        list_player.append(temp_string)
    print(result)
    await update.message.reply_text(
        '\n\n'.join(list_player),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """End the conversation."""
    await update.message.reply_text('Пока! Надеюсь, скоро снова пообщаемся.')
    return ConversationHandler.END


player_application_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        start_player_application, pattern="^search$",)],
    states={
        player_name: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_name)],
        contact: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_contact)],
        game_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_game_type)],
        system: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system_type)],
        time: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        price: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
        free_text: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_free_text)],

    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

player_search_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        start_search_conversation, pattern="^search$",)],
    # MessageHandler(filters.Regex(
    # '^search'), start_search_conversation)],
    states={
        player_selection: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_selection)],
        search_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_search_type)],
        search_system: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_search_system)],
        search_price: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_search_price)],

    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
