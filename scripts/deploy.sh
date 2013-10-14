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

function rsync-start {
    mkdir -p ${VERSION_TARGET}${!#}
    rsync -a -del --progress \
        $(for item in ${@:1:${#@}-1}; do echo ${ROOT_PATH}$item; done) \
        ${VERSION_TARGET}${!#}
}


function generate_js {
    compressed_path=$VERSION_TARGET/js/compressed
    if [ ! -e $compressed_path ]; then
        mkdir $compressed_path
    fi

    find_path=${ROOT_PATH}/app/templates
    find $find_path -name '*.jinja2' -print0 |\
    while read -d $'\0' file; do
        result=$(sed -nE '/\{% jsfiles %\}/,/\{% endjsfiles %\}/p' $file | sed '1d;$d')
        if [ "$result" ]; then
            all_files=''
            for i in ${result[@]}; do
                all_files+=" $VERSION_TARGET/js$i"
            done
            compresed_file=$(echo ${file:((${#find_path}+1)):-7} | sed 's/\//_/g')'.js'
            cat $all_files > $compressed_path/$compresed_file
        fi
    done
}

function build_static {
    rsync-start  /static/images/                      /images/
    rsync-start  /tmp/generated/css/{home,about}.css  /css/
    rsync-start  /tmp/generated/js/                   /js/generated/
    rsync-start  /static/coffee/js_lib/               /js/lib/

    generate_js

    build_font
}

function build_font {
    target=$ROOT_PATH/app/static/fonts
    mkdir -p $target

    fontforge \
        -script $ROOT_PATH/static/fonts/icons.pe \
        $ROOT_PATH/static/fonts \
        $target \
        icons

    cp $ROOT_PATH/static/fonts/icons.svg $target

    rm $target/icons.afm
}

function git-start {
    git \
        --git-dir=$STATIC_GIT_FOLDER/.git \
        --work-tree=$STATIC_GIT_FOLDER \
        ${@}
}

function deploy_static {
    build_static

    git-start add -A .
    git-start commit --amend -m 'tmp1'
    git-start push -f origin gh-pages
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
        ;;
    build_font)
        build_font
        ;;
    all)
        deploy_static
        deploy_app
        ;;
    test)
        generate_js
        ;;
    *)
        echo "usage: $0 {static|app|all|build_static|build_font}"
        ;;
esac

exit 0
