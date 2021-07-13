"""Simple chat application"""
import os
import time
from datetime import datetime
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection

import simple_chat_pb2
import simple_chat_pb2_grpc
from simple_chat_etcd_storage import Storage


class SimpleChatServicer(simple_chat_pb2_grpc.SimpleChatServicer):
    """Provides methods that implement functionality of simple chat server."""

    def __init__(self, storage: Storage):
        self._storage = storage

    def GetUsers(self, request, context):
        """Obtains list of user"""
        return simple_chat_pb2.GetUsersResponse(
            users=self._storage.get_users())

    def SendMessage(self, request, context):
        """Put retrieved message to storage"""
        message = {
            "sender": request.message.sender,
            "recipient": request.message.recipient,
            "created": datetime.timestamp(datetime.now()),
            "body": request.message.body,
        }

        self._storage.put_message(message)

        return simple_chat_pb2.SendMessageResponse()

    def ReceiveMessages(self, request, context):
        """Subscribe user to receive messages. Results are
        streamed rather than returned at once.
        Deleting queued messages from the storage after getting their.
        """
        while True:
            messages = self._storage.get_user_queue_messages(request.login)

            for message, key in messages:
                yield message
                self._storage.delete_user_queue_message(key)

            time.sleep(1)


def enable_reflection(server):
    """Provides reflection for the server"""
    SERVICE_NAMES = (
        simple_chat_pb2.DESCRIPTOR.services_by_name['SimpleChat'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)


def create_server(server_address, storage):
    """Create server and doing additional actions with server here"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    simple_chat_pb2_grpc.add_SimpleChatServicer_to_server(
        SimpleChatServicer(storage), server)

    # enable_reflection(server)

    server.add_insecure_port(server_address)
    return server


def main(server_host, server_port, storage_host, storage_port):
    """Start point"""
    storage = Storage(host=storage_host, port=storage_port)

    server_address = "{}:{}".format(server_host, server_port)
    server = create_server(server_address, storage)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    host = os.environ['SERVER_HOST']
    port = os.environ['SERVER_PORT']
    etcd_host = os.environ['ETCD_SERVER_HOST']
    etcd_port = os.environ['ETCD_SERVER_PORT']

    main(host, port, etcd_host, etcd_port)
