
import unittest
import os
from unittest.mock import patch, MagicMock

# Set a dummy DATABASE_URL before importing the db_manager
os.environ['DATABASE_URL'] = 'dbname=test'

from db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):

    @patch('db_manager.psycopg2.pool.SimpleConnectionPool')
    def setUp(self, mock_pool):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        mock_pool.return_value.getconn.return_value = self.mock_conn
        self.db = DatabaseManager()

    def test_get_user(self):
        self.mock_cursor.fetchone.return_value = (1, 'test', 'Test', 'User', 'address', '20:00', True)
        self.mock_cursor.description = [('user_id',), ('username',), ('first_name',), ('last_name',), ('address',), ('notification_time',), ('notifications_enabled',)]
        user = self.db.get_user(1)
        self.assertIsNotNone(user)
        self.assertEqual(user['user_id'], 1)

    def test_create_user(self):
        self.mock_cursor.fetchone.return_value = (1,)
        result = self.db.create_user(1, 'test', 'Test', 'User')
        self.assertTrue(result)

    def test_update_user(self):
        self.mock_cursor.rowcount = 1
        result = self.db.update_user(1, address='new_address')
        self.assertTrue(result)

    def test_get_all_users_for_notification(self):
        self.mock_cursor.fetchall.return_value = [
            (1, 'test', 'Test', 'User', 'address', '20:00', True),
            (2, 'test2', 'Test2', 'User2', 'address2', '21:00', True)
        ]
        self.mock_cursor.description = [('user_id',), ('username',), ('first_name',), ('last_name',), ('address',), ('notification_time',), ('notifications_enabled',)]
        users = self.db.get_all_users_for_notification()
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]['user_id'], 1)
        self.assertEqual(users[1]['user_id'], 2)

if __name__ == '__main__':
    unittest.main()
