#!/bin/bash


function show_all_processes {
    cols=$(tput cols)
    export COLUMNS=1000

    ps -Af |\
    grep -E 'coffee|compass|sass' |\
    grep -v grep |\
    awk '{print substr($2" "substr($0, index($0,$8)), 0, '$cols')}'
}

function kill_all_processes {
    out_show=$(show_all_processes)
    echo -en "$out_show"
    kill $(echo -en "$out_show" | awk '{print $1}')
}


case $1 in
    kill)
        kill_all_processes
        ;;
    watch)
        watch -n1 $0
        ;;
    *)
        show_all_processes
        ;;
esac

exit 0
