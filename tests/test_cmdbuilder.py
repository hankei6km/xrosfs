# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

# import pytest
# import unittest
# from unittest import mock
import os
import datetime
import time

from xrosfs.cmdbuilder import CmdBuilder

# mock = unittest.mock
# Mock = mock.Mock


class TestCmdBuilder():
    full_path = '/path/to'
    full_path_name = '/path/to_name'
    full_path_target = '/path/to_target'
    target = 'to_target'
    full_path_old = '/path/to_old'
    full_path_new = '/path/to_new'
    fd = 22

    def test_set_avail_cmds(self):
        cmd_builder = CmdBuilder()
        cmd_builder.set_avail_cmds({
            'test': {
                'path': '/usr/bin/test'
            }
        })

        assert cmd_builder.access('-x', self.full_path) ==\
            (('/usr/bin/test', '-x', self.full_path))

    def test_get_homedir(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = cmdbuilder_mock_avail_cmds()

        assert cmd_builder._get_homedir() == ((
            '/usr/bin/test',
            '-z',
            '"${HOME}"',
            '&&',
            '/usr/bin/pwd',
            '||',
            '/bin/echo',
            '"${HOME}"'
        ))

    def test_access(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = cmdbuilder_mock_avail_cmds()

        assert cmd_builder.access('-x', self.full_path) ==\
            (('/usr/bin/test', '-x', self.full_path))

    def test_chmod(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = cmdbuilder_mock_avail_cmds()

        assert cmd_builder.chmod(0x777, self.full_path) ==\
            (('/bin/chmod', '3567', '--', self.full_path))

    def test_chown(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.chown(1000, 2000, self.full_path) ==\
            (('/bin/chown', '1000:2000', '--', self.full_path))
        assert cmd_builder.chown(1000, -1, self.full_path) ==\
            (('/bin/chown', '1000', '--', self.full_path))
        assert cmd_builder.chown(-1, 2000, self.full_path) ==\
            (('/bin/chown', ':2000', '--', self.full_path))
        # Does pass '-1:-1' from api/cmd ?
        assert cmd_builder.chown(-1, -1, self.full_path) ==\
            (('/bin/chown', '', '--', self.full_path))

    def test_getattr(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.getattr(self.full_path) ==\
            (('/usr/bin/stat', '-c', cmd_builder.stat2json,
                '--', self.full_path))

    def test_readdir(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.readdir(self.full_path) ==\
            (('/bin/ls', '-a1', '--', self.full_path))

    def test_readlink(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.readlink(self.full_path) ==\
            (('/bin/readlink', '-n', '--', self.full_path))

    def test_rmdir(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.rmdir(self.full_path) ==\
            (('/usr/bin/rmdir', '--', self.full_path))

    def test_mkdir(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.mkdir(self.full_path) ==\
            (('/usr/bin/mkdir', '--', self.full_path))

    def test_statfs(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.statfs(self.full_path) ==\
            (('/usr/bin/stat', '-f', '-c', cmd_builder.statfs2json,
                '--', self.full_path))

    def test_unlink(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.unlink(self.full_path) ==\
            (('/bin/rm', '--', self.full_path))

    def test_symlink(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.symlink(
            self.full_path_name,
            self.target
        ) == ((
            '/usr/bin/ln',
            '-s',
            '--',
            self.target, self.full_path_name
        ))

    def test_rename(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.rename(self.full_path_old, self.full_path_new) ==\
            (('/bin/mv', '--', self.full_path_old, self.full_path_new))

    def test_link(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.link(
            self.full_path_name,
            self.full_path_target
        ) == ((
            '/usr/bin/ln',
            '--',
            self.full_path_target, self.full_path_name
        ))

    def test_utimens(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.utimens_update_to_now(
            self.full_path
        ) == ((
            '/usr/bin/touch',
            '-c',
            '--',
            self.full_path
        ))

        atime = \
            time.mktime(datetime.datetime(2017, 1, 2, 3, 4, 5).timetuple())
        assert cmd_builder.utimens_update_atime(
            self.full_path,
            atime
        ) == ((
            '/usr/bin/touch',
            '-c',
            '-a',
            '-t',
            '201701020304.05',
            '--',
            self.full_path
        ))

        mtime = \
            time.mktime(datetime.datetime(2017, 6, 7, 8, 9, 10).timetuple())
        assert cmd_builder.utimens_update_mtime(
            self.full_path,
            mtime
        ) == ((
            '/usr/bin/touch',
            '-c',
            '-m',
            '-t',
            '201706070809.10',
            '--',
            self.full_path
        ))

    def test_open(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.open(self.fd, os.O_RDONLY, self.full_path) ==\
            (('exec', str(self.fd) + '<', self.full_path))
        assert cmd_builder.open(self.fd, os.O_WRONLY, self.full_path) ==\
            (('exec', str(self.fd) + '>', self.full_path))
        assert cmd_builder.open(self.fd, os.O_CREAT, self.full_path) ==\
            (('exec', str(self.fd) + '>', self.full_path))
        assert cmd_builder.open(self.fd,
                                (os.O_WRONLY | os.O_TRUNC),
                                self.full_path) ==\
            (('exec', str(self.fd) + '>', self.full_path))
        assert cmd_builder.open(self.fd,
                                (os.O_WRONLY | os.O_APPEND),
                                self.full_path) ==\
            (('exec', str(self.fd) + '>>', self.full_path))
        assert cmd_builder.open(self.fd, os.O_RDWR, self.full_path) ==\
            (('exec', str(self.fd) + '<>', self.full_path))
        assert cmd_builder.open(self.fd,
                                (os.O_RDWR | os.O_TRUNC),
                                self.full_path) ==\
            (('exec', str(self.fd) + '<>', self.full_path))
        assert cmd_builder.open(self.fd,
                                (os.O_RDWR | os.O_APPEND),
                                self.full_path) ==\
            (('exec', str(self.fd) + '<>>', self.full_path))

    def test_create(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.create(self.full_path) ==\
            (('/usr/bin/touch', '--', self.full_path))

    def test_read(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.read(4096, 1, self.fd) ==\
            (('/bin/dd',
              'status=noxfer',  # busybox ver.
              # 'status=none',  # coreutil ver.
              'if=/dev/fd/' + str(self.fd),
              'bs=1',
              'count=' + str(4096),
              'skip=' + str(1)))

    def test_write(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.write(4096, 1, self.fd) ==\
            (('/bin/dd',
              'status=none',  # coreutil ver.
              'of=/dev/fd/' + str(self.fd),
              'bs=1',
              'count=' + str(4096),
              'seek=' + str(1)))

    def test_truncate(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.truncate(10, self.full_path) ==\
            (('/usr/bin/truncate',
              '-s',
              '10',
              '--',
              self.full_path))

    def test_flush(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.flush(10, self.full_path) ==\
            (('/bin/dd',
              'status=none',
              'of=' + self.full_path,
              'count=0',
              'conv=notrunc',
              'conv=fsync'))

    def test_release(self, cmdbuilder_mock_avail_cmds):
        cmd_builder = CmdBuilder()

        assert cmd_builder.release(self.fd) ==\
            (('exec', str(self.fd) + '>&-'))
