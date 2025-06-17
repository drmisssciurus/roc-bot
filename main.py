from telegram import BotCommand
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from conversation import (
	start,
	handle_role_selection,
	get_master_select,
	get_game_name_from_master,
	get_players_count_from_master,
	get_system_from_master,
	get_setting_from_master,
	get_game_type_from_master,
	get_time_from_master,
	get_cost_from_master,
	get_experience_from_master,
	get_image_from_master,
	get_free_text_from_master,
	handle_player_selection,
	get_player_name,
	get_contact_from_player,
	get_game_type_from_player,
	get_system_from_player,
	get_time_from_player,
	get_price_from_player,
	get_free_text_from_player,
	get_player_selection,
	get_search_type,
	get_search_system,
	get_search_price,
	cancel,
	show_master_application,
	show_master_editing_options,
	handle_master_editing_option,
	get_new_value_from_master,
	exit_editing_loop,
	delete_game
)

from states import *


#ddd
async def set_bot_commands(application: Application) -> None:
	"""Устанавливаем постоянные команды."""
	commands = [
		BotCommand("start", "Запустить бота"),
		BotCommand("help", "Помощь"),
		BotCommand("cancel", "Отмена текущего действия"),
	]
	await application.bot.set_my_commands(commands)


application = Application.builder().token(BOT_TOKEN).build()

# Installation persistent buttons

application.bot_data["on_startup"] = lambda: application.loop.create_task(set_bot_commands(application))

# Main conversation
conv_handler = ConversationHandler(
	entry_points=[CommandHandler('start', start)],
	states={
		initial_state: [CallbackQueryHandler(handle_role_selection, pattern="^(master|player)$")],
		master_selection: [
			CallbackQueryHandler(get_master_select, pattern="^(master_applications|new_master_application)$")],

		# Game Editing Flow
		game_editing: [CallbackQueryHandler(show_master_application, pattern="^game")],
		editing_iteration_start: [CallbackQueryHandler(show_master_editing_options, pattern="^edit_game$"), CallbackQueryHandler(exit_editing_loop, pattern="^cancel_edit_game$"), CallbackQueryHandler(delete_game, pattern="^delete_game$")],
		editing_iteration_input: [CallbackQueryHandler(handle_master_editing_option, pattern="^(master_id|game_name|players_count|system|setting|game_type|time|cost|experience|image_url|free_text|)$")],
		editing_iteration_finish: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_value_from_master)],

		# New Application Flow
		master_input_game_name: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_game_name_from_master)],
		master_input_players_count: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_players_count_from_master)],
		master_input_system: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system_from_master)],
		master_input_setting: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_setting_from_master)],
		master_input_game_type: [CallbackQueryHandler(get_game_type_from_master, pattern="^(Ваншот|Кампания|Модуль)$")],
		master_input_time: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time_from_master)],
		master_input_cost: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cost_from_master)],
		master_input_experience: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience_from_master)],
		master_input_image: [MessageHandler(filters.PHOTO, get_image_from_master)],
		master_input_free_text: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_free_text_from_master)],

		# Player
		player_selection: [CallbackQueryHandler(handle_player_selection, pattern="^(search|application)$")],

		player_name_input: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_name)],
		player_contact_input: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact_from_player)],
		player_game_type_input: [CallbackQueryHandler(get_game_type_from_player, pattern="^(Ваншот|Кампания|Модуль)$")],
		players_system_input: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system_from_player)],
		player_time_input: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time_from_player)],
		player_price_input: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price_from_player)],
		player_free_text_input: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_free_text_from_player)],

		player_search: [
			CallbackQueryHandler(get_player_selection, pattern="^(Покажи мне все игры|Я хочу выбрать по фильтру)$")],
		search_type_input: [CallbackQueryHandler(get_search_type, pattern="^(Ваншот|Кампания|Модуль)$")],
		search_system_input: [CallbackQueryHandler(get_search_system, pattern="^system-.*")],
		search_price_input: [CallbackQueryHandler(get_search_price, pattern="^cost-.*")],
	},
	fallbacks=[CommandHandler('cancel', cancel)]
)
application.add_handler(conv_handler)
application.run_polling()
