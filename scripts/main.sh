#!/bin/bash


ROOT_PATH=$(readlink -f $(dirname $0)/..)
source $ROOT_PATH/scripts/local.sh

APP_LOG_PATH=$ROOT_PATH/tmp/app.log


function _message {
    echo "== $1" | tee -a $APP_LOG_PATH
}

function _coffee {
    pid_path=$ROOT_PATH/tmp/coffee-$2.pid


    case $1 in
        start)
            coffee \
                --watch \
                --compile \
                --output $4 \
                $3 \
                >> $ROOT_PATH/tmp/coffee.log \
                2>&1 \
                &
            echo $! > $pid_path
            ;;
        stop)
            if [ -e $pid_path ]; then
                pid=$(cat $pid_path)
                kill $pid
                while [[ -d /proc/$pid ]]; do
                    sleep 0.5
                done
                rm $pid_path
            fi
            ;;
    esac
}

function _sass {
    pid_path=$ROOT_PATH/tmp/sass-$2.pid

    case $1 in
        start)
            compass \
                watch \
                --debug-info \
                --sass-dir $3 \
                --css-dir $4 \
                >> $ROOT_PATH/tmp/sass.log \
                2>&1 \
                &
            echo $! > $pid_path
            ;;
        stop)
            if [ -e $pid_path ]; then
                pid=$(cat $pid_path)
                kill $pid
                while [[ -d /proc/$pid ]]; do
                    sleep 0.5
                done
                rm $pid_path
            fi
            ;;
    esac

}

function _app {
    case $1 in
        start)
            dev_appserver \
                --allow_skipped_files \
                --storage_path=$ROOT_PATH/tmp/_db \
                $ROOT_PATH/app \
                >> $APP_LOG_PATH \
                2>&1 \
                &
            ;;
        stop)
            pids=$(\
                ps -Af |\
                grep -v grep |\
                grep -E "dev_appserver.*$ROOT_PATH" |\
                awk '{print $2}' \
            )

            if [ "$pids" ]; then
                for pid in ${pids[@]}; do
                    kill $pid
                    while [[ -d /proc/$pid ]]; do
                        sleep 0.5
                    done
                done
            fi
            ;;
    esac
}

function start {
    _message 'start'

    _coffee start client \
        $ROOT_PATH/static/coffee \
        $ROOT_PATH/tmp/generated/js

    _sass start client \
        $ROOT_PATH/static/sass \
        $ROOT_PATH/tmp/generated/css

    _app start
}

function stop {
    _message 'stop'

    _coffee stop client
    _sass stop client
    _app stop
}

function app_restart {
    _message 'app restart'

    _app stop
    _app start
}


case $1 in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    app_restart)
        app_restart
        ;;
    *)
        echo "usage: $0 {start|stop|restart|app_restart}"
        ;;
esac

exit 0
