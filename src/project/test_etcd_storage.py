"""Tests of simple_chat_etcd_storage module"""
import json
import logging
import time
import unittest
from dataclasses import asdict
from unittest.mock import patch, Mock

import simple_chat_etcd_storage as storage
from simple_chat_etcd_storage import User, Message, Storage


class TestEtcdStorage(unittest.TestCase):

    @patch('etcd3.client')
    def setUp(self, mock_etcd_client):
        self._storage = Storage(Mock(), Mock())

    @staticmethod
    def get_user_from_dict():
        """Returns simple_chat_etcd_storage.User schema model object"""
        user_dict = {
            'login': '111',
            'full_name': 'User'
        }
        return User.from_dict(user_dict)

    def test_User_from_dict(self):
        """Tests of simple_chat_etcd_storage.User.from_dict method"""
        user = self.get_user_from_dict()
        self.assertTrue(isinstance(user, User))

    @staticmethod
    def get_message_from_dict():
        """Returns simple_chat_etcd_storage.Message schema model object"""
        message_dict = {
            'sender': '111',
            'recipient': '123',
            'body': 'Hello!',
            'created': time.time()
        }
        return Message.from_dict(message_dict)

    def test_Message_from_dict(self):
        """Tests of simple_chat_etcd_storage.Message.from_dict method"""
        message = self.get_message_from_dict()
        self.assertTrue(isinstance(message, Message))

    def test_Message_get_unique_queue_message_key(self):
        """
        Tests of simple_chat_etcd_storage.Message.get_unique_queue_message_key
        method
        """
        message = self.get_message_from_dict()
        message_key = \
            "{}{}{}".format(message.sender, message.created, message.recipient)
        self.assertEqual(message.get_unique_queue_message_key(), message_key)

    def test_storage_get_users(self):
        """Tests of simple_chat_etcd_storage.Storage.get_users method"""
        mock_etcd_client_get_prefix = Mock(return_value=(
            ('{"login": "1313", "full_name": "Tom Tom"}', Mock()), ))
        self._storage._client.get_prefix = mock_etcd_client_get_prefix

        users = self._storage.get_users()

        mock_etcd_client_get_prefix.assert_called_once_with(
            storage.STORAGE_USER_PREFIX_KEY)

        self.assertTrue(isinstance(users, list))
        self.assertTrue(isinstance(users[0], User))
        self.assertGreater(len(users), 0)

    def test_storage_put_user(self):
        """Tests of simple_chat_etcd_storage.Storage.put_user method"""
        mock_etcd_client_put = Mock()
        self._storage._client.put = mock_etcd_client_put

        user = self.get_user_from_dict()
        self._storage.put_user(user)

        prefix = storage.STORAGE_USER_KEY.format(user_id=user.login)
        mock_etcd_client_put.assert_called_once_with(
            prefix, json.dumps(asdict(user)))

    def test_storage_put_message(self):
        """Tests of simple_chat_etcd_storage.Storage.put_message method"""
        mock_etcd_client_put = Mock()
        self._storage._client.put = mock_etcd_client_put

        message = self.get_message_from_dict()
        self._storage.put_message(message)

        prefix = storage.STORAGE_USER_MESSAGE_QUEUE_KEY.format(
            user_id=message.recipient,
            message_id=message.get_unique_queue_message_key())
        mock_etcd_client_put.assert_called_once_with(
            prefix, json.dumps(asdict(message)))

    def test_storage_get_user_queue_messages(self):
        """Tests of simple_chat_etcd_storage.Storage.get_user_queue_messages
         method
         """
        message_dict = {
            'sender': '111',
            'recipient': '123',
            'body': 'Hello!',
            'created': time.time()
        }
        users_tuple = ((json.dumps(message_dict), Mock()), )

        mock_etcd_client_get_prefix = Mock(return_value=users_tuple)
        self._storage._client.get_prefix = mock_etcd_client_get_prefix

        messages = self._storage.get_user_queue_messages(
            message_dict['recipient'])

        mock_etcd_client_get_prefix.assert_called_once_with(
            storage.STORAGE_USER_MESSAGE_QUEUE_PREFIX_KEY.format(
                user_id=message_dict['recipient']))

        self.assertTrue(isinstance(messages, list))
        self.assertTrue(isinstance(messages[0], Message))
        self.assertGreater(len(messages), 0)

    def test_storage_delete_user_queue_message(self):
        """Tests of simple_chat_etcd_storage.Storage.delete_user_queue_message
        method
        """
        mock_etcd_client_delete = Mock()
        self._storage._client.delete = mock_etcd_client_delete

        message = self.get_message_from_dict()
        self._storage.delete_user_queue_message(message)

        delete_message_key = storage.STORAGE_USER_MESSAGE_QUEUE_KEY.format(
            user_id=message.recipient,
            message_id=message.get_unique_queue_message_key())

        mock_etcd_client_delete.assert_called_once_with(delete_message_key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
