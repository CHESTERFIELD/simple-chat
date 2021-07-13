FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED 1

COPY ./docker/server/req.txt req.txt
COPY ./src /src
COPY ./docker/server/entrypoint.sh /server/entrypoint.sh

WORKDIR /src/project

RUN python3 -m pip install --upgrade pip \
    && pip install -r ../../req.txt \
    && python3 -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/simple_chat.proto \
    && sed -i 's/\r//' /server/entrypoint.sh \
    && chmod +x /server/entrypoint.sh

EXPOSE 50052

ENTRYPOINT ["../../server/entrypoint.sh"]