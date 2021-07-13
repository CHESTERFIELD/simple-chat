import json
import os

from simple_chat_etcd_storage import Storage, get_etcd_storage_connection


def load_users_to_storage(file_path: str, etcd_storage: Storage):
    """Load list of users to storage from json file"""
    with open(file_path, "r") as f:
        for user in json.load(f):
            etcd_storage.put_user(user)

    return True


if __name__ == '__main__':
    storage = get_etcd_storage_connection(
        os.environ['ETCD_SERVER_HOST'], os.environ['ETCD_SERVER_PORT'])

    load_users_to_storage('users.json', storage)
