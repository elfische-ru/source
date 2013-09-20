#!/bin/bash


ROOT_PATH=$(readlink -f $(dirname $0)/..)

source $ROOT_PATH/scripts/local.sh

VERSION=$(sed -rne 's/^version: (.*)\s+/\1/p' $ROOT_PATH/app/app.yaml)
VERSION_TARGET=$STATIC_GIT_FOLDER/build/$VERSION


function _message {
    echo "== $1"
}

function remove-sass-debug {
    find \
        $1 \
        -name '*.css' \
        -exec \
            sed -ri '/(@media -sass-debug-info|\/\* line)/d' '{}' \;
}

function build_static {
    # images
    current_target=$VERSION_TARGET/images
    mkdir -p $current_target

    rsync -a -del --progress\
        $ROOT_PATH/static/images/ \
        $current_target/


    # css
    current_target=$VERSION_TARGET/css
    mkdir -p $current_target

    cp \
        $ROOT_PATH/tmp/generated/css/main.css \
        $current_target/

    remove-sass-debug $current_target


    # js
    current_target=$VERSION_TARGET/js/generated
    mkdir -p $current_target

    rsync -a -del --progress\
        $ROOT_PATH/tmp/generated/js/ \
        $current_target/

    current_target=$VERSION_TARGET/js/lib/
    mkdir -p $current_target

    rsync -a -del --progress\
        $ROOT_PATH/static/coffee/js_lib/ \
        $current_target/


    # font
    build_font
}

function build_font {
    target=$VERSION_TARGET/fonts
    mkdir -p $target

    fontforge \
        -script $ROOT_PATH/static/fonts/icons.pe \
        $ROOT_PATH/static/fonts \
        $target \
        icons

    rm $target/icons.afm
}

function deploy_static {
    build_static

    git \
        --git-dir=$STATIC_GIT_FOLDER/.git \
        --work-tree=$STATIC_GIT_FOLDER \
        add -A .

    git \
        --git-dir=$STATIC_GIT_FOLDER/.git \
        --work-tree=$STATIC_GIT_FOLDER \
        commit --amend -m 'tmp1'

    git \
        --git-dir=$STATIC_GIT_FOLDER/.git \
        --work-tree=$STATIC_GIT_FOLDER \
        push -f origin gh-pages
}

function deploy_app {
    appcfg \
        -e sa.mcandrews@gmail.com \
        update \
        $ROOT_PATH/app
}


case $1 in
    app)
        deploy_app
        ;;
    static)
        deploy_static
        ;;
    build_static)
        build_static
        # build_font
        ;;
    all)
        deploy_static
        deploy_app
        ;;
    *)
        echo "usage: $0 {static|app|all}"
        ;;
esac

exit 0
