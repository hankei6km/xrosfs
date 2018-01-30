# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import datetime
import time
import pytest


class TestUtimens():

    test_file = ('utimens', 'test.txt')

    no_exist_file = ('utimens', 'no_exist_xrosfs.txt')

    def test_utimens(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_file)
        test_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_file)

        no_exist_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_file)

        # save content of test files
        with open(test_sshfs_path, 'r') as fd:
            save_content_sshfs = fd.read()
        with open(test_xrosfs_path, 'r') as fd:
            save_content_xrosfs = fd.read()

        # save content of test files
        stat_sshfs_info = os.stat(test_sshfs_path)
        stat_xrosfs_info = os.stat(test_xrosfs_path)

        # test to set timestamp
        atime = \
            time.mktime(
                datetime.datetime(2027, 11, 12, 13, 14, 15).timetuple()
            )
        mtime = \
            time.mktime(
                datetime.datetime(2027, 12, 17, 18, 19, 20).timetuple()
            )

        # set timestamp to test files
        os.utime(test_sshfs_path, (atime, mtime))
        os.utime(test_xrosfs_path, (atime, mtime))

        # check timestamp chenged from timestamp saved
        # atime not changed using touch of busybox.
        assert stat_sshfs_info.st_atime != os.stat(test_sshfs_path).st_atime
        assert stat_xrosfs_info.st_atime != os.stat(test_xrosfs_path).st_atime
        assert stat_sshfs_info.st_mtime != os.stat(test_sshfs_path).st_mtime
        assert stat_xrosfs_info.st_mtime != os.stat(test_xrosfs_path).st_mtime
        # chk_ns_atime = os.stat(test_sshfs_path).st_atime
        # chk_ns_mtime = os.stat(test_sshfs_path).st_mtime

        # check timestamp chenged
        # assertion atime can't pass test in alpine(based busy box).
        assert os.stat(test_sshfs_path).st_atime == \
            os.stat(test_xrosfs_path).st_atime
        assert os.stat(test_sshfs_path).st_mtime == \
            os.stat(test_xrosfs_path).st_mtime

        # test to set timestamp(ns)
        atime = \
            time.mktime(
                datetime.datetime(2027, 11, 12, 13, 14, 15, 99).timetuple()
            )
        mtime = \
            time.mktime(
                datetime.datetime(2027, 12, 17, 18, 19, 20, 99).timetuple()
            )

        # set timestamp(ns) to test files
        os.utime(test_sshfs_path, None, ns=(atime, mtime))
        os.utime(test_xrosfs_path, None, ns=(atime, mtime))

        # same results from sshfs and xrosfs.
        # but, st_atime and st_mtime == 1.0
        # not treat ns in fuse??
        assert os.stat(test_sshfs_path).st_atime == \
            os.stat(test_xrosfs_path).st_atime
        assert os.stat(test_sshfs_path).st_mtime == \
            os.stat(test_xrosfs_path).st_mtime
        # assert chk_ns_atime == os.stat(test_xrosfs_path).st_atime
        # assert chk_ns_mtime == os.stat(test_xrosfs_path).st_mtime

        # check not broken content of test files
        with open(test_sshfs_path, 'r') as fd:
            assert save_content_sshfs == fd.read()
        with open(test_xrosfs_path, 'r') as fd:
            assert save_content_xrosfs == fd.read()

        with pytest.raises(OSError) as excinfo:
            assert os.utime(no_exist_xrosfs_path) is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory'\
               in str(excinfo)
