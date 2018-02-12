#!/bin/bash
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

# https://stackoverflow.com/questions/242538/unix-shell-script-find-out-which-directory-the-script-file-resides
# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "${0}")
# Absolute path this script is in, thus /home/user/bin
SCRIPT_PATH=$(dirname "${SCRIPT}")

cd "$SCRIPT_PATH"

if [ "${1}" = '--help' ] || [ "${1}" = '-h' ] ; then
  python bootstrap.py "${1}"
  exit 0
fi

INST=''
pip show -q xrosfs
if [ "${?}" -ne 0 ] ; then
  pip install -e ./.. && INST='ON'
fi

python bootstrap.py "${@}"
TEST_STAUS="${?}"

if [ "${INST}" = 'ON' ] ; then
    pip uninstall -q -y xrosfs
fi

exit "${TEST_STAUS}"
