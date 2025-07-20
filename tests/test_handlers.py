
import unittest
import os
from unittest.mock import patch, MagicMock, AsyncMock


# Patch DatabaseManager before importing modules that use it
with patch.dict(os.environ, {'DATABASE_URL': 'dbname=test'}):
    with patch('db_manager.DatabaseManager') as MockDatabaseManager:
        MockDatabaseManager.return_value = MagicMock()
        from commands.handlers import start, check_today, check_tomorrow, show_info, stop_notifications, restart_notifications

class TestHandlers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Patch the db instance that was already imported
        self.mock_db = patch('commands.handlers.db').start()
        self.addCleanup(patch.stopall)

    async def test_start(self):
        update = AsyncMock()
        context = AsyncMock()
        self.mock_db.get_user.return_value = None
        await start(update, context)
        update.message.reply_text.assert_called()

    async def test_check_today(self):
        update = AsyncMock()
        context = AsyncMock()
        await check_today(update, context)
        update.message.reply_text.assert_called_once()

    async def test_check_tomorrow(self):
        update = AsyncMock()
        context = AsyncMock()
        await check_tomorrow(update, context)
        update.message.reply_text.assert_called_once()

    async def test_show_info(self):
        update = AsyncMock()
        context = AsyncMock()
        await show_info(update, context)
        update.message.reply_text.assert_called_once()

    async def test_stop_notifications(self):
        update = AsyncMock()
        context = AsyncMock()
        update.effective_user.id = 1
        await stop_notifications(update, context)
        self.mock_db.set_notifications_enabled.assert_called_with(1, False)
        update.message.reply_text.assert_called_with('Notifiche disattivate. Usa /start per riattivarle.')

    async def test_restart_notifications(self):
        update = AsyncMock()
        context = AsyncMock()
        update.effective_user.id = 1
        await restart_notifications(update, context)
        self.mock_db.set_notifications_enabled.assert_called_with(1, True)
        update.message.reply_text.assert_called_with('Notifiche riattivate. Riceverai informazioni sulla raccolta differenziata.')

if __name__ == '__main__':
    unittest.main()
