import datetime
import json
import time
from concurrent import futures

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from grpc_reflection.v1alpha import reflection

import simple_chat_pb2
import simple_chat_pb2_grpc


def init_users(file_path: str) -> list:
    """Initialize list of User from json file"""
    users = []
    with open(file_path, "r") as f:
        for user in json.loads(f.read()):
            new_user = simple_chat_pb2.User(
                login=user.get("login", ""),
                full_name=user.get("full_name", "")
            )
            users.append(new_user)

    return users


class SimpleChatServicer(simple_chat_pb2_grpc.SimpleChatServicer):
    """Provides methods that implement functionality of simple chat server."""

    def __init__(self):
        self._users = init_users('users.json')
        self._queue = []

    @property
    def users(self):
        return self._users

    @property
    def queue(self):
        return self._queue

    def GetUsers(self, request, context):
        return simple_chat_pb2.GetUsersResponse(users=self.users)

    def SendMessage(self, request, context):
        message = simple_chat_pb2.Message(
            sender=request.message.sender,
            recipient=request.message.recipient,
            created=Timestamp().FromDatetime(datetime.datetime.now()),
            body=request.message.body,
        )
        self.queue.append(message)

        return simple_chat_pb2.SendMessageResponse()

    def ReceiveMessages(self, request, context):
        while True:
            time.sleep(1)
            for message in self.queue:
                if message.recipient == request.login:
                    self.queue.remove(message)
                    yield message


def enable_reflection(server):
    """Provides reflection for the server"""
    SERVICE_NAMES = (
        simple_chat_pb2.DESCRIPTOR.services_by_name['SimpleChat'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)


def create_server(server_address):
    """Create server and doing additional actions with server here"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    simple_chat_pb2_grpc.add_SimpleChatServicer_to_server(SimpleChatServicer(), server)

    enable_reflection(server)

    port = server.add_insecure_port(server_address)
    return server, port


def serve(server):
    """Launch created server"""
    server.start()
    server.wait_for_termination()


def main():
    """Start point"""
    server, unused_port = create_server('[::]:50052')
    serve(server)


if __name__ == '__main__':
    main()
