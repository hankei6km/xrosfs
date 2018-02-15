# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import pytest
# import unittest
from unittest import mock
import queue
import shlex
import base64
from xrosfs.conshell import ConShell, EntryResult

# mock = unittest.mock
Mock = mock.Mock


def get_mock_conshell(res, logger=Mock()):
    q = queue.Queue()  # dummy stream

    # rules = iter((
    #     (b'\x01', base64.b64encode(b'test')),
    #     (b'\x01', b'\n0\0\0\0:'),
    #     (b'\x02', b'res error'),
    #     (b'\x01', b'\n1\0\0\0:')))
    iter_res = iter(res)

    shell = ConShell(logger=logger)
    # Skip ConShell#connect

    shell._shell_args = '--noprofile --norc'
    shell._prefix_command = 'LC_ALL=C set -o pipefail;'
    shell._shell_name = 'bash'
    shell._shell_path = '/bin/bash'

    def entry_command_effect(command):
        res = iter(next(iter_res))
        for fd_data in zip(res, res):
            q.put(fd_data)

    def read_result_effect():
        return q.get(timeout=1)

    def entry_effect(command, **kwargs):
        ret = org_entry(command, **kwargs)
        return (ret.stdout, ret.errno, ret.stderr)

    shell._entry_command = Mock(
        spec_set=shell._entry_command,
        side_effect=entry_command_effect)
    shell._read_result = Mock(
        spec_set=shell._read_result,
        side_effect=read_result_effect)
    org_entry = shell.entry
    shell.entry = Mock(
        spec_set=shell.entry,
        side_effect=entry_effect)

    return shell, q


