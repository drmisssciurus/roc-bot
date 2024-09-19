import re
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from database.db_connectior import db, keys_map

# Defining states for ConversationHandler

game_type = range(1)


async def start_player_conversation(update: Update, context: CallbackContext) -> None:
    # Query to get unique game types from the database
    query = """
            SELECT DISTINCT game_type FROM games
            """
    # Execute the query and get the results
    result = db.execute_query(query)
    # Forming a keyboard with game type options
    keyboard = [item[0] for item in result]
    question_keyboard = [keyboard]
    # Sending a message to the user asking them to select a game type
    await update.message.reply_text(
        'Привет Игрок! Выбери что ты ищешь?',
        reply_markup=ReplyKeyboardMarkup(
            question_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    # Move to the next dialog state
    return game_type


async def get_game_type(update: Update, context: CallbackContext) -> None:
    print(update.message.text)

    # Get the user's selected game type
    # context.user_data["game_type"] = update.message.text
    player_selection = [update.message.text]
    print(player_selection)

    # Query to get games of the selected type from the database
    query = """
            SELECT master_id, players_count, system, setting, game_type, time, cost, experience, free_text FROM games WHERE game_type=?
            """
    # Execute a request with the selected game type parameter
    result = db.execute_query(query, tuple(player_selection))
    list_player = []
    # Generating a list of games to display to the user
    for game in result:
        temp_string = ''
        for i, key in enumerate(keys_map):
            temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
        list_player.append(temp_string)
    print(result)
    # Sending a list of available games to the user
    await update.message.reply_text(
        '\n\n'.join(list_player),
    )
    # Ending the dialogue
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """End the conversation."""
    await update.message.reply_text('Пока! Надеюсь, скоро снова пообщаемся.')
    return ConversationHandler.END

# Define a dialog handler for the player
player_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^Игрок'), start_player_conversation)],
    states={
        game_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_game_type)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
