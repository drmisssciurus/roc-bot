import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.ext import CallbackContext

from conversation import start
from states import *

class TestStartHandler(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the start command handler."""

    # We patch the logger inside the 'conversation' module,
    # as that's where the 'start' function is defined and uses it.
    @patch('conversation.logger')
    async def test_start_sends_welcome_message_and_returns_initial_state(self, mock_logger: MagicMock):
        """
        Test that the start handler sends the welcome message with a keyboard
        and returns the correct initial state.
        """
        # Arrange
        # Mock the User object
        mock_user = MagicMock(spec=User)
        mock_user.id = 123456
        mock_user.username = 'testuser'

        # Mock the Update object that the handler receives.
        mock_update = MagicMock(spec=Update)
        mock_update.effective_message = AsyncMock()
        mock_update.effective_message.from_user = mock_user

        # Mock the Context object (not used in this handler, but required by the signature).
        mock_context = MagicMock(spec=CallbackContext)

        # Act
        # Call the handler function we are testing.
        result = await start(mock_update, mock_context)

        # Assert
        # 1. Check if the logger was called correctly.
        mock_logger.info.assert_called_once_with('start function called')

        # 2. Check if the correct message was sent back to the user.
        expected_text = '🧙 Добро пожаловать в Гильдию Авантюристов! Вы сегодня к нам в каком статусе?'
        expected_keyboard = [[InlineKeyboardButton("Мастер", callback_data="master"), InlineKeyboardButton("Игрок", callback_data="player")]]
        expected_markup = InlineKeyboardMarkup(expected_keyboard)

        mock_update.effective_message.reply_text.assert_awaited_once_with(expected_text, reply_markup=expected_markup)

        # 3. Check if the function returned the correct next state.
        self.assertEqual(result, initial_state)