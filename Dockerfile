FROM python:3.5.6-alpine3.8

RUN apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install flask flask-socketio eventlet && \
    apk del .build-deps gcc musl-dev 
