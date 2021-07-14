"""Simple chat script that load users to storage"""
import json
import os

from simple_chat_etcd_storage import Storage, User


def load_users_to_storage(file_path: str, etcd_storage: Storage):
    """Load list of users to storage from json file"""
    with open(file_path, "r") as f:
        for user in json.load(f):
            etcd_storage.put_user(User(user['login'], user['full_name']))

    return True


def get_etcd_storage_connection(host, port) -> 'Storage':
    """Creates new one etcd connection for working with storage"""
    etcd_storage = Storage(host, port)
    return etcd_storage


if __name__ == '__main__':
    storage = get_etcd_storage_connection(
        os.environ['ETCD_SERVER_HOST'], os.environ['ETCD_SERVER_PORT'])

    load_users_to_storage(os.path.abspath('data/users.json'), storage)
