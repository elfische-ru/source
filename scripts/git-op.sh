#!/bin/bash


ROOT_PATH=$(readlink -f $(dirname $0)/..)

source $ROOT_PATH/scripts/local.sh


function git-start {
    git \
        --git-dir=$STATIC_GIT_FOLDER/.git \
        --work-tree=$STATIC_GIT_FOLDER \
        $@
}

function git-op {
    git-start add -A
    git-start commit --amend --no-edit
    git-start tag -f $1
    git-start push -f origin public
    git-start push -f origin $1
}

git-op $@
