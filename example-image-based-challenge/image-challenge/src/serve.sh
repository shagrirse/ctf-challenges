#!/bin/sh
socat \
    -T60 \
    TCP-LISTEN:8080,reuseaddr,fork \
    EXEC:"timeout 60 ./server.py"