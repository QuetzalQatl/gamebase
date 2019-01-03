FROM python:3.5.6-alpine3.8

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN pip install flask flask-socketio eventlet
RUN apk del .build-deps gcc musl-dev

COPY ColorPicker /
