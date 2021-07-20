## Simple chat application created with gRPC framework and "etcd" key-value storage

### SERVER

* For launching the application in development mode 
write the following command:
```
docker-compose up
```
**NOTE**: you must have docker and docker-compose on your machine

* for loading some users to etcd service write following commands:
```
docker exec -it simple_chat_server_1 bash
python run_load_users.py
```

### CLIENT
* In order to submit any client request we have to join to 
  interactivity mode into the server container:
```
docker exec -it simple_chat_server_1 bash
```
* for getting users from etcd storage we should call next command:
```
python simple_chat_client.py users

# to get more helpful information about arguments
python simple_chat_client.py -h
```
* for sending message to user, call the next command:
```
python simple_chat_client.py send -s [sender] -r [recipient] -b '[body]'

# where [sender] is a sender login, 
# [recipient] is a recipient login 
# and [body] is a message text 
```
* for subscribing to message as user write the command below:
```
python simple_chat_client.py retreive -r [recipient]

# where [recipient] is a recipient login  
```

### TESTS

For launching tests we must be in the tests directory 
and write following command:
```
python -m unittest discover .
```