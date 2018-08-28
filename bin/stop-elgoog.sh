#!/usr/bin/env bash

bin=$(dirname $0)
bin=$(cd "$bin"; pwd)

. "$bin"/elgoog-config.sh

gconf="$ELGOOG_CONF_DIR"/gunicorn.py

echo "stop elgoog"

target_pid=$("$PYTHON" "$bin"/cat_pid.py "$gconf")

if kill -0 $target_pid > /dev/null 2>&1; then
    echo "kill $target_pid"
    kill $target_pid
    sleep 3
    if kill -0 $target_pid > /dev/null 2>&1; then
        echo "elgoog did not stop gracefully after 3 seconds"
    else
        echo "elgoog stopped"
    fi
else
    echo "no elgoog to stop"
fi