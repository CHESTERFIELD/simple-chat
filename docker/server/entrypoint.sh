#!/bin/bash

echo $(pwd)
echo $(ls -la)

python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/simple_chat.proto
python simple_chat_server.py