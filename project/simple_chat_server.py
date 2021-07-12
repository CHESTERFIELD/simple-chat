"""Simple chat application"""
import time
from datetime import datetime
import json
from concurrent import futures

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from grpc_reflection.v1alpha import reflection

import simple_chat_pb2
import simple_chat_pb2_grpc
from simple_chat_etcd_client import EtcdClient


def load_users_to_store(file_path: str, store_client: EtcdClient):
    """Load list of users to store from json file"""

    with open(file_path, "r") as f:
        for user in json.load(f):
            store_client.put_user(user)


class SimpleChatServicer(simple_chat_pb2_grpc.SimpleChatServicer):
    """Provides methods that implement functionality of simple chat server."""

    def __init__(self, store_client):
        self._store_client = store_client

    def GetUsers(self, request, context):
        """Obtains list of user"""
        users = [
            simple_chat_pb2.User(**json.loads(user[0].decode('utf-8')))
            for user in self._store_client.get_users()
        ]

        return simple_chat_pb2.GetUsersResponse(users=users)

    def SendMessage(self, request, context):
        """Send retrieved message to user"""
        message = {
            "sender": request.message.sender,
            "recipient": request.message.recipient,
            "created": datetime.timestamp(datetime.now()),
            "body": request.message.body,
        }

        self._store_client.put_message(message)

        return simple_chat_pb2.SendMessageResponse()

    def ReceiveMessages(self, request, context):
        """Subscribe user to receive messages. Results are
        streamed rather than returned at once.
        Deleting queued messages from the store after getting their.
        """
        while True:
            messages_iterator = self._store_client.get_user_queue_messages(request.login)

            for queue_message in messages_iterator:
                message = json.loads(queue_message[0].decode('utf-8'))
                timestamp = Timestamp()
                timestamp.FromDatetime(datetime.fromtimestamp(message["created"]))
                message['created'] = timestamp

                yield simple_chat_pb2.Message(**message)

                self._store_client.delete_user_queue_message(queue_message[1].key.decode('utf-8'))

            time.sleep(1)


def enable_reflection(server):
    """Provides reflection for the server"""
    SERVICE_NAMES = (
        simple_chat_pb2.DESCRIPTOR.services_by_name['SimpleChat'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)


def create_server(server_address, etcd_port):
    """Create server and doing additional actions with server here"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    etcd_client = EtcdClient(etcd_port)
    load_users_to_store('users.json', etcd_client)

    simple_chat_pb2_grpc.add_SimpleChatServicer_to_server(
        SimpleChatServicer(etcd_client),
        server
    )
    # enable_reflection(server)

    server.add_insecure_port(server_address)
    return server


def main():
    """Start point"""
    server = create_server('[::]:50052', 2379)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()
