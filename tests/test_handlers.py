# # tests/test_handlers.py
# import pytest
# from unittest.mock import MagicMock, AsyncMock
#
#
# # from conversation import start, state_0
# from telegram import InlineKeyboardButton
#
# from conversation import start, state_0
#
#
# @pytest.mark.asyncio
# async def test_start_handler():
#
#     update = MagicMock()
#     update.message = MagicMock()
#     update.message.reply_text = AsyncMock()
#
#
#     context = MagicMock()
#
#
#     result_state = await start(update, context)
#
#
#     update.message.reply_text.assert_awaited_once()
#
#
#     args, kwargs = update.message.reply_text.call_args
#     assert args[0] == 'Выбери кто ты?'
#
#     markup = kwargs["reply_markup"]
#
#     first_row = markup.inline_keyboard[0]
#     assert isinstance(first_row[0], InlineKeyboardButton)
#     assert first_row[0].text == "Мастер"
#     assert first_row[0].callback_data == "master"
#
#
#     assert result_state == state_0