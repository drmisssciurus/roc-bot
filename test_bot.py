import logging
import re

from telegram import Update, ReplyKeyboardMarkup, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext, \
    CallbackQueryHandler, Updater, ContextTypes

from bot import set_bot_commands
from database.db_connectior import keys_map, players_keys, db
from master import master_conversation_handler, chat_id
from player import player_application_conversation_handler, player_search_conversation_handler

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

state_0, state_1, master_id, players_count, system, setting, game_type, time, cost, experience, free_text, player_actions, player_application, player_name, player_contact, player_game_type, system_type, player_time, price, player_free_text = range(
    20)


async def start(update: Update, context: CallbackContext) -> None:
    print('Start clicked')
    reply_keyboard = [
        [
            InlineKeyboardButton("Мастер", callback_data="master"),
            InlineKeyboardButton("Игрок", callback_data="player"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(reply_keyboard)
    await update.message.reply_text(
        'Выбери кто ты?',
        # in chat button
        reply_markup=reply_markup,
    )
    return state_0


async def first_selection(update: Update, context: CallbackContext):
    print("first_selection")
    query = update.callback_query
    await query.answer()
    if query.data == 'master':
        return await start_master_conversation(update, context)
    elif query.data == 'player':
        return await choose_player_actions(update, context)


async def start_master_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Start the conversation by asking for the master's Telegram nickname
    context.user_data.clear()
    await update.effective_message.reply_text('Привет Мастер! Напиши свой никнейм в телеграмме с @?',)
    # await update.message.reply_text(
    #     'Привет Мастер! Напиши свой никнейм в телеграмме с @?',
    # )
    return master_id


async def get_master_id(update: Update, context: CallbackContext) -> None:
    # Retrieve and validate the master's nickname
    print(update.message.text)
    if not update.effective_message.text.startswith('@'):
        await update.effective_message.reply_text(
            'Неверное имя пользователя, начните писать с @',
        )
        return master_id
    if not re.match(r'^@[A-Za-z0-9_]{5,}$', update.effective_message.text):
        await update.effective_message.reply_text(
            'Неверное имя пользователя, используйте латиницу',
        )
        return master_id
    context.user_data["master_id"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Сколько игроков тебе нужно?',
    )
    return players_count


async def get_players_count(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    if not re.match(r'^\s*\d+(-\d+)?$', update.message.text):
        await update.effective_message.reply_text(
            'Только цифры, например 4-5 и тд.',
        )
        return players_count
    # Save the players_count
    context.user_data["players_count"] = update.effective_message.text

    await update.effective_message.reply_text(
        'Какая у тебя система?',
    )
    return system


async def get_system(update: Update, context: CallbackContext) -> None:
    print(update.effective_message.text)

    context.user_data["system"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Какой у тебя сеттинг?',
    )
    return setting


async def get_setting(update: Update, context: CallbackContext) -> None:
    print(update.effective_message.text)

    context.user_data["setting"] = update.effective_message.text
    # question_keyboard = [
    #     ['Ваншот', 'Кампания', 'Модуль']]
    #

    reply_keyboard = [
        [
            InlineKeyboardButton("Ваншот", callback_data="Ваншот"),
            InlineKeyboardButton("Кампания", callback_data="Кампания"),
            InlineKeyboardButton("Модуль", callback_data="Модуль"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(reply_keyboard)
    await update.effective_message.reply_text(
        'Какой у тебя вид игры?',
        reply_markup=reply_markup,
    )

    return game_type


async def get_game_type(update: Update, context: CallbackContext) -> None:
    # print(update.effective_message.text)
    query = update.callback_query
    await query.answer()
    context.user_data["game_type"] = query.data
    # Чекнуть возможность добавить выбор даты
    await update.effective_message.reply_text(
        'Выбери время и место (дату напиши в формате ДД.ММ.ГГ)',
    )
    return time


async def get_time(update: Update, context: CallbackContext) -> None:
    print(update.effective_message.text)

    context.user_data["time"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Выбери стоимость своей игры',
    )
    return cost


async def get_cost(update: Update, context: CallbackContext) -> None:
    print(update.effective_message.text)

    context.user_data["cost"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Важен ли тебе опыт игроков',
    )
    return experience


async def get_experience(update: Update, context: CallbackContext) -> None:
    print(update.effective_message.text)

    context.user_data["experience"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Напиши описание своего сеттинга если есть',
    )
    return free_text


async def get_free_text(update: Update, context: CallbackContext) -> None:
    print(update.effective_message.text)

    context.user_data["free_text"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Спасибо! Ваш анонс принят.',
    )

    # Prepare a summary of the collected data
    output_string = ''
    for key, value in context.user_data.items():  # ("key", "value")
        output_string += keys_map[key] + ": " + value + '\n'
    # Send the summary back to the master
    await update.effective_message.reply_text(
        output_string,
    )

    # Send message with summary to main resiever
    await context.bot.send_message(chat_id, "Новый анонс получен:\n" + output_string)
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


async def handle_state_1_2(update: Update, context: CallbackContext):
    print('state_1_2')
    return ConversationHandler.END


async def choose_player_actions(update: Update, context: CallbackContext):
    print("player")
    reply_keyboard = [
        [
            InlineKeyboardButton("Поиск", callback_data="search"),
            InlineKeyboardButton("Заявка", callback_data="application"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(reply_keyboard)

    new_message_text = "Что хочешь сделать?"
    await update.callback_query.edit_message_text(text=new_message_text, reply_markup=reply_markup)

    return player_actions


async def second_selection(update: Update, context: CallbackContext):
    print("second_selection")
    if update.callback_query.data == 'application':
        return await start_player_application(update, context)
    else:
        return await handle_state_2_2(update, context)


async def start_player_application(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    print("start_player_conversation() called")
    context.user_data.clear()
    await update.effective_message.reply_text(
        "Как тебя зовут?"
    )

    return player_name


async def get_player_name(update: Update, context: CallbackContext) -> None:
    print("get_player_name() called")

    print(update.effective_message.text)

    context.user_data["player_name"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Как с тобой связаться?',
    )
    return player_contact


async def get_player_contact(update: Update, context: CallbackContext) -> None:
    print("get_player_contact() called")
    print(update.effective_message.text)

    context.user_data["contact"] = update.effective_message.text

    reply_keyboard = [
        [
            InlineKeyboardButton("Ваншот", callback_data="Ваншот"),
            InlineKeyboardButton("Кампания", callback_data="Кампания"),
            InlineKeyboardButton("Модуль", callback_data="Модуль"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(reply_keyboard)
    await update.effective_message.reply_text(
        'Какой тип игры?',
        reply_markup=reply_markup,
    )

    # context.user_data["contact"] = update.message.text
    # question_keyboard = [
    #     ['Ваншот', 'Кампания', 'Модуль']]
    # await update.message.reply_text(
    #     'Какой тип игры?',
    #     reply_markup=ReplyKeyboardMarkup(
    #         question_keyboard, one_time_keyboard=True, resize_keyboard=True
    #     ),
    # )

    return player_game_type


async def get_player_game_type(update: Update, context: CallbackContext) -> None:
    print("get_game_type() called")

    print(update.effective_message.text)

    context.user_data["game_type"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Какая система?',
    )
    return system_type


async def get_system_type(update: Update, context: CallbackContext) -> None:
    print("get_system_type() called")

    print(update.effective_message.text)

    context.user_data["system"] = update.effective_message.text
    await update.effective_message.reply_text(
        'В какое время тебе предпочтительнее?',
    )
    return player_time


async def get_player_time(update: Update, context: CallbackContext) -> None:
    print("get_time() called")

    print(update.effective_message.text)

    context.user_data["time"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Если есть предпочтения по цене напиши',
    )
    return price


async def get_price(update: Update, context: CallbackContext) -> None:
    print("get_price() called")

    print(update.effective_message.text)

    context.user_data["price"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Если есть какие-то пожелания, напиши',
    )
    return player_free_text


async def get_player_free_text(update: Update, context: CallbackContext) -> None:
    print("get_free_text() called")

    print(update.effective_message.text)

    context.user_data["free_text"] = update.effective_message.text
    await update.effective_message.reply_text(
        'Спасибо! Ваша заявка принята.',
    )
    # Prepare a summary of the collected data
    output_string = ''
    for key, value in context.user_data.items():  # ("key", "value")
        output_string += players_keys[key] + ": " + value + '\n'
    # Send the summary back to the master
    await update.effective_message.reply_text(
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


async def handle_state_2_2(update: Update, context: CallbackContext):
    print("state_2.2")
    return state_2_2_1


async def handle_state_2_2_1(update: Update, context: CallbackContext):
    print("state_2.2.1")
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    print("END")
    return ConversationHandler.END


if __name__ == '__main__':
    application = Application.builder().token(
        '7530680667:AAFFJ6SxFOcji0z0Aug4xbNaPtzznJ-QSG8').build()

    # Установка постоянных кнопок
    application.bot_data["on_startup"] = lambda: application.loop.create_task(
        set_bot_commands(application))

    """
    ta="oneshot"),
data="campaign")
ta="module"),
    
    """
    # Main conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            state_0: [CallbackQueryHandler(first_selection, pattern="^(master|player)$")],
            state_1: [CallbackQueryHandler(first_selection, pattern="^master")],
            master_id: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_master_id)],
            players_count: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_players_count)],
            system: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system)],
            setting: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_setting)],
            # game_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_game_type)],
            game_type: [CallbackQueryHandler(get_game_type, pattern="^(Ваншот|Кампания|Модуль)$")],
            time: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            cost: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cost)],
            experience: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
            free_text: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_free_text)],
            # state_1_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_state_1_2)],
            player_actions: [CallbackQueryHandler(second_selection, pattern="^(search|application)$")],
            player_application: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_player_application)],
            player_name: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_name)],
            player_contact: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_contact)],
            player_game_type: [CallbackQueryHandler(get_player_game_type, pattern="^(Ваншот|Кампания|Модуль)$")],
            system_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system_type)],
            player_time: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_time)],
            price: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            player_free_text: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_free_text)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)

    application.run_polling()
