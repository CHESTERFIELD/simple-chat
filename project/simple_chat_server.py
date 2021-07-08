"""Simple chat application"""
import datetime
import json
import time
from concurrent import futures

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from grpc_reflection.v1alpha import reflection

import simple_chat_pb2
import simple_chat_pb2_grpc


def load_users(file_path: str) -> list:
    """Load list of users from json file"""
    users = []
    with open(file_path, "r") as f:
        for user in json.load(f):
            new_user = simple_chat_pb2.User(
                login=user['login'],
                full_name=user.get("full_name", "")
            )
            users.append(new_user)

    return users


class SimpleChatServicer(simple_chat_pb2_grpc.SimpleChatServicer):
    """Provides methods that implement functionality of simple chat server."""

    def __init__(self, users):
        self._users = users
        self._queue = {}

    def GetUsers(self, request, context):
        """Obtains list of user"""
        return simple_chat_pb2.GetUsersResponse(users=self._users)

    def SendMessage(self, request, context):
        """Send retrieved message to user"""
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.datetime.now())

        message = simple_chat_pb2.Message(
            sender=request.message.sender,
            recipient=request.message.recipient,
            created=timestamp,
            body=request.message.body,
        )

        if request.message.recipient in self._queue:
            self._queue[request.message.recipient].append(message)
        else:
            self._queue[request.message.recipient] = [message, ]

        return simple_chat_pb2.SendMessageResponse()

    def ReceiveMessages(self, request, context):
        """Subscribe user to receive messages. Results are
        streamed rather than returned at once
        """
        while True:
            if request.login in self._queue:
                for message in self._queue[request.login]:
                    if message.recipient == request.login:
                        self._queue[request.login].remove(message)
                        yield message
            time.sleep(1)


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

    users = load_users('users.json')
    simple_chat_pb2_grpc.add_SimpleChatServicer_to_server(
        SimpleChatServicer(users),
        server
    )
    # enable_reflection(server)

    server.add_insecure_port(server_address)
    return server


def main():
    """Start point"""
    server = create_server('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()
