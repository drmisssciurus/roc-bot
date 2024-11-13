import logging
from master import master_conv_handler, start_master_conversation
from player import player_conv_handler, start_player_conversation
from telegram import Update, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext, CallbackQueryHandler, \
    MessageHandler, filters

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Функция обработки команды /start


async def start(update: Update, context: CallbackContext) -> None:
    print('Start clicked')
    reply_keyboard = [
        [
            InlineKeyboardButton("Мастер", callback_data='master'),
            InlineKeyboardButton("Игрок", callback_data='player')
        ]
    ]
    await update.message.reply_text(
        'Выбери кто ты?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )


def main() -> None:
    application = Application.builder().token(
        "7530680667:AAFFJ6SxFOcji0z0Aug4xbNaPtzznJ-QSG8").build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(master_conv_handler)
    application.add_handler(player_conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
