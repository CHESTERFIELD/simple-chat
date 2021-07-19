"""Tests of simple_chat_server module"""
import logging
import unittest
from unittest.mock import Mock, patch

import simple_chat_pb2
import simple_chat_server
from simple_chat_etcd_storage import User, Message


class TestServer(unittest.TestCase):

    @patch("simple_chat_etcd_storage.Storage")
    def setUp(self, mock_storage):
        self._servicer = simple_chat_server.SimpleChatServicer(mock_storage)

    def test_GetUsers(self):
        """Tests of simple_chat_server.SimpleChatServicer.GetUsers
        method
        """
        mock_storage_get_users = \
            Mock(return_value=[User('123', 'Mock user')])
        self._servicer._storage.get_users = mock_storage_get_users

        response = self._servicer.GetUsers(Mock(), Mock())

        mock_storage_get_users.assert_called_once()
        self.assertTrue(isinstance(response,
                                   simple_chat_pb2.GetUsersResponse))
        self.assertTrue(hasattr(response, 'users'))
        self.assertGreater(len(response.users), 0)

    def test_SendMessage(self):
        """Tests of simple_chat_server.SimpleChatServicer.SendMessage
        method
        """
        mock_storage_put_message = Mock()
        self._servicer._storage.put_message = mock_storage_put_message

        mock_message = Message(sender='1', recipient='2', body='Hello!')

        response = self._servicer.SendMessage(Mock(
            message=mock_message), Mock())

        mock_storage_put_message.assert_called_once()
        self.assertTrue(isinstance(response,
                                   simple_chat_pb2.SendMessageResponse))

    def test_ReceiveMessages(self):
        """Tests of simple_chat_server.SimpleChatServicer.ReceiveMessages
        method
        """
        message_recipient = '2'
        message = Message('1', message_recipient, 'Hello!')

        mock_storage_get_user_queue_messages = Mock(return_value=[message])
        self._servicer._storage.get_user_queue_messages = \
            mock_storage_get_user_queue_messages

        mock_storage_delete_user_queue_message = Mock()
        self._servicer._storage.delete_user_queue_message = \
            mock_storage_delete_user_queue_message

        mock_request_login = Mock(login=message_recipient)
        response = self._servicer.ReceiveMessages(mock_request_login, Mock())

        for key, value in enumerate(response):
            if key:
                break

            mock_storage_get_user_queue_messages.assert_called_with(
                message_recipient)
            self.assertTrue(isinstance(value, simple_chat_pb2.Message))

        mock_storage_delete_user_queue_message.assert_called_with(
            message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
