FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED 1

COPY ./docker/server/req.txt req.txt
COPY ./src /src
COPY ./docker/server/entrypoint.sh /server/entrypoint.sh

RUN python3 -m pip install --upgrade pip \
    && pip install -r req.txt

RUN sed -i 's/\r//' /server/entrypoint.sh \
    && chmod +x /server/entrypoint.sh

EXPOSE 50052
WORKDIR /src/project

ENTRYPOINT ["../../server/entrypoint.sh"]