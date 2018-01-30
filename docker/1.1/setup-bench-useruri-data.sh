#!/bin/sh

set -e

setup_useruri () {
    USERURI_PATH="${MNT_BASE_PATH}"
    mkdir -p "${MNT_BASE_PATH}"
    echo "mounted pdu user" > "${USERURI_PATH}/test.txt"
}

MNT_BASE_PATH='/home/pdu/sshfs'
setup_useruri

MNT_BASE_PATH='/home/pdu/xrosfs'
setup_useruri
