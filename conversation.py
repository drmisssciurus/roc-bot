import asyncio
import logging
import re
import time

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackContext, ContextTypes

from database.db_connectior import keys_map, players_keys, db
from config import CHAT_ID, evgeniya_tiamat_id, igor_krivic_id, dadjezz_id

# Включаем логирование
logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

from states import *


def build_keyboard(button, n_per_row=2):
	return InlineKeyboardMarkup(
		[button[i:i + n_per_row] for i in range(0, len(button), n_per_row)]
	)


async def start(update: Update, context: CallbackContext) -> int:
	print('Start clicked')
	# print(update.effective_message.from_user.username)
	# print(update.effective_message.from_user.id)
	logger.info('start function called')
	reply_keyboard = [
		[
			InlineKeyboardButton("Мастер", callback_data="master"),
			InlineKeyboardButton("Игрок", callback_data="player"),
		],

	]
	reply_markup = InlineKeyboardMarkup(reply_keyboard)
	await update.effective_message.reply_text(
		'Выбери кто ты?',
		reply_markup=reply_markup,
	)
	return initial_state


# async def back(update: Update, context: CallbackContext) -> int:
#

async def handle_role_selection(update: Update, context: CallbackContext):
	print("first_selection")
	query = update.callback_query
	await query.answer()
	if query.data == 'master':
		return await start_master_conversation(update, context)
	elif query.data == 'player':
		return await start_player_conversation(update, context)


