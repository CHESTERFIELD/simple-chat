"""The class implementation that work with key-value store"""
import json

import etcd3


class EtcdClient:
    """Provides methods that implement functionality of key-value store"""
    USER_KEY = 'user/{user_id}'
    USER_MESSAGE_QUEUE_KEY = 'message/queue/user/{user_id}/{message_id}'
    USER_PREFIX_KEY = 'user/'
    USER_MESSAGE_QUEUE_PREFIX_KEY = 'message/queue/user/{user_id}'

    def __init__(self, port, host='127.0.0.1'):
        self._client = etcd3.client(host=host, port=port)

    def get_users(self):
        """Getting sequence of users"""
        users_iterator = self._client.get_prefix(self.USER_PREFIX_KEY)

        return users_iterator

    def get_user(self, user_login: str):
        """Getting user"""
        user = self._client.get(self.USER_KEY.format(user_id=user_login))
        return user

    def put_user(self, user):
        """Adding user to store"""
        self._client.put(
            self.USER_KEY.format(user_id=user['login']),
            json.dumps(user)
        )

    def put_message(self, message: dict):
        """Adding new queue message to store"""
        unique_key = self.create_unique_queue_message_key(message)

        self._client.put(
            self.USER_MESSAGE_QUEUE_KEY.format(
                user_id=message['recipient'],
                message_id=unique_key),
            json.dumps(message)
        )

    @staticmethod
    def create_unique_queue_message_key(message: dict) -> str:
        """Creating unique key value for message"""
        unique_key = message['sender'] + str(message['created']) + message['recipient']

        return unique_key

    def get_user_queue_messages(self, user_login):
        """Getting sequence of queued messages for received user login"""

        prefix = self.USER_MESSAGE_QUEUE_PREFIX_KEY.format(user_id=user_login)
        messages_iterator = self._client.get_prefix(prefix)

        return messages_iterator

    def delete_user_queue_message(self, message_key: str):
        """Deleting queued message from the store"""
        self._client.delete(message_key)

    def watch_user_queue_messages(self, user_login):
        """Watcher for new queued messages by user login"""

        prefix = self.USER_MESSAGE_QUEUE_PREFIX_KEY.format(user_id=user_login)
        messages_iterator, cancel = self._client.watch_prefix(prefix)

        return messages_iterator, cancel


def run():
    client = EtcdClient(2379)
    messages_iterator, cancel = client.watch_user_queue_messages('1313')
    for message in messages_iterator:
        print(message)


if __name__ == '__main__':
    run()
