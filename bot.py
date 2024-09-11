import logging
from master import master_conv_handler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext


# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция обработки команды /start


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     reply_keyboard = [
#         [
#             InlineKeyboardButton("Master", callback_data='master'),
#             InlineKeyboardButton("Player", callback_data='player')
#         ]
#     ]
#     await update.message.reply_text(
#         'Выбери кто ты?',
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard, one_time_keyboard=True, resize_keyboard=True
#         ),
#     )


def main() -> None:
    application = Application.builder().token(
        "7530680667:AAFFJ6SxFOcji0z0Aug4xbNaPtzznJ-QSG8").build()

    application.add_handler(master_conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
