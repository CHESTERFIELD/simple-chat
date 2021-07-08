"""Simple chat application for client"""
import argparse
import json

import grpc

import simple_chat_pb2
import simple_chat_pb2_grpc


def create_arg_parser():
    """Creates and returns the ArgumentParser object"""
    parser = argparse.ArgumentParser(description='Simple chat client')
    parser.add_argument('-d', '--json-data', help='String that contains json format',
                        default='{}', type=str
                        )
    parser.add_argument('-m', '--method', help='Type of method', type=str,
                        choices=['get_users', 'send_message', 'receive_messages']
                        )
    return parser


def get_users(stub):
    """Get list of user"""
    users = stub.GetUsers(simple_chat_pb2.GetUsersRequest())
    print(users)


def validate_send_message_data(data: dict) -> dict:
    """Validation that all necessary data is given
    :return: dict of message data
    """
    if 'message' not in data:
        raise ValueError('Message has not been received')

    for field in ('sender', 'recipient', 'body'):
        if not data['message'].get(field, None):
            raise ValueError('Message must have "{}" field'.format(field))

    return data["message"]


def send_message(stub, data):
    """Send retrieved message data to recipient"""
    message = validate_send_message_data(data)

    send_message = simple_chat_pb2.Message(
        sender=message["sender"],
        recipient=message["recipient"],
        body=message["body"],
    )

    response = stub.SendMessage(
        simple_chat_pb2.SendMessageRequest(message=send_message)
    )
    print(response)


def validate_receive_messages_data(data: dict) -> str:
    """Validation that all necessary data is given
    :return: string of user's login
    """
    if 'login' not in data or not data['login']:
        raise ValueError('Login has not been received')

    return data['login']


def receive_messages(stub, data):
    """Subscribe client to receive messages """
    login = validate_receive_messages_data(data)

    messages_iterator = stub.ReceiveMessages(
        simple_chat_pb2.ReceiveMessagesRequest(login=login)
    )
    for message in messages_iterator:
        print(message)


def validate_parser_arguments(json_data: str) -> dict:
    """Validation that received data is json string"""
    try:
        data = json.loads(json_data)
    except Exception as ex:
        raise ex

    return data


def submit_request(stub, method, data):
    """Defining what request will be submitted"""
    if method == 'get_users':
        get_users(stub)
    elif method == 'send_message':
        send_message(stub, data)
    elif method == 'receive_messages':
        receive_messages(stub, data)


def run():
    """Start point"""
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args()
    data = validate_parser_arguments(parsed_args.json_data)

    with grpc.insecure_channel('localhost:50052') as channel:
        stub = simple_chat_pb2_grpc.SimpleChatStub(channel)
        submit_request(stub=stub, method=parsed_args.method, data=data)


if __name__ == "__main__":
    run()
