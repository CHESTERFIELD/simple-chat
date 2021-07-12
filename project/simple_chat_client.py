"""Simple chat application for client"""
import argparse

import grpc
from google.protobuf.internal.well_known_types import Timestamp
from google.protobuf.json_format import MessageToDict

import simple_chat_pb2
import simple_chat_pb2_grpc


def create_arg_parser():
    """Creates and returns the ArgumentParser object"""
    parser = argparse.ArgumentParser(description='Simple chat client')
    parser.add_argument('method', help='Type of method', type=str,
                        choices=['users', 'send', 'receive']
                        )
    parser.add_argument('-s', '--sender', help='Sender login', type=str)
    parser.add_argument('-r', '--recipient', help='Recipient login', type=str)
    parser.add_argument('-b', '--body', help='Message body', type=str)

    return parser


def get_users(stub):
    """Get list of user"""
    users = stub.GetUsers(simple_chat_pb2.GetUsersRequest())
    for user in MessageToDict(users)['users']:
        print("User login: {}. User full name: {}"
              .format(user['login'], user['fullName'])
              )


def validate_send_message_data(data):
    """Validation that all necessary data is given"""
    if not all((data.body, data.recipient, data.sender)):
        raise ValueError(
            'The following fields are required: "sender", "body", "recipient"'
        )


def send_message(stub, data):
    """Send retrieved message data to recipient"""
    validate_send_message_data(data)

    simple_message = simple_chat_pb2.Message(
        sender=data.sender,
        recipient=data.recipient,
        body=data.body,
    )

    stub.SendMessage(
        simple_chat_pb2.SendMessageRequest(message=simple_message)
    )
    print("Message was sent")


def validate_receive_messages_data(data):
    """Validation that all necessary data is given"""
    if not data.recipient:
        raise ValueError('Login has not been received')


def receive_messages(stub, data):
    """Subscribe client to receive messages """
    validate_receive_messages_data(data)

    messages_iterator = stub.ReceiveMessages(
        simple_chat_pb2.ReceiveMessagesRequest(login=data.recipient)
    )

    for message in messages_iterator:
        print("From: {0}. \nTo: {1}. \nTime: {2}. \nMessage: '{3}'.\n"
              .format(message.sender,
                      message.recipient,
                      Timestamp.ToDatetime(message.created),
                      message.body
                      )
              )


def submit_request(stub, data):
    """Defining what request will be submitted"""
    if data.method == 'users':
        get_users(stub)
    elif data.method == 'send':
        send_message(stub, data)
    elif data.method == 'receive':
        receive_messages(stub, data)


def run(host, port):
    """Start point"""
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()

    server_address = host + ":" + str(port)
    with grpc.insecure_channel(server_address) as channel:
        stub = simple_chat_pb2_grpc.SimpleChatStub(channel)
        submit_request(stub, parsed_args)


if __name__ == "__main__":
    run('localhost', 50052)
