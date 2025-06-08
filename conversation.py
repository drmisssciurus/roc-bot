import asyncio
import logging
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackContext, ContextTypes

from database.db_connectior import keys_map, players_keys, db
from config import CHAT_ID

# from player import player_application_conversation_handler, player_search_conversation_handler

# Включаем логирование
logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

state_0, state_1, master_id, master_actions, master_select, game_edit, game_name, editing_loop, game_display, editing_iteration_input, editing_iteration_finish, end_editing, players_count, system, setting, game_type, time, cost, experience, free_text, upload_image, player_actions, player_application, player_name, player_contact, player_game_type, system_type, player_time, price, player_free_text, player_selection, search_type, search_system, search_price = range(
	34)


async def start(update: Update, context: CallbackContext) -> int:
	print('Start clicked')  # TODO Restart logic
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


async def start_master_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	# Start the conversation by asking for the master's Telegram nickname
	context.user_data.clear()
	master_id = str(update.callback_query.from_user.username)
	print('masterID:' + master_id)
	context.user_data["master_id"] = master_id

	print('get_master_branch clicked')
	reply_keyboard = [
		[
			InlineKeyboardButton("Посмотреть свои заявки",
								 callback_data="master_applications"),
			InlineKeyboardButton("Создать новую заявку",
								 callback_data="new_master_application"),
		]
	]
	reply_markup = InlineKeyboardMarkup(reply_keyboard)
	await update.callback_query.edit_message_text(text=f'Привет {master_id}! Что ты хочешь сделать?',
												  reply_markup=reply_markup)

	return master_select


""" TODO: New branch
        1. First of all instead of requesting players count, ask what action is perform.
        2. if NEw game return players_count state. and go on
        3. Otherwise return <new_state>. then new conversation flow
"""


async def get_master_select(update: Update, context: CallbackContext):
	print('I am in get_master_select')
	query = update.callback_query
	await query.answer()

	if query.data == 'master_applications':
		query = """
                    SELECT game_name, game_id, players_count, system, setting, game_type, time, cost, experience, image_url, free_text FROM games
                    WHERE master_id=?
                    """
		# Execute a request with the selected game type parameter
		result = db.execute_query(query, (context.user_data["master_id"],))
		context.user_data['games'] = result
		buttons = []
		# Generating a list of games to display to the user as buttons
		for game in result:
			button = InlineKeyboardButton(
				game[0], callback_data='game-' + str(game[1]))
			buttons.append(button)
		reply_markup = InlineKeyboardMarkup([buttons])
		await update.effective_message.reply_text('Вот твои заявки!', reply_markup=reply_markup)
		return game_edit
	elif query.data == 'new_master_application':
		await update.callback_query.edit_message_text(text='Какое Название у твоей игры')
		#
		# await update.effective_message.reply_text(
		#     'Какое Название у твоей игры',
		# )
		return game_name

async def show_master_select(update: Update, context: CallbackContext):
	print('I am in show_master_select')
	query = update.callback_query
	context.user_data['game_to_edit'] = int(query.data[5:])
	game = None
	for item in context.user_data['games']:
		if item[1] == int(query.data[5:]):
			game = item
			print(game)
			break
	temp_string = ''
	image_url = None
	for i, key in enumerate(keys_map):
		if key != 'image_url':
			temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
		else:
			image_url = game[i]
	reply_keyboard = [
		[
			InlineKeyboardButton("Внести изменения",
								 callback_data="edit_game"),
			InlineKeyboardButton("Выйти",
								 callback_data="cancel_edit_game"),
		]
	]
	reply_markup = InlineKeyboardMarkup(reply_keyboard)
	await update.callback_query.edit_message_text(text=temp_string, reply_markup=reply_markup)
	return editing_loop

async def master_edit_game(update: Update, context: CallbackContext):
	print('I am in master_edit_game')
	def build_keyboard(button, n_per_row=2):
		return InlineKeyboardMarkup(
			[button[i:i + n_per_row] for i in range(0, len(button), n_per_row)]
		)
	buttons = [InlineKeyboardButton(key[1], callback_data=key[0]) for key in keys_map.items() if key[0] != 'master_id']
	reply_markup = build_keyboard(buttons)
	await update.effective_message.reply_text('Что изменить?', reply_markup=reply_markup)
	return editing_iteration_input

async def edit_game(update: Update, context: CallbackContext):
	print('I am in edit_game')
	query = update.callback_query.data
	await update.effective_message.reply_text('Введи новое значение:')
	context.user_data['value_to_edit'] = query
	return editing_iteration_finish

async def master_new_data(update: Update, context: CallbackContext):
	print('I am in master_new_data')
	query = f"""
    		UPDATE games
    		SET {context.user_data['value_to_edit']} = ?
    		WHERE game_id = ?;
			"""
	result = db.execute_query(query, (update.effective_message.text, context.user_data['game_to_edit']))
	print(result)
	return end_editing


async def get_game_name(update: Update, context: CallbackContext) -> int:
	print('im in get_game_name')
	context.user_data["game_name"] = update.effective_message.text
	await update.effective_message.reply_text(
		'Сколько игроков тебе нужно?',
	)
	return players_count


