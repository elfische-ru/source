#!/bin/bash


function show_all_processes {
    cols=$(tput cols)
    export COLUMNS=1000

    out=$(
        ps -Af |\
        grep -E 'coffee|compass|sass' |\
        grep -v grep
    )

    if [ "$1" = "full" ]; then
        echo "$out" | awk '{print $2" "substr($0, index($0,$8))}'
    else
        echo "$out" | awk '{print substr($2" "substr($0, index($0,$8)), 0, '$cols')}'
    fi
}

function kill_all_processes {
    out_show=$(show_all_processes)
    if [ "$out_show" ]; then
        echo -en "$out_show"
        kill $(echo -en "$out_show" | awk '{print $1}')
    else
        echo 'none'
    fi
}


case $1 in
    kill)
        kill_all_processes
        ;;
    watch)
        watch -n1 $0
        ;;
    full)
        show_all_processes full
        ;;
    *)
        show_all_processes
        ;;
esac

exit 0
