# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

from unittest import mock
import pytest

from xrosfs.cmdbuilder import CmdBuilder
from xrosfs.conshell import ConShell

Mock = mock.Mock


def pytest_addoption(parser):
    parser.addoption('--pyclewn', action='store_true', default=False,
                     help='Wait to connect to pyclwen at run pytest')


def pytest_cmdline_main(config):
    pyclwen_opt = config.getoption('--pyclewn')
    if pyclwen_opt:
        from clewn.vim import pdb
        pdb()


@pytest.fixture
def conshell_mock_methods():
    ret = Mock(
        new_callable=ConShell,
    )
    # ret.entry = Mock()
    ret.quote.return_value = []
    return ret


@pytest.fixture
def cmdbuilder_mock_avail_cmds():
    CmdBuilder._avail_cmds = {
        'which': {
            'path': '/bin/which'
        },
        'pwd': {
            'path': '/usr/bin/pwd'
        },
        'ls': {
            'path': '/bin/ls'
        },
        'echo': {
            'path': '/bin/echo'
        },
        'stat': {
            'path': '/usr/bin/stat'
        },
        'test': {
            'path': '/usr/bin/test'
        },
        'chmod': {
            'path': '/bin/chmod'
        },
        'chown': {
            'path': '/bin/chown'
        },
        'readlink': {
            'path': '/bin/readlink'
        },
        'rm': {
            'path': '/bin/rm'
        },
        'rmdir': {
            'path': '/usr/bin/rmdir'
        },
        'mkdir': {
            'path': '/usr/bin/mkdir'
        },
        'ln': {
            'path': '/usr/bin/ln'
        },
        'mv': {
            'path': '/bin/mv'
        },
        'exec': {
            'path': 'exec'
        },
        'touch': {
            'path': '/usr/bin/touch'
        },
        'dd': {
            'path': '/bin/dd'
        },
        'truncate': {
            'path': '/usr/bin/truncate'
        }
    }

    return CmdBuilder
