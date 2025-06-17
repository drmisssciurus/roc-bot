import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import InlineKeyboardButton
from conversation import start, state_0


@pytest.mark.asyncio
async def test_start_successful_reply():
	update = MagicMock()
	update.message = MagicMock()
	update.message.reply_text = AsyncMock()

	context = MagicMock()

	result_state = await start(update, context)

	update.message.reply_text.assert_awaited_once()

	args, kwargs = update.message.reply_text.call_args
	assert args[0] == 'Выбери кто ты?'


	assert result_state == state_0


@pytest.mark.asyncio
async def test_start_correct_keyboard():
	update = MagicMock()
	update.message = MagicMock()
	update.message.reply_text = AsyncMock()

	context = MagicMock()

	result_state = await start(update, context)
	args, kwargs = update.message.reply_text.call_args

	markup = kwargs["reply_markup"]

	first_row = markup.inline_keyboard[0]
	assert isinstance(first_row[0], InlineKeyboardButton)
	assert first_row[0].text == "Мастер"
	assert first_row[0].callback_data == "master"

	assert first_row[1].text == "Игрок"
	assert first_row[1].callback_data == "player"


@pytest.mark.asyncio
async def test_start_no_message():
	update = MagicMock(message=None)
	context = MagicMock()

	with pytest.raises(AttributeError):
		await start(update, context)