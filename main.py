from telegram import BotCommand
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from conversation import start, state_0, state_1, master_select, game_edit, game_name, players_count, system, setting, \
	first_selection, get_master_select, get_game_name, get_players_count, get_system, get_setting, get_game_type, \
	game_type, time, cost, experience, upload_image, free_text, player_actions, player_application, player_name, \
	player_contact, player_game_type, system_type, player_time, price, player_free_text, player_selection, search_type, \
	search_system, search_price, get_time, get_cost, get_experience, get_image_from_master, get_free_text, \
	second_selection, start_player_application, get_player_name, get_player_contact, get_player_game_type, \
	get_system_type, get_player_time, get_price, get_player_free_text, get_player_selection, get_search_type, \
	get_search_system, get_search_price, cancel, show_master_select


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
		state_0: [CallbackQueryHandler(first_selection, pattern="^(master|player)$")],
		state_1: [CallbackQueryHandler(first_selection, pattern="^master&")],
		master_select: [
			CallbackQueryHandler(get_master_select, pattern="^(master_applications|new_master_application)$")],
		game_edit: [CallbackQueryHandler(show_master_select, pattern="^game")],
		# game_name: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_master_select)],

		players_count: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_players_count)],
		system: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system)],
		setting: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_setting)],
		game_type: [CallbackQueryHandler(get_game_type, pattern="^(Ваншот|Кампания|Модуль)$")],
		time: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
		cost: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cost)],
		experience: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_experience)],
		upload_image: [MessageHandler(filters.PHOTO, get_image_from_master)],
		free_text: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_free_text)],
		player_actions: [CallbackQueryHandler(second_selection, pattern="^(search|application)$")],
		player_application: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_player_application)],
		player_name: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_name)],
		player_contact: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_contact)],
		player_game_type: [CallbackQueryHandler(get_player_game_type, pattern="^(Ваншот|Кампания|Модуль)$")],
		system_type: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_system_type)],
		player_time: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_time)],
		price: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
		player_free_text: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_free_text)],
		player_selection: [
			CallbackQueryHandler(get_player_selection, pattern="^(Покажи мне все игры|Я хочу выбрать по фильтру)$")],
		search_type: [CallbackQueryHandler(get_search_type, pattern="^(Ваншот|Кампания|Модуль)$")],
		search_system: [CallbackQueryHandler(get_search_system, pattern="^system-.*")],
		search_price: [CallbackQueryHandler(get_search_price, pattern="^cost-.*")],
	},
	fallbacks=[CommandHandler('cancel', cancel)]
)
application.add_handler(conv_handler)
application.run_polling()
