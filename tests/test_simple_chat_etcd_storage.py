"""Tests of simple_chat_etcdstorage module"""
import json
import logging
import time
import unittest
from dataclasses import asdict
from unittest.mock import patch, Mock

import simple_chat_etcd_storage as storage
from simple_chat_etcd_storage import User, Message, Storage


class UserTestCase(unittest.TestCase):

    def test_from_dict(self):
        """Tests of from_dict method"""
        user_login = '111'
        user_full_name = 'User'

        user_dict = {
            'login': user_login,
            'full_name': user_full_name
        }
        user = User.from_dict(user_dict)
        user2 = User(user_login, user_full_name)

        self.assertEqual(user, user2)


class MessageTestCase(unittest.TestCase):

    def test_from_dict(self):
        """Tests of from_dict method"""
        sender = '111'
        recipient = '123'
        body = 'Hello!'
        created = time.time()
        
        message_dict = {
            'sender': sender,
            'recipient': recipient,
            'body': body,
            'created': created
        }
        message = Message.from_dict(message_dict)
        message2 = Message(sender, recipient, body, created)

        self.assertEqual(message, message2)

    def test_get_unique_queue_message_key(self):
        """ Tests of get_unique_queue_message_key method"""
        message = Message('1', '2', 'Hello!')
        
        message_key = \
            "{}{}{}".format(message.sender, message.created, message.recipient)
        self.assertEqual(message.get_unique_queue_message_key(), message_key)


class StorageTestCase(unittest.TestCase):

    @patch('etcd3.client')
    def setUp(self, mock_etcd_client):
        self.storage = Storage(Mock(), Mock())

    def test_get_users(self):
        """Tests of get_users method"""
        users_tuple = (('{"login": "1", "full_name": "User"}', Mock()),)
        
        mock_etcd_client_get_prefix = Mock(return_value=users_tuple)
        self.storage._client.get_prefix = mock_etcd_client_get_prefix

        users = self.storage.get_users()

        mock_etcd_client_get_prefix.assert_called_once_with(
            storage.STORAGE_USER_PREFIX_KEY)

        self.assertEqual(users[0], User('1', 'User'))

    def test_put_user(self):
        """Tests of put_user method"""
        mock_etcd_client_put = Mock()
        self.storage._client.put = mock_etcd_client_put

        user = User('1', 'User')
        self.storage.put_user(user)

        prefix = storage.STORAGE_USER_KEY.format(user_id=user.login)
        mock_etcd_client_put.assert_called_once_with(
            prefix, json.dumps(asdict(user)))

    def test_put_message(self):
        """Tests of put_message method"""
        mock_etcd_client_put = Mock()
        self.storage._client.put = mock_etcd_client_put

        message = Message('1', '2', 'Hello!')
        self.storage.put_message(message)

        prefix = storage.STORAGE_USER_MESSAGE_QUEUE_KEY.format(
            user_id=message.recipient,
            message_id=message.get_unique_queue_message_key())

        mock_etcd_client_put.assert_called_once_with(
            prefix, json.dumps(asdict(message)))

    def test_get_user_queue_messages(self):
        """Tests of get_user_queue_messages method"""
        message_dict = {
            'sender': '111',
            'recipient': '123',
            'body': 'Hello!',
            'created': time.time()
        }

        users_tuple = ((json.dumps(message_dict), Mock()), )

        mock_etcd_client_get_prefix = Mock(return_value=users_tuple)
        self.storage._client.get_prefix = mock_etcd_client_get_prefix

        messages = self.storage.get_user_queue_messages(
            message_dict['recipient'])

        mock_etcd_client_get_prefix.assert_called_once_with(
            storage.STORAGE_USER_MESSAGE_QUEUE_PREFIX_KEY.format(
                user_id=message_dict['recipient']))

        self.assertEqual(Message.from_dict(message_dict), messages[0])

    def test_delete_user_queue_message(self):
        """Tests of delete_user_queue_message method"""
        mock_etcd_client_delete = Mock()
        self.storage._client.delete = mock_etcd_client_delete

        message = Message('1', '2', 'Hello!')
        self.storage.delete_user_queue_message(message)

        delete_message_key = storage.STORAGE_USER_MESSAGE_QUEUE_KEY.format(
            user_id=message.recipient,
            message_id=message.get_unique_queue_message_key())

        mock_etcd_client_delete.assert_called_once_with(delete_message_key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
