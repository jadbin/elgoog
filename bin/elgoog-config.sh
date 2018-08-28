#!/usr/bin/env bash

bin=$(dirname $0)
bin=$(cd "$bin"; pwd)

export ELGOOG_HOME=${ELGOOG_HOME:-$(cd "$bin"/../; pwd)}
export ELGOOG_CONF_DIR=${ELGOOG_CONF_DIR:-"$ELGOOG_HOME"/conf}

if [ -f "$ELGOOG_CONF_DIR"/elgoog-env.sh ]; then
    . "$ELGOOG_CONF_DIR"/elgoog-env.sh
fi

export ELGOOG_LOG_DIR=${ELGOOG_LOG_DIR:-"$ELGOOG_HOME"/.log}
export ELGOOG_PID_DIR=${ELGOOG_PID_DIR:-"$ELGOOG_HOME"/.pid}
export ELGOOG_ID_STRING=${ELGOOG_ID_STRING:-$USER}
