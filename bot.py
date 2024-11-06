import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext
from master import master_conversation_handler
from player import player_application_conversation_handler, player_search_conversation_handler

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

SELECTION, PLAYER_ACTIONS = range(2)

async def start(update: Update, context: CallbackContext) -> None:
    print('Start clicked')
    reply_keyboard = [
        [
            "Мастер",
            "Игрок"
        ]
    ]
    await update.message.reply_text(
        'Выбери кто ты?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return SELECTION


async def choose_player_actions(update: Update, context: CallbackContext) -> None:
    print("choose_action() called")
    print(update.message.text)

    reply_keyboard = [
        [
            "Поиск", "Заявка"
        ]
    ]
    await update.message.reply_text(
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
        text="Что хочешь сделать?"
    )
    return PLAYER_ACTIONS


async def cancel(update: Update, context: CallbackContext) -> int:
    """End the conversation."""
    await update.message.reply_text('Пока! Надеюсь, скоро снова пообщаемся.')
    return ConversationHandler.END


if __name__ == '__main__':
    application = Application.builder().token('7530680667:AAFFJ6SxFOcji0z0Aug4xbNaPtzznJ-QSG8').build()

    selection_handlers = [
        master_conversation_handler,
        MessageHandler(filters.Regex('^Игрок'), choose_player_actions)
    ]

    player_selections = [
        player_search_conversation_handler,
        player_application_conversation_handler
    ]

    # Main conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTION: selection_handlers,
            PLAYER_ACTIONS: player_selections
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)
    application.run_polling()
