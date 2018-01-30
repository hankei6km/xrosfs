# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import shlex
import base64

import docker

from .xros_utils import init_logger


class CmdSet:
    avail_cmd = {
        'which': {
            'path': '/bin/which'
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

    def get_fullpath(self, cmd_name):
        ret = ''
        try:
            ret = self.avail_cmd[cmd_name]['path']
        except KeyError:
            raise RuntimeError('not found cmd full path: {0}'.format(cmd_name))

        return ret


class EntryResult():
    __slots__ = ['stdout', 'errno', 'stderr']

    def __init__(self, stdout='', errno=0, stderr=''):
        self.stdout = stdout
        self.errno = errno
        self.stderr = stderr


class ConShell():
    """ Send shell command to container via `docker.exec` and
    Receive stdout/stderr from commands.
    """

    def __init__(self, user='', logger=init_logger(__name__)):
        self.user = user
        # config logger was proccessed in global(`_init__.py`).
        # It's followed fuse.LogginMixIn style.
        self.logger = logger
        # Suppress debug output method when debug mode is disabled.
        from logging import DEBUG
        if self.logger.isEnabledFor(DEBUG) is False:
            self._debug_entry_command = lambda command: None
            self._debug_entry_ret = lambda ret: None

    # _init_require_cmds = tuple('pwd')
    _avail_cmds = {
        # setup cmds that initialize other cmds in advance
        # (extend this dict at `connect`).
        'which': {
            'path': '/bin/which',
        },
        'exec': {
            'path': 'exec'  # function
        },
        'exit': {
            'path': 'exit'  # function
        }
    }
    _support_shell = ({
        'shell_name': 'bash',
        'shell_path': '/bin/bash',
        'shell_args': '--noprofile --norc',
        'prefix_command': 'LC_ALL=C set -o pipefail;'
    }, {
        'shell_name': 'ash',
        'shell_path': '/bin/ash',
        'shell_args': '--noprofile --norc',
        'prefix_command': 'LC_ALL=C set -o pipefail;'
    })

    _shell_name = 'sh'  # basic shell(replace other shell at `connect`)
    _shell_path = '/bin/sh'
    _shell_args = ''
    _prefix_command = 'LC_ALL=C '

    sh_stream = None

    def _debug_entry_command(self, command):
        self.logger.debug('#entry => {command}'.format(command=command))

    def _debug_entry_ret(self, ret):
        self.logger.debug('#entry <= errno={ret.errno}'.format(ret=ret))
        self.logger.debug('#entry <= stdout={ret.stdout}'.format(ret=ret))
        self.logger.debug('#entry <= stderr={ret.stderr}'.format(ret=ret))

    def _entry_command(self, command):
        # write data to readonly stream force.
        # (type(self.sh_stream) = <class 'socket.SocketIO'>)
        os.write(self.sh_stream.fileno(),
                 bytearray(command, 'utf-8'))

    def _read_result(self):
        """Read result from stream that connected container.
        Returns:
            fd: pipe's file descriptor(stdout, stderr)?
            result: data readed from stream.
        """
        # Header??
        # byte 0  : [0x01 or 0x02] pipe's file descriptor(stdout, stderr)?
        # byte 1-3: [0x00, 0x00, 0x00]
        # byte 4-7: Length?
        fd = self.sh_stream.read(1)
        self.sh_stream.read(3)
        body_len = int.from_bytes(self.sh_stream.read(4), byteorder='big')

        # Body
        result = self.sh_stream.read(body_len)

        return fd, result

    def _which_cmd(self, cmd_name):
        ret = ''

        # res = self.entry(('which', '--', cmd_name))
        for path in ['/usr/sbin', '/usr/bin', '/sbin', '/bin']:
            full_path = os.path.join(path, cmd_name)
            res = self.entry((
                'ls', full_path
            ))
            if res.errno == 0 and res.stdout.split('\n', 1)[0] == full_path:
                ret = full_path
                break

        return ret

    def _get_shell_item(self):
        ret = None

        for item in self._support_shell:
            res = self._which_cmd(item['shell_name'])
            if res != '':
                item['shell_path'] = res
                ret = item
                break

        return ret

    def _open_stream(self):
        self.sh_stream = self.stream_exec(
            ' '.join((self._shell_path, self._shell_args)))

    def _switch_to_support_shell(self):
        item = self._get_shell_item()
        if item is not None:
            # close current stream
            self.entry(['exit'])
            # setup shell attributes
            self._shell_name = item['shell_name']
            self._shell_path = item['shell_path']
            self._shell_args = item['shell_args']
            self._prefix_command = item['prefix_command']
            # open stream in new attributes
            self._open_stream()
        else:
            raise RuntimeError('not installed support shell'
                               'in target container')

    def _setup_init_shell(self):
        self._open_stream()

    def setup_avail_cmds(self, require_cmds):
        for cmd_name in require_cmds:
            cmd_path = self._which_cmd(cmd_name)
            if cmd_path != '':
                self._avail_cmds[cmd_name] = {  # consider define class??
                    'path': cmd_path
                }
            else:
                raise RuntimeError(
                    'not found cmd full path: {0}'.format(cmd_name)
                )
        return self._avail_cmds

    def connect(self, container_name):
        client = docker.from_env()
        try:
            self.container = client.containers.get(container_name)

            # setup initial shell to search bash/ash erc.
            # (i.e. run `$ test -x '/bin/bash`)
            self._setup_init_shell()

            # switch shell that 'sh' to support shell(bash/ash) and
            # re connect stream.
            self._switch_to_support_shell()
        except docker.errors.NotFound as exc:
            raise exc

        # print(self.sh_stream.writable()) # False
        # print(self.sh_stream.isatty()) # False
        # print(self.sh_stream.seekable()) # False
        # print(type(self.sh_stream)) # <class 'socket.SocketIO'>

    def quote(self, command):
        return [shlex.quote(i) for i in command]

    def entry(self, command, quote=True, stdin_data=None, stdout_to_str=True,
              mixin_stderr_to_stdout=False,
              _disable_encode_stdoute_data=False):
        ret = EntryResult()

        #
        # Prepare commands bytes
        #
        if quote:
            c = ' '.join(self.quote(command))
        else:
            c = ' '.join(command)
        self._debug_entry_command(command)

        prefix_command = self._prefix_command
        if stdin_data:
            base64_data = str(base64.b64encode(stdin_data), 'utf-8')
            prefix_command = prefix_command + 'echo -n '\
                + shlex.quote(base64_data)  \
                + '|base64 -d|'
        append_command = '\n'
        if not _disable_encode_stdoute_data:
            append_command = ' |base64' + append_command
        if mixin_stderr_to_stdout:
            append_command = ' 2>&1' + append_command

        #
        # Entry commands
        #

        self._entry_command(prefix_command + c + append_command)

        # if stdin_data:
        #     #self.sh_stream.flush()
        #     time.sleep(1)
        #     c = os.write(self.sh_stream.fileno(), stdin_data)
        #     #print('data:' + str(c))

        # Entry separetor.
        self._entry_command('/bin/echo -en "\\n${?}\\0\\0\\0:"\n')

        #
        # Retreve results
        #
        out_data = {
            b'\x01': b'',
            b'\x02': b''
        }

        fd, data = self._read_result()
        out_data[fd] = data
        chk = 'loop'
        while chk == 'loop':
            if out_data[b'\x01'][-4:] == b'\0\0\0:':
                # Trim delimiter bytes
                out_data[b'\x01'] = out_data[b'\x01'][0:-4]
                chk = 'done'
            else:
                fd, data = self._read_result()
                out_data[fd] = out_data[fd] + data

        # Split result from stdout to bytes and error code(as string).
        (stdout_result, errno_result) = out_data[b'\x01'].rsplit(b'\n', 1)
        ret.errno = int(str(errno_result, 'utf-8'))
        if not _disable_encode_stdoute_data:
            stdout_result = base64.b64decode(stdout_result)
        else:
            stdout_result = stdout_result
        if stdout_to_str:
            try:
                ret.stdout = str(stdout_result, 'utf-8')
            except UnicodeDecodeError:
                # capture exception to revocer?
                raise
        else:
            ret.stdout = stdout_result
        if len(out_data[b'\x02']) > 0:
            try:
                ret.stderr = str(out_data[b'\x02'], 'utf-8')
            except UnicodeDecodeError:
                # capture exception to revocer?
                raise
        self._debug_entry_ret(ret)
        return ret

    def stream_exec(self, command):
        """Exec command and reserve stream to container.

        Note:
            Always use to exec shell(sh) for prepare `exec` method.

        Args:
            command: command to docker exec.

        Returns:
            Stream to shell in container.

        """
        return self.container.exec_run(
            command,
            user=self.user,
            stdin=True,
            socket=True
        )


if __name__ == '__main__':  # pragma: no cover.
    import sys
    shell = ConShell()
    shell.connect(sys.argv[1])
    ret = shell.entry(['ls', 'test10'])
    print('stdout: ' + ret.stdout)
    print('errnor:' + str(ret.errno))
    print('stderr: ' + ret.stderr)
