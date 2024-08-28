# print("Hello, World!");

# if 5 > 2:
#   print("Five is greater than two!") #Python uses indentation to indicate a block of code. Without them code didnt work

# """
# это
# многострочный
# комментарий
# """

# #Variables (Variable names are case-sensitive.)

# x = 5
# y = "John"
# print(x)
# print(y)

# x = 4       # x is of type int
# x = "Sally" # x is now of type str
# print(x)

# x = str(3)    # x will be '3'
# y = int(3)    # y will be 3
# z = float(3)  # z will be 3.0

# #Get the Type

# x = 5
# y = "John"
# print(type(x))
# print(type(y))

# #Legal variable names:

# myvar = "John"
# my_var = "John"
# _my_var = "John"
# myVar = "John"
# MYVAR = "John"
# myvar2 = "John"

# x, y, z = "Orange", "Banana", "Cherry"
# print(x)
# print(y)
# print(z)

# x = y = z = "Orange"
# print(x)
# print(y)
# print(z)

# fruits = ["apple", "banana", "cherry"]
# x, y, z = fruits
# print(x)
# print(y)
# print(z)


# #Slicing

# b = "Hello, World!"
# print(b[2:5])

# b = "Hello, World!"
# print(b[:5])

# b = "Hello, World!"
# print(b[2:])

# b = "Hello, World!"
# print(b[-5:-2]) #orl

def myFunc(e, i):
    return e * i


newFunc = myFunc(*(2, 3))
newFunc.extend([])

type(newFunc)


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
    logging.info(update.message.text)
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


# Обработчик выбора вариантов ответа мастера

async def handle_answer_master(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == 'Я мастер, ищу игроков':
        question_keyboard = [
            ['RPG', 'BoardGames']]
        await update.message.reply_text(
            'Выберите пожалуйста вариант:',
            reply_markup=ReplyKeyboardMarkup(
                question_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )


# async def handle_player_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:


# async def handle_player_next_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:


def main() -> None:
    application = Application.builder().token(
        os.environ.get("BOT_TOKEN")).build()

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.Regex('^Старт$'), handle_start_button))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_answer))
    # application.add_handler(MessageHandler(
    #     filters.TEXT & ~filters.COMMAND, handle_player_answer))
    # application.add_handler(MessageHandler(
    #     filters.TEXT & ~filters.COMMAND, handle_player_next_answer))

    # Запускаем бота
    application.run_polling()