class TestConSehll():
    def test_get_shell_item(self):
        shell = ConShell()

        shell.entry = Mock(side_effect=(
            EntryResult('', 1, ''),
            EntryResult('', 1, ''),
            EntryResult('', 1, ''),
            EntryResult('', 1, ''),
            EntryResult('', 1, ''),
            EntryResult('', 1, ''),
            EntryResult('', 1, ''),
            EntryResult('/bin/ash', 0, ''),
        ))

        assert shell._get_shell_item() == {
            'shell_name': 'ash',
            'shell_path': '/bin/ash',
            'shell_args': '--noprofile --norc',
            'prefix_command': 'LC_ALL=C set -o pipefail;'
        }

    def test_switch_to_support_shell(self):
        shell = ConShell()

        shell.container = Mock()
        shell.container.exec_run = Mock(
            return_value='mock sh_stream'
        )
        shell._get_shell_item = Mock(
            return_value={
                'shell_name': 'bash',
                'shell_path': '/bin/bash',
                'shell_args': '--noprofile --norc',
                'prefix_command': 'LC_ALL=C set -o pipefail;'
            }
        )
        shell.entry = Mock()

        shell._switch_to_support_shell()
        shell.container.exec_run.assert_called_once_with(
            '/bin/bash --noprofile --norc', user='', socket=True, stdin=True)
        assert shell.sh_stream == 'mock sh_stream'

        # not installed support shell
        shell._get_shell_item = Mock(
            return_value=None
        )

        with pytest.raises(RuntimeError) as excinfo:
            shell._switch_to_support_shell()
        assert 'not installed support shell' in str(excinfo)

    def test_setup_init_shell(self):
        shell = ConShell()

        shell.container = Mock()
        shell.container.exec_run = Mock(
            return_value='mock sh_stream'
        )

        shell._setup_init_shell()
        shell.container.exec_run.assert_called_once_with(
            '/bin/sh ', user='', socket=True, stdin=True)
        assert shell.sh_stream == 'mock sh_stream'

    def test_setup_avail_cmd(self):
        import os
        shell = ConShell()
        shell._which_cmd = Mock(
            side_effect=lambda cmd_name: os.path.join('/bin', cmd_name)
        )
        shell.setup_avail_cmds(('cmd1', 'cmd2'))
        assert shell._avail_cmds == {
            'which': {
                'path': '/bin/which',
            },
            'umask': {
                'path': 'umask'  # function
            },
            'exec': {
                'path': 'exec'  # function
            },
            'exit': {
                'path': 'exit'  # function
            },
            'cmd1': {
                'path': '/bin/cmd1'
            },
            'cmd2': {
                'path': '/bin/cmd2'
            }
        }

    @mock.patch('docker.from_env')
    def test_connect(self, mock_from_env):

        # Prepare to called docker.from_env().containers.get().exec_run()
        container = Mock()
        container.exec_run.return_value = 'mock sh_stream'
        client = Mock()
        client.containers.get.return_value = container
        mock_from_env.return_value = client

        # Test
        container_name = 'container_that_lie'
        shell = ConShell()
        shell._switch_current_shell = Mock()
        shell._setup_init_shell = Mock()
        shell._switch_to_support_shell = Mock()
        shell.connect(container_name)

        client.containers.get.assert_called_once_with(
            container_name)
        shell._setup_init_shell.assert_called_once_with()
        shell._switch_to_support_shell.assert_called_once_with()

    @mock.patch('os.write')
    def test_entry_command(self, mock_write):

        shell = ConShell()
        # Skip ConShell#connect
        shell.sh_stream = Mock(**{'fileno.return_value': -1})

        # Test
        shell._entry_command('test')
        mock_write.assert_called_once_with(-1, b'test')

    def test_read_result(self):

        shell = ConShell()
        # Skip ConShell#connect
        shell.sh_stream = Mock(**{
            'read.side_effect':
            (b'\x01', b'\x00\x00\x00', b'\x00\x00\x00\x07', b'res test',
             b'\x02', b'\x00\x00\x00', b'\x00\x00\x00\x08', b'res error')
        })

        # Test
        assert shell._read_result() == (b'\x01', b'res test')
        calls = [
            mock.call(1),
            mock.call(3),
            mock.call(4),
            mock.call(7),
        ]
        shell.sh_stream.read.assert_has_calls(calls)
        assert shell.sh_stream.read.call_count == 4

        assert shell._read_result() == (b'\x02', b'res error')
        calls = [
            mock.call(1),
            mock.call(3),
            mock.call(4),
            mock.call(8),
        ]
        shell.sh_stream.read.assert_has_calls(calls)
        assert shell.sh_stream.read.call_count == 8

    def test_entry_basic(self):
        shell, q = get_mock_conshell((
            (b'\x01', base64.b64encode(b'test')),
            (b'\x01', b'\n0\0\0\0:'),
            (b'\x02', b'not found'),
            (b'\x01', b'\n1\0\0\0:')))

        # Test
        assert shell.entry(('echo', 'test')) == ('test', 0, '')
        assert shell.entry(('stat', '/foo/bar')) == ('', 1, 'not found')

        # Check internal works in ConShell
        assert q.empty()
        calls = [
            mock.call('LC_ALL=C set -o pipefail;echo test |base64\n'),
            mock.call(
                '/bin/echo -en "\\n${?}\\0\\0\\0:"\n'),
            mock.call('LC_ALL=C set -o pipefail;stat /foo/bar |base64\n'),
            mock.call(
                '/bin/echo -en "\\n${?}\\0\\0\\0:"\n'),
        ]
        shell._entry_command.assert_has_calls(calls)
        assert shell._entry_command.call_count == 4

    def test_entry_quote(self):
        shell, q = get_mock_conshell((
            (b'\x01', base64.b64encode(b'test\n')),
            (b'\x01', b'\n0\0\0\0:')))

        # Test
        assert shell.entry([
            shlex.quote('echo'),
            shlex.quote('T\'&&est'),
            '|',
            shlex.quote('sed'),
            shlex.quote('-e'),
            shlex.quote('s/T\'&&/t/'),
        ], quote=False) == ('test\n', 0, '')

        # Check args in command was quoted
        assert q.empty()
        calls = [
            mock.call(
                'LC_ALL=C set -o pipefail;echo \'T\'"\'"\'&&est\' | '
                'sed -e \'s/T\'"\'"\'&&/t/\' |base64\n'),
            mock.call(
                '/bin/echo -en "\\n${?}\\0\\0\\0:"\n'),
        ]
        shell._entry_command.assert_has_calls(calls)
        assert shell._entry_command.call_count == 2

    def test_entry_stdin_data(self):
        shell, q = get_mock_conshell((
            (b'\x01', base64.b64encode(b'test\m')),
            (b'\x01', b'\n0\0\0\0:')))

        # Test
        assert shell.entry([
            'sed', '-e', 's/T\'&&/t/',
        ], stdin_data=b'T\'&&st') == ('test\m', 0, '')

        # Check args in command was quoted
        assert q.empty()
        calls = [
            mock.call(
                'LC_ALL=C set -o pipefail;echo -n VCcmJnN0|base64 -d|'
                'sed -e \'s/T\'"\'"\'&&/t/\' |base64\n'),
            mock.call(
                '/bin/echo -en "\\n${?}\\0\\0\\0:"\n'),
        ]
        shell._entry_command.assert_has_calls(calls)
        assert shell._entry_command.call_count == 2

    def test_entry_mixin_stderr_to_stdout(self):
        shell, q = get_mock_conshell((
            (b'\x01', base64.b64encode(b'test\n')),
            (b'\x01', b'\n0\0\0\0:')))

        # Test
        assert shell.entry([
            'dummy', 'args'
        ], mixin_stderr_to_stdout=True) == ('test\n', 0, '')

        # Check args in command was quoted
        assert q.empty()
        calls = [
            mock.call(
                'LC_ALL=C set -o pipefail;dummy args 2>&1 |base64\n'),
            mock.call(
                '/bin/echo -en "\\n${?}\\0\\0\\0:"\n'),
        ]
        shell._entry_command.assert_has_calls(calls)
        assert shell._entry_command.call_count == 2

    def test_entry_std_to_str(self):
        shell, q = get_mock_conshell((
            (b'\x01', base64.b64encode(b'test')),
            (b'\x01', b'\n0\0\0\0:')))

        # Test
        assert shell.entry((
            'echo', 'test'
        ), stdout_to_str=False) == (b'test', 0, '')

        # Check internal works in ConShell
        assert q.empty()
        calls = [
            mock.call('LC_ALL=C set -o pipefail;echo test |base64\n'),
            mock.call(
                '/bin/echo -en "\\n${?}\\0\\0\\0:"\n'),
        ]
        shell._entry_command.assert_has_calls(calls)
        assert shell._entry_command.call_count == 2

    def test_entry_disable_encode_stdoute_data(self):
        shell, q = get_mock_conshell((
            (b'\x01', b'test'),
            (b'\x01', b'\n0\0\0\0:')))

        # Test
        assert shell.entry((
            'echo', 'test'
        ), _disable_encode_stdoute_data=True) == ('test', 0, '')

        # Check internal works in ConShell
        assert q.empty()
        calls = [
            mock.call('LC_ALL=C set -o pipefail;echo test\n'),
            mock.call(
                '/bin/echo -en "\\n${?}\\0\\0\\0:"\n'),
        ]
        shell._entry_command.assert_has_calls(calls)
        assert shell._entry_command.call_count == 2

    def test_entry_convert_exception(self):
        shell, q = get_mock_conshell((
            (b'\x01', base64.b64encode(b'\xfftest\n')),
            (b'\x01', b'\n0\0\0\0:'),
            (b'\x02', b'ffnot found\n\xff'),
            (b'\x01', b'\n1\0\0\0:')))

        # Test
        with pytest.raises(UnicodeDecodeError) as excinfo:
            shell.entry(('echo', 'test'))
        assert "'utf-8' codec can't decode byte 0xff in position 0"\
               in str(excinfo)

        with pytest.raises(UnicodeDecodeError) as excinfo:
            shell.entry(('stat', '/foo/bar'))
        assert "'utf-8' codec can't decode byte 0xff in position 12"\
               in str(excinfo)


class TestConSehllLogger():
    def test_disable_logger_output(self):
        logger = Mock()
        logger.isEnabledFor = Mock(return_value=False)
        shell, q = get_mock_conshell(
            ((b'\x01', b'test'),
             (b'\x01', b'\n0\0\0\0:')),
            logger=logger
        )

        # Test
        assert shell.entry((
            'echo', 'test'
        ), _disable_encode_stdoute_data=True) == ('test', 0, '')

        assert not shell.logger.debug.called

    def test_enable_logger_output(self):
        logger = Mock()
        logger.isEnabledFor = Mock(return_value=True)
        shell, q = get_mock_conshell(
            ((b'\x01', b'test'),
             (b'\x01', b'\n0\0\0\0:')),
            logger=logger
        )

        # Test
        assert shell.entry((
            'echo', 'test'
        ), _disable_encode_stdoute_data=True) == ('test', 0, '')

        calls = [
            mock.call("#entry => ('echo', 'test')"),
            mock.call('#entry <= errno=0'),
            mock.call('#entry <= stdout=test'),
            mock.call('#entry <= stderr=')
        ]
        shell.logger.debug.assert_has_calls(calls)
