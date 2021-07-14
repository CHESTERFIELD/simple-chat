"""Simple chat application"""
import os
import time
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection
from google.protobuf.timestamp_pb2 import Timestamp

import simple_chat_pb2
import simple_chat_pb2_grpc
from simple_chat_etcd_storage import Storage, Message


class SimpleChatServicer(simple_chat_pb2_grpc.SimpleChatServicer):
    """Provides methods that implement functionality of simple chat server."""

    def __init__(self, storage: Storage):
        self._storage = storage

    def GetUsers(self, request, context):
        """Obtains list of user"""
        return simple_chat_pb2.GetUsersResponse(
            users=[simple_chat_pb2.User(login=user.login,
                                        full_name=user.full_name)
                   for user in self._storage.get_users()])

    def SendMessage(self, request, context):
        """Put retrieved message to storage"""
        message = Message(request.message.sender,
                          request.message.recipient,
                          request.message.body)

        self._storage.put_message(message)

        return simple_chat_pb2.SendMessageResponse()

    def ReceiveMessages(self, request, context):
        """Subscribe user to receive messages. Results are
        streamed rather than returned at once.
        Deleting queued messages from the storage after getting their.
        """
        while True:
            messages = self._storage.get_user_queue_messages(request.login)

            for message in messages:
                timestamp = Timestamp()
                timestamp.FromSeconds(int(message.created))
                yield simple_chat_pb2.Message(
                    sender=message.sender,
                    recipient=message.recipient,
                    body=message.body,
                    created=timestamp)

                self._storage.delete_user_queue_message(message)

            time.sleep(1)


def enable_reflection(server):
    """Provides reflection for the server"""
    SERVICE_NAMES = (
        simple_chat_pb2.DESCRIPTOR.services_by_name['SimpleChat'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)


def create_server(server_address: str, storage: Storage,
                  is_enable_reflection: bool) -> grpc.server:
    """Create server and doing additional actions with server here"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    simple_chat_pb2_grpc.add_SimpleChatServicer_to_server(
        SimpleChatServicer(storage), server)

    if is_enable_reflection:
        enable_reflection(server)

    server.add_insecure_port(server_address)
    return server


def main(server_host: str, server_port: str, storage_host: str,
         storage_port: str, is_enable_reflection: bool = False):
    """Start point"""
    storage = Storage(host=storage_host, port=storage_port)

    server_address = "{}:{}".format(server_host, server_port)
    server = create_server(server_address, storage, is_enable_reflection)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    host = os.environ['SERVER_HOST']
    port = os.environ['SERVER_PORT']
    etcd_host = os.environ['ETCD_SERVER_HOST']
    etcd_port = os.environ['ETCD_SERVER_PORT']
    is_reflected = bool(os.environ['REFLECTION'])

    main(host, port, etcd_host, etcd_port, is_reflected)
