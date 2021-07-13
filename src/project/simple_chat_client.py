"""Simple chat application for client"""
import argparse

import grpc
from google.protobuf.internal.well_known_types import Timestamp

import simple_chat_pb2
import simple_chat_pb2_grpc
from simple_chat_etcd_storage import User, Message


def create_arg_parser():
    """Creates and returns the ArgumentParser object"""
    parser = argparse.ArgumentParser(description='Simple chat client')
    parser.add_argument('-H', '--host', help='Host of the server', type=str,
                        default='localhost')
    parser.add_argument('-p', '--port', help='Port of the server', type=int,
                        default=50052)
    parser.add_argument('method', help='Type of the method', type=str,
                        choices=['users', 'send', 'receive'])
    parser.add_argument('-s', '--sender', help='Sender login', type=str)
    parser.add_argument('-r', '--recipient', help='Recipient login', type=str)
    parser.add_argument('-b', '--body', help='Message body', type=str)

    return parser


def get_users(stub):
    """Get list of users"""
    response = stub.GetUsers(simple_chat_pb2.GetUsersRequest())

    for user in response.users:
        user = User(login=user.login, full_name=user.full_name)
        print(user)


def validate_send_message_data(sender, recipient, body):
    """Validates that all necessary data is given"""
    if not sender or not recipient or not body:
        raise ValueError('The following fields are required: '
                         '"sender", "recipient", "body"')


def send_message(stub, sender, recipient, body):
    """Sends retrieved message data to recipient"""
    validate_send_message_data(sender, recipient, body)

    stub.SendMessage(simple_chat_pb2.SendMessageRequest(
        message=simple_chat_pb2.Message(
            sender=sender,
            recipient=recipient,
            body=body)))

    print("Message was sent")


def validate_receive_messages_data(recipient):
    """Validation that all necessary data is given"""
    if not recipient:
        raise ValueError('Recipient has not been received')


def receive_messages(stub, recipient):
    """Subscribe client to receive messages """
    validate_receive_messages_data(recipient)

    messages = stub.ReceiveMessages(
        simple_chat_pb2.ReceiveMessagesRequest(login=recipient))

    for message in messages:
        message = Message(sender=message.sender, recipient=message.recipient,
                          created=Timestamp.ToDatetime(message.created),
                          body=message.body)
        print(message)


def submit_request(stub, data):
    """Defining what request will be submitted"""
    if data.method == 'users':
        get_users(stub)
    elif data.method == 'send':
        send_message(stub, data.sender, data.recipient, data.body)
    elif data.method == 'receive':
        receive_messages(stub, data.recipient)


def run():
    """Start point"""
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()

    server_address = "{}:{}".format(parsed_args.host, parsed_args.port)
    with grpc.insecure_channel(server_address) as channel:
        stub = simple_chat_pb2_grpc.SimpleChatStub(channel)
        submit_request(stub, parsed_args)


if __name__ == "__main__":
    run()