async def start_master_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE, is_first_time=True) -> int:
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

		],
		[
			InlineKeyboardButton("Назад", callback_data="start_again"),
		]
	]
	reply_markup = InlineKeyboardMarkup(reply_keyboard)
	# await update.effective_message.edit_text(text=f'Привет {master_id}! Что ты хочешь сделать?',
	# 											  reply_markup=reply_markup)
	if is_first_time:
		await update.effective_message.edit_text(text=f'Привет {master_id}! Что ты хочешь сделать?',
												 reply_markup=reply_markup)
	else:
		await update.effective_message.reply_text(text=f'Вернулся {master_id}? Что ты теперь хочешь сделать?',
												  reply_markup=reply_markup)
	return master_selection


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
				SELECT game_name, game_id FROM games
				WHERE master_id=?
				"""
		# Execute a request with the selected game type parameter
		result = db.execute_query(query, (context.user_data["master_id"],))
		if result:
			buttons = []

			for game in result:
				button = InlineKeyboardButton(
					game[0], callback_data='game-' + str(game[1]))
				buttons.append(button)

			reply_markup = build_keyboard(buttons, n_per_row=1)


			await update.callback_query.edit_message_text('Вот твои заявки!', reply_markup=reply_markup)
			return game_editing
		else:
			await update.callback_query.edit_message_text('Не найдено ни одной игры =(')
			time.sleep(3)
			return await start_master_conversation(update, context, is_first_time=False)


	elif query.data == 'new_master_application':
		await update.callback_query.edit_message_text(
			text="✍️ Раз вы здесь и ищете авантюристов – значит, что-то стряслось? С каким делом гильдия может вам помочь? (_Укажите название грядущей игры_)",
			parse_mode="Markdown",
			# reply_markup=InlineKeyboardMarkup(
			# 	[
			# 		[
			# 			InlineKeyboardButton(text="Назад", callback_data="back_to_role_selection"),
			# 			# InlineKeyboardButton(text="Отмена", callback_data="cancel") # TODO Optional
			# 		]
			# 	]
			# )
		)

		return master_input_game_name


async def show_master_application(update: Update, context: CallbackContext, game_id=None):
	print('I am in show_master_select')
	if game_id is None:
		query = update.callback_query
		context.user_data['game_to_edit'] = int(query.data[5:])
	else:
		context.user_data['game_to_edit'] = game_id

	query = """
					SELECT
						game_name,
						players_count,
						system,
						setting,
						game_type,
						time,
						cost,
						experience,
						free_text,
						image_url 
					FROM games
					WHERE game_id=?
					"""

	game = db.execute_query(query, (context.user_data["game_to_edit"],))[0]

	keys = keys_map.copy()
	keys.pop('master_id')
	image_url = None
	temp_string = ''
	for i, key in enumerate(keys):
		if key != 'image_url':
			temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
		else:
			image_url = game[i]

	time.sleep(1)
	reply_keyboard = [
		[
			InlineKeyboardButton("Внести изменения",
								 callback_data="edit_game"),
			InlineKeyboardButton("Удалить заявку",
								 callback_data="delete_game"),
			InlineKeyboardButton("Выйти",
								 callback_data="cancel_edit_game"),
		]
	]
	reply_markup = InlineKeyboardMarkup(reply_keyboard)

	await update.effective_message.delete()
	if image_url:

		await update.effective_message.reply_photo(caption=str(temp_string), photo=image_url, reply_markup=reply_markup)
	else:

		await update.effective_message.reply_text(temp_string, reply_markup=reply_markup)

	return editing_iteration_start


async def show_master_editing_options(update: Update, context: CallbackContext):
	print('I am in master_edit_game')

	buttons = [InlineKeyboardButton(key[1], callback_data=key[0]) for key in keys_map.items() if key[0] != 'master_id']
	reply_markup = build_keyboard(buttons)
	await update.effective_message.reply_text('Что изменить?', reply_markup=reply_markup)
	return editing_iteration_input


async def handle_master_editing_option(update: Update, context: CallbackContext):
	print('I am in edit_game')
	query = update.callback_query.data
	await update.callback_query.edit_message_text('Введи новое значение:')
	context.user_data['value_to_edit'] = query
	return editing_iteration_finish


async def get_new_value_from_master(update: Update, context: CallbackContext):
	print('I am in master_new_data')
	# TODO check input for all options
	query = f"""
    		UPDATE games
    		SET {context.user_data['value_to_edit']} = ?
    		WHERE game_id = ?;
			"""
	result = db.execute_query(query, (update.effective_message.text, context.user_data['game_to_edit']))
	print(result)
	return await show_master_application(update, context, context.user_data['game_to_edit'])


async def exit_editing_loop(update: Update, context: CallbackContext):
	print('I am in exit_editing_loop')
	await update.effective_message.reply_text('Вы закончили редактирование!')
	return await start_master_conversation(update, context, False)


async def delete_game(update: Update, context: CallbackContext):
	print('I am in delete_game')
	query = f"""
			DELETE FROM games
			WHERE game_id = ?;
			"""
	result = db.execute_query(query, (context.user_data["game_to_edit"],))
	await update.callback_query.edit_message_text('Ваша заявка удалена :(')
	return await start_master_conversation(update, context)


async def get_game_name_from_master(update: Update, context: CallbackContext) -> int:
	print('im in get_game_name')

	context.user_data["game_name"] = update.effective_message.text
	await update.effective_message.reply_text(
		'👨‍👨‍👦‍👦 Ух, звучит серьёзно! Тут нужна целая группа приключенцев… Сколько, как вы считаете? (_Укажите, сколько свободных мест есть на вашу игру_)',
		parse_mode="Markdown"
	)
	return master_input_players_count


async def get_players_count_from_master(update: Update, context: CallbackContext) -> int:
	print(update.message.text)

	if not re.match(r'^\s*\d+(-\d+)?$', update.message.text):
		await update.effective_message.reply_text(
			'Только цифры, например 4-5 и тд.',
		)
		return master_input_players_count
	# Save the players_count
	context.user_data["players_count"] = update.effective_message.text

	await update.effective_message.reply_text(
		'🎲 Понимаю вашу спешку, но нужно следовать правилам. У нас тут система, знаете ли! (_Укажите, по какой системе игровых правил вы собираетесь вести игру_)',
		parse_mode="Markdown"
	)
	return master_input_system


async def get_system_from_master(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["system"] = update.effective_message.text
	await update.effective_message.reply_text(
		'🌐 Так-так, и куда же придётся отправиться нашим доблестным авантюристам? (_Парой слов опишите сеттинг и/или жанр вашей игры_)',
		parse_mode="Markdown"
	)
	return master_input_setting


async def get_setting_from_master(update: Update, context: CallbackContext) -> int:
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
		'⏳ Похоже, дело небыстрое… Надолго ли вам понадобятся услуги приключенцев гильдии? (_Укажите планируемую длительность игры: ван-шот, модуль или кампания_)',
		parse_mode="Markdown",
		reply_markup=reply_markup,
	)

	return master_input_game_type


async def get_game_type_from_master(update: Update, context: CallbackContext) -> int:
	# print(update.effective_message.text)
	query = update.callback_query
	await query.answer()
	context.user_data["game_type"] = query.data
	# Чекнуть возможность добавить выбор даты
	await update.effective_message.reply_text(
		'📆 Хорошо, записал… И когда вы готовы выдвигаться в путь? (_Укажите удобные даты и/или время для игры_)',
		parse_mode="Markdown",
	)
	return master_input_time


async def get_time_from_master(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["time"] = update.effective_message.text
	await update.effective_message.reply_text(
		'💰 Осталась пара формальностей. Вы хотите взять с приключенцев страховочный взнос? А то, знаете ли, бывали случаи… (_Укажите желаемую цену за игровую сессию с игрока_)',
		parse_mode="Markdown",
	)
	return master_input_cost


async def get_cost_from_master(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["cost"] = update.effective_message.text
	await update.effective_message.reply_text(
		'🌟 Ваше дело можно решить разными способами, знаете ли… Какие навыки и снаряжение нужны вашим авантюристам? (_Укажите желаемый опыт и/или стиль игры ваших игроков_)',
		parse_mode="Markdown",

	)
	return master_input_experience


async def get_experience_from_master(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["experience"] = update.effective_message.text
	await update.effective_message.reply_text(
		'🖼️ Последний штрих: пожалуйста, приложите вашу гербовую печать, портрет преступника и карту местности. Приключенцам нужны зацепки, знаете ли! (_Прикрепите к вашей заявке сопроводительное изображение это обязательный пункт_)',
		parse_mode="Markdown",
	)
	return master_input_image


async def get_image_from_master(update: Update, context: CallbackContext) -> int:
	image = update.effective_message.photo[-1]
	file = await context.bot.get_file(image.file_id)
	await file.download_to_drive(f'./images/{image.file_id}.jpg')
	context.user_data["image_url"] = f'./images/{image.file_id}.jpg'
	await update.effective_message.reply_text(
		'📜 Формуляр заполнен! Я подготовлю почтовых ястребов – а вы можете написать письмо для вашей будущей группы героев. (_Оставьте описание вашей игры, пожелания к игрокам и иное, что считаете нужным_)',
		parse_mode="Markdown",
	)
	return master_input_free_text


async def get_free_text_from_master(update: Update, context: CallbackContext) -> int:
	print(update.effective_message.text)

	context.user_data["free_text"] = update.effective_message.text

	# Prepare a summary of the collected data
	output_string = ''
	for key, value in context.user_data.items():
		if key != 'image_url':
			if key == 'master_id':
				output_string += keys_map[key] + ': ' + '@' + str(value) + '\n'
			else:
				output_string += keys_map[key] + ": " + value + '\n'

	# Send the summary back to the master
	await update.effective_message.reply_photo(
		caption=output_string, photo=context.user_data['image_url']
	)

	# Send message with summary to main resiever
	await context.bot.send_photo(evgeniya_tiamat_id, photo=context.user_data['image_url'],
								 caption="❗️Новый анонс получен❗️\n" + output_string)

	await context.bot.send_photo(dadjezz_id, photo=context.user_data['image_url'],
								 caption="❗️Новый анонс получен❗️\n" + output_string)

	await context.bot.send_photo(igor_krivic_id, photo=context.user_data['image_url'],
								 caption="❗️Новый анонс получен❗️\n" + output_string)
	# Insert the data into the database
	query = f"""
            INSERT INTO games (master_id, game_name, players_count, system, setting, game_type, time, cost, experience, image_url, free_text)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """
	try:
		db.execute_query(query, tuple(context.user_data.values()))
	except Exception as e:
		print(e)
	await update.effective_message.reply_text(
		'Спасибо! Ваш анонс принят. Нажми /start если хочешь начать сначала.',
	)

	return ConversationHandler.END


async def start_player_conversation(update: Update, context: CallbackContext):
	print("player")

	reply_keyboard = [
		[
			InlineKeyboardButton("Поиск", callback_data="search"),
			# InlineKeyboardButton("Заявка", callback_data="application"),
		],
		[
			InlineKeyboardButton("Назад", callback_data="start_again"),
		]
	]
	reply_markup = InlineKeyboardMarkup(reply_keyboard)

	new_message_text = "Что хочешь сделать?"
	await update.callback_query.edit_message_text(text=new_message_text, reply_markup=reply_markup)

	return player_selection


async def handle_player_selection(update: Update, context: CallbackContext):
	print("second_selection")
	if update.callback_query.data == 'application':
		return await start_player_application(update, context)
	elif update.callback_query.data == 'search':
		return await start_player_search(update, context)



async def start_player_application(update: Update, context: CallbackContext) -> int:
	query = update.callback_query
	query.answer()
	print("start_player_conversation() called")
	context.user_data.clear()
	await update.callback_query.edit_message_text(
		text="😀 Приветствуем в рядах гильдии – мы всегда рады новым героям! Представьтесь, пожалуйста. (_Напишите своё имя и/или никнейм_)",
		parse_mode="Markdown",
	)

	return player_name_input


async def get_player_name(update: Update, context: CallbackContext) -> int:
	print("get_player_name() called")

	print(update.effective_message.text)

	context.user_data["player_name"] = update.effective_message.text
	# await update.callback_query.edit_message_text(text="Как с тобой связаться?")
	await update.effective_message.reply_text(
		text="✍️ Когда мы найдём подходящее приключение для вас, куда отправлять почтового ястреба? (_Укажите никнейм в ТГ и/или предпочитаемый способ связи_)",
		parse_mode="Markdown",
	)
	return player_contact_input


async def get_contact_from_player(update: Update, context: CallbackContext) -> int:
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
		"⏳Походы в приключения бывают долгими, знаете ли! Как надолго вы готовы отлучиться? (_Укажите предпочтительную длительность игры: ван-шот, модуль или кампания_)",
		parse_mode="Markdown",
		reply_markup=reply_markup,
	)
	return player_game_type_input


async def get_game_type_from_player(update: Update, context: CallbackContext) -> int:
	print("get_game_type() called")

	print(update.effective_message.text)

	context.user_data["game_type"] = update.effective_message.text

	await update.callback_query.edit_message_text(
		text='🌐 Какого рода приключения предпочитаете? Подвигу везде есть место! (_В паре слов опишите, в каком сеттинге и/или жанре вы хотели бы сыграть_)',
		parse_mode="Markdown",
	)
	return players_system_input


async def get_system_from_player(update: Update, context: CallbackContext) -> int:
	print("get_system_type() called")

	print(update.effective_message.text)

	context.user_data["system"] = update.effective_message.text
	await update.effective_message.reply_text(
		'📆 Дожили: приключения по расписанию… В моё время авантюрист был всегда готов, знаете ли! (_Укажите удобные даты и/или время для игры_)',
		parse_mode="Markdown",
	)
	return player_time_input


async def get_time_from_player(update: Update, context: CallbackContext) -> int:
	print("get_time() called")

	print(update.effective_message.text)

	context.user_data["time"] = update.effective_message.text
	await update.effective_message.reply_text(
		'💰 Последняя формальность: гильдия принимает взносы от авантюристов – сколько вы готовы внести в нашу казну? (_Укажите желаемую цену за игровую сессию_)',
		parse_mode="Markdown",
	)
	return player_price_input


async def get_price_from_player(update: Update, context: CallbackContext) -> int:
	print("get_price() called")

	print(update.effective_message.text)

	context.user_data["price"] = update.effective_message.text
	await update.effective_message.reply_text(
		'📜 Формуляр заполнен! Пока чернила сохнут – расскажите немного о себе? Авантюристы бывают разные, знаете ли! (_Опишите свой игровой опыт, пожелания от игры, настольно-ролевые предпочтения и иное, что считаете нужным_)',
		parse_mode="Markdown",
	)
	return player_free_text_input


async def get_free_text_from_player(update: Update, context: CallbackContext) -> int:
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
							  callback_data='Покажи мне все игры')
		],
		[
			InlineKeyboardButton('Я хочу выбрать по фильтру',
								 callback_data='Я хочу выбрать по фильтру'),
		],
		# [
		# 	InlineKeyboardButton('Назад', callback_data='start_again')
		# ]
	]
	reply_markup = InlineKeyboardMarkup(question_keyboard)
	await update.effective_message.reply_text(
		'Выбери вариант:',
		reply_markup=reply_markup,
	)
	return player_search


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
		await update.effective_message.reply_text("На этом все. Нажми /start если хочешь начать сначала")
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
		return search_type_input


def get_game_announcement() -> list:
	# Query to get games of the selected type from the database
	query = """
            SELECT master_id, game_name, players_count, system, setting, game_type, time, cost, experience, free_text, image_url FROM games
            """
	# Execute a request with the selected game type parameter
	result = db.execute_query(query)
	list_player = []
	# Generating a list of games to display to the user
	for game in result:
		temp_string = ''
		for i, key in enumerate(keys_map):

			if key != 'image_url':
				if key == 'master_id':
					temp_string += keys_map[key] + ': ' + '@' + str(game[i]) + '\n'
				else:
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
	return search_system_input


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
	return search_price_input


async def get_search_price(update: Update, context: CallbackContext) -> int:
	# print("get_search_price: " + update.effective_message.text)
	player_choise_price = update.callback_query.data[len("cost-"):]
	query = """
            SELECT 
            		master_id,
            		game_name,
            		players_count,
            		system,
            		setting,
            		game_type,
            		time,
            		cost,
            		experience,
            		free_text,
            		image_url 
            FROM games 
            WHERE game_type=? AND system=? AND cost=?;
            """
	result = db.execute_query(
		query, (context.user_data["game_type"], context.user_data["game_system"], player_choise_price))

	for game in result:
		image_url = None
		temp_string = ''
		for i, key in enumerate(keys_map):
			if key != 'image_url':
				temp_string += keys_map[key] + ': ' + str(game[i]) + '\n'
			else:
				image_url = game[i]
		if image_url:
			await update.effective_message.reply_photo(caption=str(temp_string), photo=image_url)
		else:
			await update.effective_message.reply_text(temp_string)
	await update.effective_message.reply_text("На этом все. Нажми /start если хочешь начать сначала")
	return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
	print("END")
	await update.effective_message.reply_text('Пока!')
	return ConversationHandler.END
