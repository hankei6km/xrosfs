# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import pytest
# import unittest
from unittest import mock
import os
import types
import datetime
import time

from xrosfs.xrosfs import XrosFS
from xrosfs.conshell import ConShell, EntryResult

# mock = unittest.mock
Mock = mock.Mock


class TestXroFS():
    def test_full_path(self):
        xrosfs = XrosFS(Mock(), Mock(), '/mnt')

        # Prepare function decorated
        @XrosFS.full_path()
        def f(self, path, arg1, arg2=None, full_path=''):
            m = Mock()
            m(full_path, arg1, arg2=arg2)
            return m

        # Test
        f(xrosfs, 'chk', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/chk', 'arg1_test', arg2='arg2_test')
        f(xrosfs, '/chk', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/chk', 'arg1_test', arg2='arg2_test')
        f(xrosfs, '//chk', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/chk', 'arg1_test', arg2='arg2_test')
        f(xrosfs, '/', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/', 'arg1_test', arg2='arg2_test')

    def test_directory_traversal(self):
        xrosfs = XrosFS(Mock(), Mock(), '/mnt')

        # Prepare function decorated
        @XrosFS.full_path()
        def f(self, path, full_path=''):
            m = Mock()
            m(full_path)
            return full_path

        # Test by various paths
        paths = [
            '../chk',
            '../../../../../../chk',
            '..//..//..//..//..//..//chk',
            'test/test/../../../chk',
            'test/../test/../test/../../chk',
            'test/./test/./test/../.././.././../chk',
            '/../../../../chk',
            '///../chk'
        ]
        for path in paths:
            with pytest.raises(PermissionError) as excinfo:
                assert os.path.normpath(f(xrosfs, path)) == ''
            assert 'Directory traversal deteceted, arg path=' + path\
                   in str(excinfo)

    def test_full_path_multiple_args(self):
        xrosfs = XrosFS(Mock(), Mock(), '/mnt')

        # Prepare function decorated
        @XrosFS.full_path(['old', 'new'])
        def f(self, old, new, arg1, arg2=None,
                full_path_old='',
                full_path_new=''):
            m = Mock()
            m(full_path_old, full_path_new, arg1, arg2=arg2)
            return m

        # Test
        f(xrosfs, 'chk_old', 'chk_new', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/chk_old', '/mnt/chk_new',
                                    'arg1_test', arg2='arg2_test')
        f(xrosfs, '/chk_old', '/chk_new', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/chk_old', '/mnt/chk_new',
                                    'arg1_test', arg2='arg2_test')
        f(xrosfs, '//chk_old', '//chk_new', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/chk_old', '/mnt/chk_new',
                                    'arg1_test', arg2='arg2_test')
        f(xrosfs, '/', 'new', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/', '/mnt/new',
                                    'arg1_test', arg2='arg2_test')
        f(xrosfs, 'old', '/', 'arg1_test', 'arg2_test').\
            assert_called_once_with('/mnt/old', '/mnt/',
                                    'arg1_test', arg2='arg2_test')

    def test_directory_traversal_multiple_args(self):
        xrosfs = XrosFS(Mock(), Mock(), '/mnt')

        # Prepare function decorated
        @XrosFS.full_path(['old', 'new'])
        def f(self, old, new, full_path_old='', full_path_new=''):
            m = Mock()
            m(full_path_old, full_path_new)
            return (full_path_old, full_path_new)

        # Test by various paths
        paths = [
            '../chk',
            '../../../../../../chk',
            '..//..//..//..//..//..//chk',
            'test/test/../../../chk',
            'test/../test/../test/../../chk',
            'test/./test/./test/../.././.././../chk',
            '/../../../../chk',
            '///../chk'
        ]

        # Test old
        for path in paths:
            with pytest.raises(PermissionError) as excinfo:
                assert os.path.normpath(f(xrosfs, path, 'new')) is ()
            assert 'Directory traversal deteceted, arg old=' + path\
                   in str(excinfo)

        # Test new
        for path in paths:
            with pytest.raises(PermissionError) as excinfo:
                assert os.path.normpath(f(xrosfs, 'old', path)) is ()
            assert 'Directory traversal deteceted, arg new=' + path\
                   in str(excinfo)

    def test_entry(self):
        xrosfs = XrosFS(Mock(), Mock(), '/mnt')

        # Prepare results(errno=0)
        res_normal_end = EntryResult('normal end', 0, '')
        xrosfs.shell.entry.return_value = res_normal_end
        command = ['test']

        # Test
        assert xrosfs._entry(command) is res_normal_end
        xrosfs.shell.entry.assert_called_once_with(command)

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Prepare results(errno=3, stderr='Permission denied')
        res_abnormal_end = EntryResult('', 3, 'abend')
        xrosfs.shell.entry.return_value = res_abnormal_end
        command = ['test']

        # Test
        assert xrosfs._entry(command, raise_unknow=False) is res_abnormal_end
        with pytest.raises(RuntimeError) as excinfo:
            assert xrosfs._entry(command) == ''
        assert 'cmd:test errno:3 stderr:abend' in str(excinfo)

    def test_get_homedir(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), Mock(), '/mnt')
        xrosfs.cmd_builder = cmdbuilder_mock_avail_cmds()

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult('/root\n')

        # Test
        assert xrosfs._get_homedir() == '/root'
        xrosfs.shell.entry.assert_called_once_with((
            '/usr/bin/test',
            '-z',
            '"${HOME}"',
            '&&',
            '/usr/bin/pwd',
            '||',
            '/bin/echo',
            '"${HOME}"'
        ), quote=False)

    def test_access(
            self,
            conshell_mock_methods,
            cmdbuilder_mock_avail_cmds):
        shell = Mock()
        shell.quote.side_effect = lambda c: ConShell.quote(shell, c)
        xrosfs = XrosFS(shell, cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.access('/path/to/test & test', os.W_OK) is None
        xrosfs.shell.entry.assert_called_once_with(
            (['/usr/bin/test', '-w', "'/mnt/path/to/test & test'"]),
            quote=False)

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test multpule mode bits
        assert xrosfs.access('/path/to/test & test',
                             os.W_OK | os.R_OK | os.X_OK) is None
        xrosfs.shell.entry.assert_called_once_with(
            ([
                '/usr/bin/test', '-x', "'/mnt/path/to/test & test'", '&&',
                '/usr/bin/test', '-w', "'/mnt/path/to/test & test'", '&&',
                '/usr/bin/test', '-r', "'/mnt/path/to/test & test'"
            ]),
            quote=False)

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test os.F_OK
        assert xrosfs.access('/path/to/test & test', os.F_OK) is None
        xrosfs.shell.entry.assert_called_once_with(
            (['/usr/bin/test', '-e', "'/mnt/path/to/test & test'"]),
            quote=False)

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Prepare
        xrosfs.shell.entry.return_value = EntryResult('', 1, '')

        # Test to can't access
        with pytest.raises(OSError) as excinfo:
            assert xrosfs.access('/path/to/test & test', os.F_OK) is None
        assert 'fuse.FuseOSError: [Errno 13] Permission denied'\
               in str(excinfo)

    def test_chmod(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.chmod('/path/to/test & test', 0x777) == 0
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/chmod', '3567', '--', '/mnt/path/to/test & test'))

    def test_chown(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.chown('/path/to/test & test', 1000, 2000) == 0
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/chown', '1000:2000', '--',
                '/mnt/path/to/test & test'))

    def test_getattr(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult(
            '{"st_mode":"0x81ed","st_ino":547312,"st_dev":46,'
            '"st_nlink":1,"st_uid":0,"st_gid":0,"st_size":76584,'
            '"st_atime":1502264616,"st_mtime":1426348024,'
            '"st_ctime":1501780227}')

        # Test
        assert xrosfs.getattr('/usr/bin/stat') ==\
            {"st_mode": 33261, "st_ino": 547312, "st_dev": 46,
             "st_nlink": 1, "st_uid": 0, "st_gid": 0, "st_size": 76584,
             "st_atime": 1502264616, "st_mtime": 1426348024,
             "st_ctime": 1501780227}
        xrosfs.shell.entry.assert_called_once_with(
            ('/usr/bin/stat', '-c', xrosfs.cmd_builder.stat2json, '--',
                '/mnt/usr/bin/stat'))

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Test not exist path
        xrosfs.shell.entry.return_value =\
            EntryResult('', 1, 'stat: cannot stat ‘/not_extist’:'
                        'No such file or directory\n')
        with pytest.raises(OSError) as excinfo:
            assert xrosfs.getattr('/usr/bin/stat') == ''
        assert 'fuse.FuseOSError: [Errno 2] No such file or directory'\
               in str(excinfo)

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Test json parse error
        xrosfs.shell.entry.return_value =\
            EntryResult('{')
        with pytest.raises(RuntimeError) as excinfo:
            assert xrosfs.getattr('/usr/bin/stat') == ''
        assert 'RuntimeError: stat:' in str(excinfo)

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Check recover from getattr failed
        xrosfs.shell.entry.side_effect = (
            EntryResult('', 1, ''),
            EntryResult(
                '{"st_mode":"0x81ed","st_ino":547312,"st_dev":46,'
                '"st_nlink":1,"st_uid":0,"st_gid":0,"st_size":76584,'
                '"st_atime":1502264616,"st_mtime":1426348024,'
                '"st_ctime":1501780227}')
        )
        assert xrosfs.getattr('/usr/bin/stat') ==\
            {"st_mode": 33261, "st_ino": 547312, "st_dev": 46,
             "st_nlink": 1, "st_uid": 0, "st_gid": 0, "st_size": 76584,
             "st_atime": 1502264616, "st_mtime": 1426348024,
             "st_ctime": 1501780227}
        assert xrosfs.shell.entry.call_count == 2

        # Reset mock
        xrosfs.shell.entry.reset_mock()
        xrosfs.shell.entry.side_effect = \
            [EntryResult('', 1, '') for i in range(1, 20)]

        # Check fatal error
        xrosfs.shell.entry.return_value = EntryResult('', 1, ''),
        with pytest.raises(RuntimeError) as excinfo:
            assert xrosfs.getattr('/usr/bin/stat') == ''
        assert 'RuntimeError: Fatale error getattr failed 10 times' in \
            str(excinfo)
        assert xrosfs.shell.entry.call_count == 10

        # Reset mock
        xrosfs.shell.entry.reset_mock()
        xrosfs.shell.entry.side_effect = None

        # Check to raise unknown
        xrosfs.shell.entry.side_effect = [EntryResult('', 1, 'check')]

        with pytest.raises(RuntimeError) as excinfo:
            assert xrosfs.getattr('/usr/bin/stat') == ''
        assert 'RuntimeError: cmd' in str(excinfo)

    def test_readdir(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        files = ['foo', 'bar']
        xrosfs.shell.entry.return_value = EntryResult('\n'.join(files) + '\n')

        # Test
        ls = xrosfs.readdir('/chk', None)
        assert isinstance(ls, types.GeneratorType)
        assert [i for i in ls] == files
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/ls', '-a1', '--', '/mnt/chk'))

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Test not exist path
        xrosfs.shell.entry.return_value =\
            EntryResult('', 2, 'ls: cannot access \'/not_exist\':'
                        'No such file or directory\n')
        xrosfs.readdir('/not_exist', None)
        with pytest.raises(OSError) as excinfo:
            ls = xrosfs.readdir('/not_exist', None)
            # Run code that before first `yield` in generator function
            assert next(ls) == ''
        assert 'fuse.FuseOSError: [Errno 2] No such file or directory'\
               in str(excinfo)

    def test_readlink(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult('../link/file.txt')

        # Test
        assert xrosfs.readlink('/path/to/test & test') == '../link/file.txt'
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/readlink', '-n', '--', '/mnt/path/to/test & test'))

    def test_rmdir(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.rmdir('/path/to/test & test') == 0
        xrosfs.shell.entry.assert_called_once_with(
            ('/usr/bin/rmdir', '--', '/mnt/path/to/test & test'))

        # Prepare rm not empty directory dummy results
        xrosfs.shell.entry.return_value = \
            EntryResult(
                '', 1, 'rm: cannot remove \'test1\': Directory not empty')

        # Test
        with pytest.raises(OSError) as excinfo:
            assert xrosfs.rmdir('test1') == 0
        assert 'fuse.FuseOSError: [Errno 39] Directory not empty'\
               in str(excinfo)

    def test_mkdir(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.mkdir('/path/to/test & test', 0o022) == 0
        calls = [
            mock.call(('/usr/bin/mkdir', '--', '/mnt/path/to/test & test')),
            mock.call(('/bin/chmod', '0022', '--', '/mnt/path/to/test & test'))
        ]
        xrosfs.shell.entry.assert_has_calls(calls)

        # Prepare mkdir to exist directory dummy results
        xrosfs.shell.entry.return_value = \
            EntryResult(
                '', 1, 'mkdir: cannot create directory \'test1\': File exists')

        # Test
        with pytest.raises(OSError) as excinfo:
            assert xrosfs.mkdir('test1', 0o022) == 0
        assert 'fuse.FuseOSError: [Errno 17] File exists'\
               in str(excinfo)

    def test_statfs(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.side_effect = [
            EntryResult(
                '{"f_bavail": 1, "f_bfree": 2, "f_blocks": 3,'
                '"f_bsize": 4, "f_favail": 5, "f_ffree": 6,'
                '"f_files": 7, "f_frsize": 8, "f_namemax": 9}\n'
            ),
            EntryResult(
                'overlay / overlay rw,relatime,lowerdir=/var/... 0 0\n'
                'proc /proc proc ... 0 0\n'
                'tmpfs /dev tmpfs ... 0 0\n'
            )
        ]

        # Test
        assert xrosfs.statfs('/home/pdu/xrosfs/bench_test/mnt/xrosfs') == \
            {"f_bavail": 1, "f_bfree": 2, "f_blocks": 3,
             "f_bsize": 4, "f_favail": 5, "f_ffree": 6,
             "f_files": 7, "f_frsize": 8, "f_namemax": 9,
             "f_flag": 32 | os.ST_RELATIME}
        calls = [
            mock.call(('/usr/bin/stat',
                       '-f',
                       '-c',
                       '{"f_bavail":%a,"f_bfree":%f,"f_blocks":%b,'
                       '"f_bsize":%s,"f_favail":%d,"f_ffree":%d,'
                       '"f_files":%c,"f_frsize":%S,"f_namemax":%l}',
                       '--',
                       '/mnt/home/pdu/xrosfs/bench_test/mnt/xrosfs')),
            mock.call(['cat', '/proc/mounts'])
        ]
        xrosfs.shell.entry.assert_has_calls(calls)

        # Reset mock
        xrosfs.shell.entry.side_effect = None
        xrosfs.shell.entry.reset_mock()

        # Test not exist path
        xrosfs.shell.entry.return_value =\
            EntryResult('', 1, 'stat: cannot stat ‘/not_extist’:'
                        'No such file or directory\n')
        with pytest.raises(OSError) as excinfo:
            assert xrosfs.statfs('/home/pdu/xrosfs/bench_test/mnt/xrosfs') == \
                ''
        assert 'fuse.FuseOSError: [Errno 2] No such file or directory'\
               in str(excinfo)

        # Reset mock
        xrosfs.shell.entry.reset_mock()

        # Test json parse error
        xrosfs.shell.entry.return_value =\
            EntryResult('{')
        with pytest.raises(RuntimeError) as excinfo:
            assert xrosfs.getattr('/usr/bin/stat') == ''
        assert 'RuntimeError: stat:' in str(excinfo)

    def test_unlink(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.unlink('/path/to/test & test') is None
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/rm', '--', '/mnt/path/to/test & test'))

    def test_symlink(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult('', 0)

        # Test
        assert xrosfs.symlink(
            '/path/to/test & test/name',
            'test & test/target'
        ) == 0
        xrosfs.shell.entry.assert_called_once_with(
            ('/usr/bin/ln', '-s', '--',
             'test & test/target',
             '/mnt/path/to/test & test/name'))

    def test_rename(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult('', 0)

        # Test
        assert xrosfs.rename(
            '/path/to/test & test/old',
            '/path/to/test & test/new'
        ) == 0
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/mv', '--',
             '/mnt/path/to/test & test/old',
             '/mnt/path/to/test & test/new'))

    def test_link(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult('', 0)

        # Test
        assert xrosfs.link(
            '/path/to/test & test/name',
            '/path/to/test & test/target'
        ) == 0
        xrosfs.shell.entry.assert_called_once_with(
            ('/usr/bin/ln', '--',
             '/mnt/path/to/test & test/target',
             '/mnt/path/to/test & test/name'))

    def test_utimens(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult('', 0)

        # Test
        assert xrosfs.utimens('/path/to/test & test', None) is None
        xrosfs.shell.entry.assert_called_once_with(
            ('/usr/bin/touch', '-c', '--',
             '/mnt/path/to/test & test'))

        xrosfs.shell.entry.reset_mock()

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult('', 0)

        atime = \
            time.mktime(datetime.datetime(2017, 1, 2, 3, 4, 5).timetuple())
        mtime = \
            time.mktime(datetime.datetime(2017, 6, 7, 8, 9, 10).timetuple())
        assert xrosfs.utimens(
            '/path/to/test & test',
            (atime, mtime)
        ) is None
        calls = [
            mock.call((
                '/usr/bin/touch',
                '-c',
                '-a',
                '-t',
                '201701020304.05',
                '--',
                '/mnt/path/to/test & test')),
            mock.call((
                '/usr/bin/touch',
                '-c',
                '-m',
                '-t',
                '201706070809.10',
                '--',
                '/mnt/path/to/test & test')),
        ]
        xrosfs.shell.entry.assert_has_calls(calls)

    def test_read_dev_fd(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        files = ['0', '1',
                 '20', '21', '23', '25', '20', '21', '23', '25',
                 '2', '3']
        xrosfs.shell.entry.return_value = EntryResult('\n'.join(files) + '\n')

        # Test
        assert xrosfs._read_dev_fd() == files
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/ls', '-a1', '--', '/dev/fd/'))

    def test_open(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results from `/dev/fd/` (next availabe fd is 22)
        xrosfs._read_dev_fd = Mock(return_value=['0', '1',
                                                 '20', '21', '23', '25',
                                                 '2', '3'])
        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.open('/path/to/test & test', os.O_RDONLY) == 22
        xrosfs.shell.entry.assert_called_once_with(
            ('exec', '22<', "'/mnt/path/to/test & test'"),
            _disable_encode_stdoute_data=True, quote=False)

    def test_create(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()
        xrosfs.chmod = Mock()
        xrosfs.open = Mock(return_value=20)

        # Test
        assert xrosfs.create('/path/to/test & test', 0x777, fi=None) == 20
        xrosfs.shell.entry.assert_called_once_with(
            ('/usr/bin/touch', '--', '/mnt/path/to/test & test'))
        xrosfs.chmod.assert_called_once_with(
            '/path/to/test & test', 0x777)
        xrosfs.open.assert_called_once_with(
            '/path/to/test & test', os.O_WRONLY | os.O_CREAT)

    def test_read(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult('bar')

        # Test
        assert xrosfs.read('/path/to/test & test', 4096, 1, 22) == 'bar'
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/dd',
             'status=noxfer',  # busybox ver.
             # 'status=none',  # coreutil ver.
             'if=/dev/fd/22',
             'bs=1',
             'count=4096',
             'skip=1'),
            stdout_to_str=False)

    def test_write(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.write('/path/to/test & test', 'bar', 1, 22) == 3
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/dd',
             'status=none',
             'of=/dev/fd/22',
             'bs=1',
             'count=3',
             'seek=1'),
            stdin_data='bar')

    def test_truncate(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.truncate('/path/to/test & test', 10) is None
        xrosfs.shell.entry.assert_called_once_with(
            ('/usr/bin/truncate', '-s', '10', '--',
             '/mnt/path/to/test & test'))

    def test_flush(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.flush('/path/to/test & test', 10) is 0
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/dd',
             'status=none',
             'of=' + '/mnt/path/to/test & test',
             'count=0',
             'conv=notrunc',
             'conv=fsync'))

    def test_close(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.release('/path/to/test & test', 22) is None
        xrosfs.shell.entry.assert_called_once_with(
            ('exec', '22>&-'),
            _disable_encode_stdoute_data=True, quote=False)

    def test_fsync(
            self,
            cmdbuilder_mock_avail_cmds):
        xrosfs = XrosFS(Mock(), cmdbuilder_mock_avail_cmds(), '/mnt')

        # Prepare dummy results
        xrosfs.shell.entry.return_value = EntryResult()

        # Test
        assert xrosfs.fsync('/path/to/test & test', None, 10) is 0
        xrosfs.shell.entry.assert_called_once_with(
            ('/bin/dd',
             'status=none',
             'of=' + '/mnt/path/to/test & test',
             'count=0',
             'conv=notrunc',
             'conv=fsync'))
