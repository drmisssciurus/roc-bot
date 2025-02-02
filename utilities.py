# async def start(update: Update, context: CallbackContext) -> None:
#     print('Start clicked')
#     reply_keyboard = [
#         [
#             InlineKeyboardButton("Мастер", callback_data='master'),
#             InlineKeyboardButton("Игрок", callback_data='player')
#         ]
#     ]
#     await update.message.reply_text(
#         'Выбери кто ты?',
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard, one_time_keyboard=True, resize_keyboard=True
#         ),
#     )
