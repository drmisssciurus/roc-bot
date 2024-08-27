import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция обработки команды /start


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [['Старт']]
    await update.message.reply_text(
        'Привет! Добро пожаловать в Бот RoC. Нажмите кнопку "Старт", чтобы продолжить.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )


# Обработчик кнопки "Старт"


async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == 'Старт':
        # Показываем вопрос и варианты ответа
        question_keyboard = [
            ['Я игрок, ищу something', 'Я мастер, ищу игроков']]
        await update.message.reply_text(
            'Выберите пожалуйста вариант:',
            reply_markup=ReplyKeyboardMarkup(
                question_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )

# Обработчик выбора вариантов ответа


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(update.message.text)
    if update.message.text in ['Я игрок, ищу something', 'Я мастер, ищу игроков']:
        await update.message.reply_text(f'Вы выбрали {update.message.text}. Спасибо за ваш ответ!')
    if update.message.text == 'Я игрок, ищу something':
        question_keyboard = [
            ['RPG', 'BoardGames']]
        await update.message.reply_text(
            'Выберите пожалуйста вариант:',
            reply_markup=ReplyKeyboardMarkup(
                question_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
    if update.message.text == 'RPG':
        question_keyboard = [
            ['RPG', 'BoardGames']]
        await update.message.reply_text(
            'Выберите пожалуйста вариант:',
            reply_markup=ReplyKeyboardMarkup(
                question_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )


# Обработчик выбора вариантов ответа игрока


# async def handle_player_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:


# async def handle_player_next_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:


def main() -> None:
    application = Application.builder().token(
        os.environ.get("BOT_TOKEN")).build()

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_start_button))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_answer))
    # application.add_handler(MessageHandler(
    #     filters.TEXT & ~filters.COMMAND, handle_player_answer))
    # application.add_handler(MessageHandler(
    #     filters.TEXT & ~filters.COMMAND, handle_player_next_answer))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
