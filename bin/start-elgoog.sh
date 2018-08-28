#!/usr/bin/env bash

bin=$(dirname $0)
bin=$(cd "$bin"; pwd)

. "$bin"/elgoog-config.sh

if [ ! -d "$ELGOOG_LOG_DIR" ]; then
    mkdir -p "$ELGOOG_LOG_DIR"
fi
if [ ! -d "$ELGOOG_PID_DIR" ]; then
    mkdir -p "$ELGOOG_PID_DIR"
fi

gconf="$ELGOOG_CONF_DIR"/gunicorn.py

echo "start elgoog"

cd "$ELGOOG_HOME"
gunicorn -c "$gconf" -D "elgoog.app:create_app()" $@
cd - > /dev/null

sleep 3
target_pid=$("$PYTHON" "$bin"/cat_pid.py "$gconf")
if ! ps -p $target_pid > /dev/null 2>&1; then
    echo "fail to start elgoog"
    exit 1
else
    echo "elgoog started"
fi