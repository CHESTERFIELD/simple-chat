"""The class implementation that work with key-value storage"""
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List

import etcd3


STORAGE_USER_KEY = 'user/{user_id}'
STORAGE_USER_MESSAGE_QUEUE_KEY = 'message/queue/user/{user_id}/{message_id}'
STORAGE_USER_PREFIX_KEY = 'user/'
STORAGE_USER_MESSAGE_QUEUE_PREFIX_KEY = 'message/queue/user/{user_id}'


@dataclass
class User:
    """Model for user"""

    login: str
    full_name: str

    @staticmethod
    def from_dict(data: dict) -> 'User':
        """Converts dict to object"""
        return User(data['login'], data['full_name'])


@dataclass
class Message:
    """Model for message"""

    sender: str
    recipient: str
    body: str
    created: float = field(default_factory=lambda: time.time())

    def get_unique_queue_message_key(self) -> str:
        """Creating unique key value for message"""
        return "{}{}{}".format(self.sender, self.created, self.recipient)

    @staticmethod
    def from_dict(data: dict) -> 'Message':
        """Converts dict to object"""
        return Message(data['sender'], data['recipient'], data['body'],
                       float(data['created']))


class Storage:
    """Provides methods that implement functionality of key-value storage"""

    def __init__(self, host, port):
        self._client = etcd3.client(host, port)

    def get_users(self) -> List[User]:
        """Getting sequence of users"""
        users = [
            User.from_dict(json.loads(user_value))
            for user_value, _ in self._client.get_prefix(
                STORAGE_USER_PREFIX_KEY)
        ]

        return users

    def put_user(self, user: User):
        """Adding user to storage"""
        self._client.put(STORAGE_USER_KEY.format(user_id=user.login),
                         json.dumps(asdict(user)))

    def put_message(self, message: Message):
        """Adding new queue message to storage"""
        unique_key = message.get_unique_queue_message_key()

        self._client.put(STORAGE_USER_MESSAGE_QUEUE_KEY.format(
                user_id=message.recipient,
                message_id=unique_key),
            json.dumps(asdict(message)))

    def get_user_queue_messages(self, user_login: str) -> List[Message]:
        """Getting sequence of queued messages for received user login"""
        prefix = STORAGE_USER_MESSAGE_QUEUE_PREFIX_KEY.format(
            user_id=user_login)

        messages = []
        for value, _ in self._client.get_prefix(prefix):
            message = Message.from_dict(json.loads(value))
            messages.append(message)

        return messages

    def delete_user_queue_message(self, message: Message):
        """Deleting queued message from the storage"""
        delete_key = STORAGE_USER_MESSAGE_QUEUE_KEY.format(
            user_id=message.recipient,
            message_id=message.get_unique_queue_message_key())

        self._client.delete(delete_key)
