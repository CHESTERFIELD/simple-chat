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