# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import datetime


class CmdBuilder:
    def __init__(self):
        self.stat2json = '{' + ','.join([
            '"st_mode":"0x%f"',  # output hexadecimal number as string.
            '"st_ino":%i',
            '"st_dev":%d',
            '"st_nlink":%h',
            '"st_uid":%u',
            '"st_gid":%g',
            '"st_size":%s',
            '"st_atime":%X',
            '"st_mtime":%Y',
            '"st_ctime":%Z',
        ]) + '}'

        self.statfs2json = '{' + ','.join([
            '"f_bavail":%a',
            '"f_bfree":%f',
            '"f_blocks":%b',
            '"f_bsize":%s',
            '"f_favail":%d',  # can't get to non-superuser in `stat`.
            '"f_ffree":%d',
            '"f_files":%c',
            # '"f_flag":%?', https://docs.python.org/3/library/os.html
            '"f_frsize":%S',
            '"f_namemax":%l',
        ]) + '}'

        self.chmod_mask = 4095
        # 4959 ==
        # stat.S_ISUID | stat.S_ISGID | stat.S_ENFMT | stat.S_ISVTX |
        # stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC | stat.S_IRWXU |
        # stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRWXG |
        # stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IRWXO |
        # stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH

    require_cmds = (
        'pwd', 'ls', 'echo', 'stat', 'test', 'chmod', 'chown', 'readlink',
        'rm', 'rmdir', 'mkdir', 'ln', 'mv', 'touch', 'dd', 'truncate'
    )

    def set_avail_cmds(self, avail_cmds):
        self._avail_cmds = avail_cmds

    def _get_homedir(self):
        # This method does not use in fuse operation.
        # just use to get home dir of exec user
        # when not passed `server_path` from CLI args.
        return (
            self._avail_cmds['test']['path'],
            '-z',
            '"${HOME}"',
            '&&',
            self._avail_cmds['pwd']['path'],
            '||',
            self._avail_cmds['echo']['path'],
            '"${HOME}"'
        )

    def access(self, mode, full_path):
        return (self._avail_cmds['test']['path'], mode, full_path)

    def _chmod_octal_digit(self, mode):
        return '{0:04o}'.format(mode & self.chmod_mask)

    def chmod(self, mode, full_path=None):
        return (self._avail_cmds['chmod']['path'],
                self._chmod_octal_digit(mode),
                '--',
                full_path)

    def chown(self, uid, gid, full_path):
        arg = ''
        if uid != -1 and gid != -1:
            arg = str(uid) + ':' + str(gid)
        elif uid != -1 and gid == -1:
            arg = str(uid)
        elif uid == -1 and gid != -1:
            arg = ':' + str(gid)

        return (self._avail_cmds['chown']['path'], arg, '--', full_path)

    def getattr(self, full_path):
        return (
            self._avail_cmds['stat']['path'],
            '-c',
            self.stat2json,
            '--',
            full_path
        )

    def readdir(self, full_path):
        return (self._avail_cmds['ls']['path'], '-a1', '--', full_path)

    def readlink(self, full_path):
        return (self._avail_cmds['readlink']['path'], '-n', '--', full_path)

    def rmdir(self, full_path):
        # remove *empty* directories.
        return (self._avail_cmds['rmdir']['path'], '--', full_path)

    def mkdir(self, full_path):
        return (self._avail_cmds['mkdir']['path'], '--', full_path)

    def statfs(self, full_path):
        return (
            self._avail_cmds['stat']['path'],
            '-f', '-c', self.statfs2json, '--', full_path
        )

    def unlink(self, full_path):
        return (self._avail_cmds['rm']['path'], '--', full_path)

    def symlink(self, full_path_name, target):
        return (
            self._avail_cmds['ln']['path'],
            '-s',
            '--',
            target,
            full_path_name
        )

    def rename(self, full_path_old, full_path_new):
        return (
            self._avail_cmds['mv']['path'],
            '--',
            full_path_old,
            full_path_new
        )

    def link(self, full_path_name, full_path_target):
        return (
            self._avail_cmds['ln']['path'],
            '--',
            full_path_target, full_path_name
        )

    def utimens_update_to_now(self, full_path):
        return (
            self._avail_cmds['touch']['path'],
            '-c',
            '--',
            full_path
        )

    def utimens_update_atime(self, full_path, time):
        # TODO: detect acceptale args of touch in connected container and
        #       switch args to set timestamp.
        # '-a' flag not effect to touch of busybox.
        atime = datetime.datetime.fromtimestamp(time)
        tstr = atime.strftime('%Y%m%d%H%M.%S')
        return (self._avail_cmds['touch']['path'],
                '-c',
                '-a',
                '-t',
                tstr,
                '--',
                full_path)

    def utimens_update_mtime(self, full_path, time):
        # TODO: detect acceptale args of touch in connected container and
        #       switch args to set timestamp.
        # '-m' flag ignored to touch of busybox
        mtime = datetime.datetime.fromtimestamp(time)
        tstr = mtime.strftime('%Y%m%d%H%M.%S')
        return (self._avail_cmds['touch']['path'],
                '-c',
                '-m',
                '-t',
                tstr,
                '--',
                full_path)

    def open(self, fd, flags, full_path):
        flags = flags % 32768  # what mean is 32768(0x8000)?

        # TODO: Tranlate flags of os.open to operator strict.
        # It's not support `os.O_EXCL` etc yet.
        operator = '<'
        if os.O_RDONLY == flags:
            operator = '<'
        if os.O_WRONLY == flags:
            operator = '>'
        if os.O_CREAT == flags:
            operator = '>'
        if (os.O_WRONLY | os.O_TRUNC) == flags:
            operator = '>'
        if (os.O_WRONLY | os.O_APPEND) == flags:
            operator = '>>'
        if os.O_RDWR == flags:
            operator = '<>'
        if (os.O_RDWR | os.O_TRUNC) == flags:
            operator = '<>'
        if (os.O_RDWR | os.O_APPEND) == flags:
            operator = '<>>'

        return (
            self._avail_cmds['exec']['path'],
            str(fd) + operator,
            full_path
        )

    def create(self, full_path):
        return (self._avail_cmds['touch']['path'], '--', full_path)

    def read(self, length, offset, fh):

        return (self._avail_cmds['dd']['path'],
                'status=noxfer',  # busybox ver.
                # 'status=none',  # coreutil ver.
                'if=/dev/fd/' + str(fh),
                'bs=1',
                'count=' + str(length),
                'skip=' + str(offset))

    def write(self, length, offset, fh):
        return (self._avail_cmds['dd']['path'],
                'status=none',
                'of=/dev/fd/' + str(fh),
                'bs=1',
                'count=' + str(length),
                'seek=' + str(offset))

    def truncate(self, length, full_path):
        return (self._avail_cmds['truncate']['path'],
                '-s',
                str(length),
                '--',
                full_path)

    def flush(self, fh, full_path):
        # It is not confirmed whether `fsync` is actually called
        # return (['fsync', '--', full_path])
        return (self._avail_cmds['dd']['path'],
                'status=none',
                'of=' + full_path,
                'count=0',
                'conv=notrunc',
                'conv=fsync')

    def release(self, fh):
        return (self._avail_cmds['exec']['path'], str(fh) + '>&-')


if __name__ == '__main__':  # pragma: no cover.
    import shlex
    cmd_builder = CmdBuilder()
    c = ' '.join(
        [shlex.quote(i) for i in cmd_builder.getattr('/usr/bin/stat')])
    print(c)
