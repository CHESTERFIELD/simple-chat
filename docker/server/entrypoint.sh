#!/bin/bash

echo $(pwd)
echo $(ls -la)

python run_protos.py
python simple_chat_server.py