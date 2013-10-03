#!/bin/bash

ROOT_PATH=$(readlink -f $(dirname $0)/..)

source $ROOT_PATH/scripts/local.sh

VERSION=$(sed -rne 's/^version: (.*)\s+/\1/p' $ROOT_PATH/app/app.yaml)


function extract {
    $(\
        cd $ROOT_PATH; \
        pybabel extract \
            --msgid-bugs-address=$I18N_EMAIL \
            --copyright-holder=$I18N_COPYRIGHT_HOLDER \
            --project=$I18N_PROJECT \
            --version=$VERSION \
            -F app/$1.mapping \
            -o app/locale/$1.pot \
            . \
    )
}

function init_domain {
    $(cd $ROOT_PATH; pybabel init -D $1 -l de_DE -d app/locale -i app/locale/$1.pot)
    $(cd $ROOT_PATH; pybabel init -D $1 -l ru_RU -d app/locale -i app/locale/$1.pot)
}

function update {
    $(cd $ROOT_PATH; pybabel update -D $1 -i app/locale/$1.pot -d app/locale)
}

function compile {
    $(cd $ROOT_PATH; pybabel compile -D $1 -d app/locale)
}


case $1 in
    init)
        init_domain base
        init_domain js
        ;;
    compile)
        compile base
        compile js
        ;;
    update)
        extract base
        update base
        extract js
        update js
        ;;
    *)
        echo "usage: $0 {init|compile|update}"
        ;;
esac

exit 0