# TODO: паспечатать заявку полностью и кнопка с вопросом удалить(уверен что хочешь удалить) и
# TODO: обновить заявку- обновление по пунктам заявки?


async def get_players_count(update: Update, context: CallbackContext) -> int:
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


async def get_system(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["system"] = update.effective_message.text
	await update.effective_message.reply_text(
		'Какой у тебя сеттинг?',
	)
	return setting


async def get_setting(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["setting"] = update.effective_message.text
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


async def get_game_type(update: Update, context: CallbackContext) -> int:
	# print(update.effective_message.text)
	query = update.callback_query
	await query.answer()
	context.user_data["game_type"] = query.data
	# Чекнуть возможность добавить выбор даты
	await update.effective_message.reply_text(
		'Выбери время и место (дату напиши в формате ДД.ММ.ГГ)',
	)
	return time


async def get_time(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["time"] = update.effective_message.text
	await update.effective_message.reply_text(
		'Выбери стоимость своей игры',
	)
	return cost


async def get_cost(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["cost"] = update.effective_message.text
	await update.effective_message.reply_text(
		'Важен ли тебе опыт игроков',
	)
	return experience


async def get_experience(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["experience"] = update.effective_message.text
	await update.effective_message.reply_text(
		'Загрузи картинку если есть',
	)
	return upload_image


async def get_image_from_master(update: Update, context: CallbackContext) -> int:
	image = update.effective_message.photo[-1]
	file = await context.bot.get_file(image.file_id)
	await file.download_to_drive(f'./images/{image.file_id}.jpg')
	context.user_data["image_url"] = f'./images/{image.file_id}.jpg'
	await update.effective_message.reply_text(
		'Напиши описание своего сеттинга если есть',
	)
	return free_text


async def get_free_text(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["free_text"] = update.effective_message.text
	await update.effective_message.reply_text(
		'Спасибо! Ваш анонс принят.',
	)

	# Prepare a summary of the collected data
	output_string = ''
	for key, value in context.user_data.items():  # ("key", "value")
		if key != 'image_url':
			output_string += keys_map[key] + ": " + value + '\n'

	# Send the summary back to the master
	await update.effective_message.reply_photo(
		caption=output_string, photo=context.user_data['image_url']
	)

	# Send message with summary to main resiever
	await context.bot.send_message(CHAT_ID, "Новый анонс получен:\n" + output_string)
	# Insert the data into the database
	query = f"""
            INSERT INTO games (master_id, game_name, players_count, system, setting, game_type, time, cost, experience, image_url, free_text)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
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
		return await start_player_search(update, context)


async def start_player_application(update: Update, context: CallbackContext) -> int:
	query = update.callback_query
	query.answer()
	print("start_player_conversation() called")
	context.user_data.clear()
	await update.callback_query.edit_message_text(text="Как тебя зовут?")

	return player_name


async def get_player_name(update: Update, context: CallbackContext) -> int:
	print("get_player_name() called")

	print(update.effective_message.text)

	context.user_data["player_name"] = update.effective_message.text
	# await update.callback_query.edit_message_text(text="Как с тобой связаться?")
	await update.effective_message.reply_text(text="Как с тобой связаться?")
	return player_contact


async def get_player_contact(update: Update, context: CallbackContext) -> int:
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

	await update.message.reply_text(
		"Какой тип игры?",
		# in chat button
		reply_markup=reply_markup,
	)
	return player_game_type


async def get_player_game_type(update: Update, context: CallbackContext) -> int:
	print("get_game_type() called")

	print(update.effective_message.text)

	context.user_data["game_type"] = update.effective_message.text

	await update.callback_query.edit_message_text(text='Какая система?')
	return system_type


async def get_system_type(update: Update, context: CallbackContext) -> int:
	print("get_system_type() called")

	print(update.effective_message.text)

	context.user_data["system"] = update.effective_message.text
	await update.effective_message.reply_text(
		'В какое время тебе предпочтительнее?',
	)
	return player_time


async def get_player_time(update: Update, context: CallbackContext) -> int:
	print("get_time() called")

	print(update.effective_message.text)

	context.user_data["time"] = update.effective_message.text
	await update.effective_message.reply_text(
		'Если есть предпочтения по цене напиши',
	)
	return price


async def get_price(update: Update, context: CallbackContext) -> int:
	print("get_price() called")

	print(update.effective_message.text)

	context.user_data["price"] = update.effective_message.text
	await update.effective_message.reply_text(
		'Если есть какие-то пожелания, напиши',
	)
	return player_free_text


async def get_player_free_text(update: Update, context: CallbackContext) -> int:
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


async def start_player_search(update: Update, context: CallbackContext) -> int:

	print("start_search_conversation")
	question_keyboard = [
		[
			InlineKeyboardButton('Покажи мне все игры',
								 callback_data='Покажи мне все игры'),
			InlineKeyboardButton('Я хочу выбрать по фильтру',
								 callback_data='Я хочу выбрать по фильтру'),
		]
	]
	reply_markup = InlineKeyboardMarkup(question_keyboard)
	await update.effective_message.reply_text(
		'Выбери вариант:',
		reply_markup=reply_markup,
	)
	return player_selection


async def get_player_selection(update: Update, context: CallbackContext) -> int:

	query = update.callback_query
	# делает отдельные сообщения
	if query.data == 'Покажи мне все игры':
		# Предполагается, что это возвращает список строк
		list_player = get_game_announcement()
		# Отправляем каждую строку как отдельное сообщение
		for player in list_player:
			if player[1] is None:
				await update.effective_message.reply_text(str(player[0]))
			else:
				await update.effective_message.reply_photo(caption=str(player[0]), photo=player[1])
			await asyncio.sleep(0.5)
		return ConversationHandler.END
	else:
		question_keyboard = [
			[
				InlineKeyboardButton('Ваншот', callback_data='Ваншот'),
				InlineKeyboardButton('Кампания', callback_data='Кампания'),
				InlineKeyboardButton('Модуль', callback_data='Модуль'),
			]
		]
		reply_markup = InlineKeyboardMarkup(question_keyboard)
		await update.effective_message.reply_text(
			"Выбери тип игры:",
			reply_markup=reply_markup,
		)
		return search_type


def get_game_announcement() -> list:
	# Query to get games of the selected type from the database
	query = """
            SELECT master_id, players_count, system, setting, game_type, time, cost, experience, image_url, free_text FROM games
            """
	# Execute a request with the selected game type parameter
	result = db.execute_query(query)
	list_player = []
	# Generating a list of games to display to the user
	for game in result:
		temp_string = ''
		for i, key in enumerate(keys_map):
			if key != 'image_url':
				temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
			else:
				image_url = game[i]
		list_player.append((temp_string, image_url))
	print(result)
	# Sending a list of available games to the user
	# Ending the dialogue
	return list_player


async def get_search_type(update: Update, context: CallbackContext) -> int:
	print(update.callback_query.data)
	context.user_data["game_type"] = player_choise_type = update.callback_query.data
	query = """
            SELECT DISTINCT system FROM games WHERE game_type=?
            """
	result = db.execute_query(query, (player_choise_type,))

	if not result:
		await update.effective_message.reply_text(
			"Ничего не найдено по указанным параметрам. Попробуйте изменить фильтр."
		)
		return ConversationHandler.END

	buttons = []

	for system in result:
		button = InlineKeyboardButton(
			system[0], callback_data='system-' + system[0])
		buttons.append(button)

	print(buttons)
	reply_markup = InlineKeyboardMarkup([buttons])
	await update.effective_message.reply_text(
		"Какая система?",
		reply_markup=reply_markup,
	)
	return search_system


async def get_search_system(update: Update, context: CallbackContext) -> int:
	# print(update.effective_message.text)
	context.user_data["game_system"] = player_choise_system = update.callback_query.data[len(
		"system-"):]

	query = """
            SELECT DISTINCT cost FROM games WHERE game_type=? AND system=? ORDER BY cost ASC;
            """
	result = db.execute_query(
		query, (context.user_data["game_type"], player_choise_system))
	print(result)

	buttons = []

	for cost in result:
		button = InlineKeyboardButton(
			cost[0], callback_data='cost-' + str(cost[0]))
		buttons.append(button)

	print(buttons)
	reply_markup = InlineKeyboardMarkup([buttons])

	await update.effective_message.reply_text(
		"Какая стоимость?",
		reply_markup=reply_markup,
	)
	return search_price


async def get_search_price(update: Update, context: CallbackContext) -> int:
	# print("get_search_price: " + update.effective_message.text)
	player_choise_price = update.callback_query.data[len("cost-"):]
	query = """
            SELECT master_id, players_count, system, setting, game_type, time, cost, experience, free_text FROM games WHERE game_type=? AND system=? AND cost=?;
            """
	result = db.execute_query(
		query, (context.user_data["game_type"], context.user_data["game_system"], player_choise_price))
	print(result)

	list_player = []
	for game in result:
		temp_string = ''
		for i, key in enumerate(keys_map):
			temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
		list_player.append(temp_string)
	print(result)
	await update.effective_message.reply_text(
		'\n\n'.join(list_player),
	)
	return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
	print("END")
	return ConversationHandler.END


async def get_experience_with_image(update: Update, context: CallbackContext) -> int:
	# TODO: implement optional for user do not load the image
	if update.effective_message.photo:
		# Выбираем самое большое изображение (обычно последнее в списке)
		photo = update.effective_message.photo[-1]
		# Сохраняем file_id фотографии для дальнейшего использования
		context.user_data["experience_image"] = photo.file_id
		await update.effective_message.reply_text(
			"Картинка получена! Теперь напиши описание своего сеттинга, если есть."
		)
		# Переход к следующему состоянию (например, ожидание свободного текста)
		return free_text  # free_text – константа/метка для следующего шага диалога
	else:
		# Если фото не загружено, просим загрузить изображение
		await update.effective_message.reply_text(
			"Пожалуйста, загрузите картинку, используя функцию отправки фото."
		)
		# Можно вернуть текущий статус, чтобы бот продолжал ожидать загрузки картинки
		return 'kkk'
