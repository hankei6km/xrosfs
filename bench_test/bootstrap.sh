#!/bin/bash
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.


if [ "${1}" = '--help' ] || [ "${1}" = '-h' ] ; then
  python bootstrap.py "${1}"
  exit 0
fi

INST=''
pip show -q xrosfs
if [ "${?}" -ne 0 ] ; then
    pip install -e ../. && INST='ON'
fi

python bootstrap.py "${@}"

if [ "${INST}" = 'ON' ] ; then
    pip uninstall -q -y xrosfs
fi
