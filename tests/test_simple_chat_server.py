"""Tests of simple_chat_server module"""
import logging
import time
import unittest
from unittest.mock import Mock

import simple_chat_pb2
import simple_chat_server
from simple_chat_etcd_storage import User, Message


class SimpleChatServicerTestCase(unittest.TestCase):

    def setUp(self):
        self.storage = Mock()
        self.servicer = simple_chat_server.SimpleChatServicer(self.storage)

    def test_GetUsers(self):
        """Tests of GetUsers method"""
        user = User('123', 'Mock user')

        mock_storage_get_users = Mock(return_value=[user])
        self.storage.get_users = mock_storage_get_users

        response = self.servicer.GetUsers(Mock(), Mock())

        mock_storage_get_users.assert_called_once()
        response_user = User(response.users[0].login,
                             response.users[0].full_name)
        self.assertEqual(response_user, user)

    def test_SendMessage(self):
        """Tests of SendMessage method"""
        mock_storage_put_message = Mock()
        self.storage.put_message = mock_storage_put_message

        mock_message = Mock(sender='1', recipient='2', body='Hello!')

        response = self.servicer.SendMessage(Mock(
            message=mock_message), Mock())

        mock_storage_put_message.assert_called_once()
        self.assertIsInstance(response, simple_chat_pb2.SendMessageResponse)

    def test_ReceiveMessages(self):
        """Tests of ReceiveMessages method"""
        message_recipient = '2'
        mock_message = Message('1', message_recipient,
                               'Hello!', int(time.time()))

        mock_storage_get_user_queue_messages = Mock(
            return_value=[mock_message])

        self.storage.get_user_queue_messages = \
            mock_storage_get_user_queue_messages

        mock_storage_delete_user_queue_message = Mock()
        self.storage.delete_user_queue_message = \
            mock_storage_delete_user_queue_message

        mock_request_login = Mock(login=message_recipient)
        response = self.servicer.ReceiveMessages(mock_request_login, Mock())

        message = next(response)
        next(response)

        response_message = Message(message.sender, message.recipient,
                                   message.body, message.created.seconds)

        mock_storage_get_user_queue_messages.assert_called_with(
            message_recipient)

        self.assertEqual(response_message, mock_message)

        mock_storage_delete_user_queue_message.assert_called_with(
            mock_message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
