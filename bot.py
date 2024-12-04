import logging
from telegram import Update, ReplyKeyboardMarkup, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
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
            InlineKeyboardButton("Мастер", callback_data="master"),
            InlineKeyboardButton("Игрок", callback_data="player"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(reply_keyboard)

    await update.message.reply_text(
        'Выбери кто ты?',
        # in chat button
        reply_markup=reply_markup,
        # in menu button
        # reply_markup=ReplyKeyboardMarkup(
        #     reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        # ),
    )
    return SELECTION

print(SELECTION)


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


async def set_bot_commands(application: Application) -> None:
    """Устанавливаем постоянные команды."""
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Помощь"),
        BotCommand("cancel", "Отмена текущего действия"),
    ]
    await application.bot.set_my_commands(commands)


async def handle_selection(update, context):
    query = update.callback_query
    await query.answer()  # Подтверждаем, что callback обработан

    if query.data == "master":
        # Запускаем master_conversation_handler
        await master_conversation_handler(update, context)
    elif query.data == "player":
        # Вызываем функцию для выбора игрока
        await choose_player_actions(update, context)

if __name__ == '__main__':
    application = Application.builder().token(
        '7530680667:AAFFJ6SxFOcji0z0Aug4xbNaPtzznJ-QSG8').build()

    # Установка постоянных кнопок
    application.bot_data["on_startup"] = lambda: application.loop.create_task(
        set_bot_commands(application))

    selection_handlers = [
        # master_conversation_handler,
        # CallbackQueryHandler(handle_selection, pattern="^(master|player)$"),
        MessageHandler(filters.Regex('^Мастер'), handle_selection),

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
    # application.add_handler(CallbackQueryHandler(
    #     handle_selection, pattern="^(master|player)$"))
    application.run_polling()
