##SERVER
For obtaining the list of users we use the following command:
```
grpcurl -plaintext -d '' localhost:50052 SimpleChat.GetUsers
```


For subscriber to receiving message we should use the following command:
```
grpcurl -plaintext -d '{"login": "[any_exist_login]"}' localhost:50052 SimpleChat.ReceiveMessages
```

For sending some message to user we use the command below:
```
grpcurl -plaintext -d '{"message": {"sender": "[any_exist_login]", "recipient": "[any_exist_login]", "body": "[message_text]"}}' localhost:50052 SimpleChat.SendMessage
```

If server don't use reflection, we use the command below:
```
grpcurl -import-path ./protos -proto simple_chat.proto list/describe
```

##CLIENT
For subscribe to receiving messages by client use the command below:
```
python simple_chat_client.py --json-data '{"login": "1313"}' --method receive_messages
```

For send message to user by client use the command below:
```
python simple_chat_client.py --json-data '{"message": {"sender": "1212", "recipient": "1313", "body": "Some text"}}' --method send_message
```