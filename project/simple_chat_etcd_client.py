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

    def get_users(self) -> tuple:
        """Getting sequence of users"""
        users = self._client.get_prefix(self.USER_PREFIX_KEY)

        return users

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
        """Adding new message to store"""
        max_key = self.get_max_key_user_queue_message(message['recipient']) + 1

        self._client.put(
            self.USER_MESSAGE_QUEUE_KEY.format(
                user_id=message['recipient'],
                message_id=max_key),
            json.dumps(message)
        )

    def get_max_key_user_queue_message(self, user_login) -> int:
        """Finding max key value of queued messages for received user login"""
        messages = self._client.get_prefix(
            self.USER_MESSAGE_QUEUE_PREFIX_KEY.format(user_id=user_login),
            keys_only=True
        )
        messages_keys = [message[1].key.decode('utf-8') for message in messages]

        max_key = int(max(messages_keys).split('/')[-1]) if messages_keys else 0

        return max_key

    def get_user_queue_messages(self, user_login) -> tuple:
        """Getting sequence of queued messages for received user's login.
        Deleting queued messages from the store after getting their.
        """

        prefix = self.USER_MESSAGE_QUEUE_PREFIX_KEY.format(user_id=user_login)
        messages = self._client.get_prefix(prefix)

        self._client.delete_prefix(prefix)

        return messages


def run():
    client = EtcdClient(2379)
    client.get_user_queue_messages('1313')


if __name__ == '__main__':
    run()
