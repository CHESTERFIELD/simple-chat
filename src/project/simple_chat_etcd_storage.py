"""The class implementation that work with key-value storage"""
import json
from dataclasses import dataclass, field
from datetime import datetime

import etcd3
from google.protobuf.timestamp_pb2 import Timestamp
from typing import List, Tuple

import simple_chat_pb2


def get_etcd_storage_connection(host='localhost', port=2379) -> 'Storage':
    """Creates new one etcd connection for working with storage"""
    etcd_storage = Storage(host, port)
    return etcd_storage


class Storage:
    """Provides methods that implement functionality of key-value storage"""
    USER_KEY = 'user/{user_id}'
    USER_MESSAGE_QUEUE_KEY = 'message/queue/user/{user_id}/{message_id}'
    USER_PREFIX_KEY = 'user/'
    USER_MESSAGE_QUEUE_PREFIX_KEY = 'message/queue/user/{user_id}'

    def __init__(self, host, port):
        self._client = etcd3.client(host, port)

    def get_users(self) -> List[simple_chat_pb2.User]:
        """Getting sequence of users"""
        users = [
            User.from_json_str(user_value.decode('utf-8')).to_pb()
            for user_value, _ in self._client.get_prefix(self.USER_PREFIX_KEY)
        ]

        return users

    def put_user(self, user: dict):
        """Adding user to storage"""
        self._client.put(self.USER_KEY.format(user_id=user['login']),
                         json.dumps(user))

    def put_message(self, message: dict):
        """Adding new queue message to storage"""
        unique_key = self.create_unique_queue_message_key(
            message['sender'], message['created'], message['recipient'])

        self._client.put(
            self.USER_MESSAGE_QUEUE_KEY.format(
                user_id=message['recipient'],
                message_id=unique_key),
            json.dumps(message))

    @staticmethod
    def create_unique_queue_message_key(sender, created, recipient) -> str:
        """Creating unique key value for message"""
        return "{}{}{}".format(sender, created, recipient)

    def get_user_queue_messages(self, user_login: str) -> \
            List[Tuple[simple_chat_pb2.Message, str]]:
        """Getting sequence of queued messages for received user login"""
        prefix = self.USER_MESSAGE_QUEUE_PREFIX_KEY.format(user_id=user_login)
        messages_iterator = self._client.get_prefix(prefix)

        messages = []
        for value, metadata in messages_iterator:
            message = Message.from_json_str(value.decode('utf-8'))
            message_key = metadata.key.decode('utf-8')

            messages.append((message.to_pb(), message_key))

        return messages

    def delete_user_queue_message(self, message_key: str):
        """Deleting queued message from the storage"""
        self._client.delete(message_key)


@dataclass
class User:
    """Model for user"""

    login: str
    full_name: str

    def to_pb(self) -> simple_chat_pb2.User:
        """Converts object to protocol buffer"""
        return simple_chat_pb2.User(
            login=self.login, full_name=self.full_name)

    @staticmethod
    def from_json_str(json_str: str) -> 'User':
        """Converts json string to object"""
        return User(**json.loads(json_str))


@dataclass
class Message:
    """Model for message"""

    sender: str
    recipient: str
    body: str
    created: datetime = field(default_factory=datetime)

    def to_pb(self) -> simple_chat_pb2.Message:
        """Converts object to protocol buffer"""
        timestamp = Timestamp()
        timestamp.FromDatetime(self.created)
        return simple_chat_pb2.Message(
            sender=self.sender,
            recipient=self.recipient,
            body=self.body,
            created=timestamp)

    @staticmethod
    def from_json_str(json_str: str) -> 'Message':
        """Converts json string to object"""
        message_data = json.loads(json_str)

        message_data['created'] = \
            datetime.fromtimestamp(message_data['created'])

        return Message(**message_data)
