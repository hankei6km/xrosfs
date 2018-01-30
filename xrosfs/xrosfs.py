# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import sys
import shlex
import re
import json
import errno
import inspect
from operator import itemgetter
from functools import wraps

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from pathlib import Path


class XrosFS(LoggingMixIn, Operations):
    def __init__(self, shell, cmd_builder, root):
        self.shell = shell
        self.cmd_builder = cmd_builder
        self.root = os.path.normpath(root)

    opts2statvfs_flag = {
        'append': os.ST_APPEND,
        'nodev': os.ST_NODEV,
        'nosuid': os.ST_NOSUID,
        'synchronous': os.ST_SYNCHRONOUS,
        'mandlock': os.ST_MANDLOCK,
        'nodiratime': os.ST_NODIRATIME,
        'rdonly': os.ST_RDONLY,
        'write': os.ST_WRITE,
        'noatime': os.ST_NOATIME,
        'noexec': os.ST_NOEXEC,
        'relatime': os.ST_RELATIME,
        'rw': 32  # os.ST_???
    }

    errno_mapper = {
        '': [(
            re.compile('Permission denied$'), 1
        ), (
            re.compile(': File exists$'), 17
        ), (
            re.compile(': Directory not empty$'), 39
        ), (
            re.compile('No such file or directory$'), 2
        )],
        'fsync': [(
            re.compile(': File exists$'), 17
        ), (
            re.compile(': Directory not empty$'), 39
        ), (
            re.compile('No such file or directory$'), 2
        )]
    }

    def _is_directory_traversal(self, path, full_path):
        """ Detect directory traversal.
        """
        norm_path = os.path.normpath(full_path)
        root = os.path.commonpath([self.root, norm_path])
        return root != self.root

    def _full_path(self, path):
        if os.path.isabs(path):
            p = Path(path)
            if p.root != path:  # confirmed that path is abs.
                path = path[len(p.root):]
            else:
                path = ''
        return os.path.join(self.root, path)

    def full_path(p=['path']):
        def full_path_inner(f):
            # https://stackoverflow.com/questions/218616/getting-method-parameter-names-in-python
            path_args_list = []
            spec_args = inspect.getargspec(f).args
            for i in p:
                # Build prefix of full_path arg name.
                # `path` -> `full_path`
                # `foo` -> `full_path_foo'
                # `bar` -> `full_path_bar'
                full_path_arg_prefix = \
                    'full_' if i == 'path' else 'full_path_'
                # Pickup target args that passed name of args stored path.
                # It is support only positional argument yet.
                path_args_list.append((
                    i,
                    full_path_arg_prefix + i,
                    spec_args.index(i)))

            @wraps(f)
            def ret(self, *args, **kwargs):
                # Add full_path into kwargs.
                for arg_name, arg_full_path_name, arg_idx in path_args_list:
                    # Shift position of idx by considering `self` arg.
                    path = args[arg_idx - 1]
                    full_path = self._full_path(path)
                    if self._is_directory_traversal(path, full_path):
                        raise PermissionError(
                            'Directory traversal deteceted, '
                            'arg ' + arg_name + '=' + path)
                    kwargs[arg_full_path_name] = full_path
                return f(self, *args, **kwargs)

            return ret
        return full_path_inner

    def _raise_unknown(self, command, res):
        raise RuntimeError('cmd:{0} errno:{1} stderr:{2}'.format(
            command[0], res.errno, res.stderr))

    def _entry(self,
               command, errno_map='', raise_unknow=True, *args, **kwargs):
        res = self.shell.entry(command, *args, **kwargs)
        if res.errno != 0:
            for r, fuse_errno in self.errno_mapper[errno_map]:
                if r.search(res.stderr, 0) is not None:
                    raise FuseOSError(fuse_errno)
            if raise_unknow:
                self._raise_unknown(command, res)

        return res

    def _get_homedir(self):
        res = self._entry(self.cmd_builder._get_homedir(), quote=False)
        return res.stdout.split('\n', 1)[0]

    @full_path()
    def access(self, path, mode, full_path=None):
        # Map mode bit to each `test` command
        mode_test = [{
            'mode': os.X_OK,
            'test': ['-x', full_path]
        }, {
            'mode': os.W_OK,
            'test': ['-w', full_path]
        }, {
            'mode': os.R_OK,
            'test': ['-r', full_path]
        }]
        # Append `test` command to list by mode
        test_commands = []
        if mode == os.F_OK:
            test_commands = [self.cmd_builder.access('-e', full_path)]
        else:
            for m in mode_test:
                if mode & m['mode'] == m['mode']:
                    test_commands.append(self.cmd_builder.access(*m['test']))

        # Build command list from `test` commands list
        command = []
        for c in test_commands:
            for i in self.shell.quote(c):
                command.append(i)
            command.append('&&')
        if len(command) > 0:
            res = self._entry(command[:-1], quote=False, raise_unknow=False)
            if res.errno != 0:
                raise FuseOSError(errno.EACCES)
        # else:
        #     raise RuntimeError('Can\'t parse mode:' + mode)

    @full_path()
    def chmod(self, path, mode, full_path=None):
        res = self._entry(self.cmd_builder.chmod(mode, full_path))
        return res.errno

    @full_path()
    def chown(self, path, uid, gid, full_path=None):
        res = self._entry(self.cmd_builder.chown(uid, gid, full_path))
        return res.errno

    @full_path()
    def getattr(self, path, fh=None, full_path=None):
        command = self.cmd_builder.getattr(full_path)
        res = self._entry(
            command, raise_unknow=False
        )
        # TODO: remove bellow code that recover from getatter failed.
        # what reason to occurs stdout and stderr is balnk with errno ==1.
        # why??
        cnt = 1
        while res.stdout == '' and res.errno == 1 and res.stderr == '':
            # print('*************** retry getattr')
            res = self._entry(
                command, raise_unknow=False
            )
            cnt = cnt + 1
            if cnt > 9:
                raise RuntimeError('Fatale error getattr failed 10 times')
        if res.errno != 0:
            self._raise_unknown(command, res)

        try:
            st = json.loads(res.stdout)
            # hexadecimal string to integer.
            # (json not support hexadecimal literal).
            st['st_mode'] = int(st['st_mode'], 16)
        except json.JSONDecodeError as e:
            raise RuntimeError('stat: ' + full_path) from e

        return st

    @full_path()
    def readdir(self, path, fh, full_path=None):
        # TODO: Support parse filename that contains '\n'.
        # And test another control chars (i.e. '\0' etc.).
        res = self._entry(self.cmd_builder.readdir(full_path))
        dirents = re.sub(r'\n$', '', res.stdout).split('\n')
        for r in dirents:
            yield r

    @full_path()
    def readlink(self, path, full_path):
        res = self._entry(self.cmd_builder.readlink(full_path))
        ret = res.stdout
        # TODO: Enable bellow snitaize code and check direcotry traversal.
        # if os.path.isabs(ret):
        #     # Path name is absolute, sanitize it.
        #     ret = os.path.relpath(ret, self.root)
        return ret

    @full_path()
    def rmdir(self, path, full_path):
        res = self._entry(self.cmd_builder.rmdir(full_path))
        return res.errno

    @full_path()
    def mkdir(self, path, mode, full_path):
        res = self._entry(self.cmd_builder.mkdir(full_path))
        errno = res.errno
        if res.errno == 0:
            errno = self.chmod(path, mode)
        return errno

    @full_path()
    def statfs(self, path, full_path):
        res = self._entry(self.cmd_builder.statfs(full_path))
        if res.errno != 0:
            # not found ??
            raise FuseOSError(errno.ENOENT)
        # try:
        #     st = json.loads(res.stdout)
        # except json.JSONDecodeError:
        #     raise FuseOSError(errno.ENOENT)
        st = json.loads(res.stdout)

        # retrive mount flag
        # (form remote is right?)
        mounts = self._entry(['cat', '/proc/mounts']).stdout
        li = sorted([
            itemgetter(1, 3)(i.split(' '))
            for i in mounts.split('\n')
            if len(i) > 0 and full_path.startswith(i.split(' ', 2)[1])
        ], key=itemgetter(0), reverse=True)

        flag = 0
        for opt in li[0][1].split(','):
            if opt in self.opts2statvfs_flag:
                flag = flag + self.opts2statvfs_flag[opt]
                st['f_flag'] = flag

        return st

    @full_path()
    def unlink(self, path, full_path):
        self._entry(self.cmd_builder.unlink(full_path))

    @full_path(['name', 'target'])
    def symlink(self, name, target, full_path_name, full_path_target):
        res = self._entry(self.cmd_builder.symlink(
            full_path_name,
            target
        ))
        return res.errno

    @full_path(['old', 'new'])
    def rename(self, old, new, full_path_old, full_path_new):
        res = self._entry(self.cmd_builder.rename(
            full_path_old, full_path_new))
        return res.errno

    @full_path(['name', 'target'])
    def link(self, name, target, full_path_name, full_path_target):
        res = self._entry(self.cmd_builder.link(
            full_path_name,
            full_path_target
        ))
        return res.errno

    @full_path()
    def utimens(self, path, times=None, full_path=None):
        if times is None:
            # set current time to full_path
            self._entry(self.cmd_builder.utimens_update_to_now(full_path))
        else:
            self._entry(
                self.cmd_builder.utimens_update_atime(
                    full_path, times[0]
                )
            )
            self._entry(
                self.cmd_builder.utimens_update_mtime(
                    full_path, times[1]
                )
            )

    def _read_dev_fd(self):
        """ only use to read `/dev/fd/`
        """
        res = self._entry(self.cmd_builder.readdir('/dev/fd/'))
        return re.sub(r'\n$', '', res.stdout).split('\n')

    @full_path()
    def open(self, path, flags, full_path):
        # Get available fd value by status of containers's '/dev/fd/'
        fd_set = set(fd for fd in self._read_dev_fd())
        fg = (i for i in range(20, 30) if not str(i) in fd_set)
        # TODO: Check no available fd then raise FuseOSError
        fd = next(fg)
        self._entry(self.cmd_builder.open(
                    fd, flags, shlex.quote(full_path)
                    ), quote=False, _disable_encode_stdoute_data=True)

        return fd

    @full_path()
    def create(self, path, mode, fi=None, full_path=None):
        self._entry(self.cmd_builder.create(full_path))
        self.chmod(path, mode)
        return self.open(path, os.O_WRONLY | os.O_CREAT)

    def read(self, path, length, offset, fh):
        # Always use fh
        res = self._entry(self.cmd_builder.read(
            length, offset, fh
        ), stdout_to_str=False)
        return res.stdout

    def write(self, path, buf, offset, fh):
        # Always use fh
        length = len(buf)
        self._entry(self.cmd_builder.write(
            length, offset, fh
        ), stdin_data=buf)
        return length

    @full_path()
    def truncate(self, path, length, fh=None, full_path=None):
        self._entry(self.cmd_builder.truncate(length, full_path))

    @full_path()
    def flush(self, path, fh, full_path=None):
        res = self._entry(
            self.cmd_builder.flush(fh, full_path),
            errno_map='fsync',
            raise_unknow=False
        )
        ret = res.errno if res.errno != 1 else 0
        return ret

    def release(self, path, fh):
        # Always use fh
        self._entry(self.cmd_builder.release(fh),
                    quote=False, _disable_encode_stdoute_data=True)
        return None

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


if __name__ == '__main__':
    FUSE(XrosFS(sys.argv[1], sys.argv[2]),
         sys.argv[3], nothreads=True, foreground=True)
