import re
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters
from database.db_connectior import db, keys_map

#  States

game_type = range(1)


async def start_player_conversation(update: Update, context: CallbackContext) -> None:
    query = """
            SELECT DISTINCT game_type FROM games
            """
    result = db.execute_query(query)
    keyboard = [item[0] for item in result]
    question_keyboard = [keyboard]
    await update.message.reply_text(
        'Привет Игрок! Выбери что ты ищешь?',
        reply_markup=ReplyKeyboardMarkup(
            question_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return game_type


async def get_game_type(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    # context.user_data["game_type"] = update.message.text
    player_selection = [update.message.text]
    print(player_selection)
    query = """
            SELECT master_id, players_count, system, setting, game_type, time, cost, experience, free_text FROM games WHERE game_type=?
            """
    result = db.execute_query(query, tuple(player_selection))
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

player_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('player', start_player_conversation)],
    states={
        game_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_game_type)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
