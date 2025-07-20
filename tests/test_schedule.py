
import unittest
import os
from unittest.mock import patch, MagicMock, AsyncMock


# Patch DatabaseManager before importing modules that use it
with patch.dict(os.environ, {'DATABASE_URL': 'dbname=test'}):
    with patch('db_manager.DatabaseManager') as MockDatabaseManager:
        MockDatabaseManager.return_value = MagicMock()
        from service.schedule import get_waste_collection, send_notification, schedule_tomorrow_notification

class TestSchedule(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Patch the db instance that was already imported
        self.mock_db = patch('service.schedule.db').start()
        self.addCleanup(patch.stopall)

    def test_get_waste_collection(self):
        # March 1st has PLASTICA scheduled
        waste_types = get_waste_collection(1, 3)
        print(f"Waste types for March 1st: {waste_types}") # Debugging print
        self.assertIn('PLASTICA', waste_types)

    async def test_send_notification(self):
        self.mock_db.get_user.return_value = {'user_id': 1, 'notifications_enabled': True, 'address': 'test_address'}
        context = AsyncMock()
        context.job.data = 1
        await send_notification(context)
        context.bot.send_message.assert_called_once()

    async def test_schedule_tomorrow_notification(self):
        self.mock_db.get_all_users_for_notification.return_value = [
            {'user_id': 1, 'notification_time': '20:00'}
        ]
        context = MagicMock()
        context.job_queue.get_jobs_by_name.return_value = [] # Mock this to return an empty list
        context.job_queue.run_once = MagicMock()
        await schedule_tomorrow_notification(context)
        context.job_queue.run_once.assert_called_once()

if __name__ == '__main__':
    unittest.main()
