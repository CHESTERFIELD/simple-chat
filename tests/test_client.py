"""Tests of simple_chat_client module"""
import logging
import time
import unittest
from unittest.mock import Mock, patch

from google.protobuf.timestamp_pb2 import Timestamp

import simple_chat_client
import simple_chat_pb2


class TestClient(unittest.TestCase):

    @staticmethod
    def get_mock_parser(method_type: str) -> Mock:
        """Mocks arguments parser object"""
        mock_parser = Mock()
        mock_parser.method = method_type
        mock_parser.sender = '123'
        mock_parser.recipient = '111'
        mock_parser.body = 'Hello'

        return mock_parser

    @patch('simple_chat_client.get_users')
    def test_submit_request_get_users(self, get_users):
        """Tests of simple_chat_client.submit_request 'users branch' method"""
        mock_parser = self.get_mock_parser('users')
        mock_stub = Mock()

        simple_chat_client.submit_request(mock_stub, mock_parser)
        get_users.assert_called_once_with(mock_stub)

    @patch('simple_chat_client.send_message')
    def test_submit_request_send_message(self, send_message):
        """Tests of simple_chat_client.submit_request 'send branch' method"""
        mock_parser = self.get_mock_parser('send')
        mock_stub = Mock()

        simple_chat_client.submit_request(mock_stub, mock_parser)
        send_message.assert_called_once_with(mock_stub, mock_parser.sender,
                                             mock_parser.recipient,
                                             mock_parser.body)

    @patch('simple_chat_client.receive_messages')
    def test_submit_request_receive_messages(self, receive_messages):
        """Tests of simple_chat_client.submit_request
        'receive branch' method
        """
        mock_parser = self.get_mock_parser('receive')
        mock_stub = Mock()

        simple_chat_client.submit_request(mock_stub, mock_parser)
        receive_messages.assert_called_once_with(mock_stub,
                                                 mock_parser.recipient)

    def test_validate_send_message_data(self):
        """Tests of simple_chat_client.validate_send_message_data method"""
        simple_chat_client.validate_send_message_data("1234", "1111", "Hello!")

    def test_validate_send_message_data_error(self):
        """Tests of simple_chat_client.validate_send_message_data
        method values errors
        """
        with self.assertRaises(ValueError):
            simple_chat_client.validate_send_message_data("", "1111", "Hello!")

        with self.assertRaises(ValueError):
            simple_chat_client.validate_send_message_data("1234", "", "Hello!")

        with self.assertRaises(ValueError):
            simple_chat_client.validate_send_message_data("1234", "1111", "")

    def test_validate_receive_messages_data(self):
        """Tests of simple_chat_client.validate_receive_messages_data method"""
        simple_chat_client.validate_receive_messages_data("1234")

    def test_validate_receive_messages_data_error(self):
        """Tests of simple_chat_client.validate_receive_messages_data
        method value error
        """
        with self.assertRaises(ValueError):
            simple_chat_client.validate_receive_messages_data("")

    @patch('builtins.print')
    @patch('simple_chat_pb2_grpc.SimpleChatStub')
    def test_get_users(self, mock_stub, mock_print):
        """Tests of simple_chat_client.get_users method"""
        login = '111'
        full_name = "Mock User"

        mock_stub.GetUsers.return_value = Mock(
            users=[simple_chat_pb2.User(login=login, full_name=full_name), ])

        simple_chat_client.get_users(mock_stub)
        mock_stub.GetUsers.assert_called_once()

        mock_print.assert_called_once_with(
            "User login: {}. User full name: {}".format(login, full_name))

    @patch('builtins.print')
    @patch('simple_chat_pb2_grpc.SimpleChatStub')
    def test_send_message(self, mock_stub, mock_print):
        """Tests of simple_chat_client.send_message method"""
        sender = '1'
        recipient = '2'
        body = 'Hello!'

        mock_stub.SendMessage = Mock()

        mock_message = simple_chat_pb2.Message(
            sender=sender,
            recipient=recipient,
            body=body)

        simple_chat_client.send_message(mock_stub, sender, recipient, body)
        mock_stub.SendMessage.assert_called_once_with(
            simple_chat_pb2.SendMessageRequest(message=mock_message))

        mock_print.assert_called_once_with("Message was sent")

    @patch('builtins.print')
    @patch('simple_chat_pb2_grpc.SimpleChatStub')
    def test_receive_messages(self, mock_stub, mock_print):
        """Tests of simple_chat_client.receive_messages method"""
        sender = '111'
        recipient = '123'
        body = 'Hello!'
        timestamp = Timestamp()
        timestamp.FromSeconds(int(time.time()))

        mock_stub.ReceiveMessages.return_value = [simple_chat_pb2.Message(
            sender=sender,
            recipient=recipient,
            body=body,
            created=timestamp)]

        simple_chat_client.receive_messages(mock_stub, recipient)
        mock_stub.ReceiveMessages.assert_called_once()

        mock_print.assert_called_once_with(
            "From: {}. \nTo: {}. \nTime: {}. \nMessage: '{}'.\n".format(
                sender, recipient, Timestamp.ToDatetime(timestamp), body))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
