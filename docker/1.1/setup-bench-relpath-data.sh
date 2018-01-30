#!/bin/sh

set -e

setup_relpath () {
    RELPATH_PATH="${MNT_BASE_PATH}"
    mkdir -p "${MNT_BASE_PATH}"
    echo "mounted relpath" > "${RELPATH_PATH}/test.txt"
}

MNT_BASE_PATH='/root/sshfs'
setup_relpath

MNT_BASE_PATH='/root/xrosfs'
setup_relpath
