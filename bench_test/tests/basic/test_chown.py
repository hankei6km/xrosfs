# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestChown():

    test_file = ('chown', 'test.txt')
    no_exist_xrosfs_file = ('chown', 'no_exist.txt')

    def test_chown(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_file)
        test_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_file)
        no_exist_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_xrosfs_file)

        stat_sshfs_info = os.stat(test_file_sshfs_path)
        stat_xrosfs_info = os.stat(test_file_xrosfs_path)
        assert stat_sshfs_info.st_uid == stat_xrosfs_info.st_uid
        assert stat_sshfs_info.st_gid == stat_xrosfs_info.st_gid
        assert stat_xrosfs_info.st_uid == 1000
        assert stat_xrosfs_info.st_gid == 100

        # Mount exported direcotry as root user,
        # chown operation granted on mounted directory.
        # TODO: Check permission error with normal user.
        assert os.chown(test_file_sshfs_path, 65534, 1001) is None
        assert os.chown(test_file_xrosfs_path, 65534, 1001) is None

        stat_sshfs_info = os.stat(test_file_sshfs_path)
        stat_xrosfs_info = os.stat(test_file_xrosfs_path)
        assert stat_sshfs_info.st_uid == stat_xrosfs_info.st_uid
        assert stat_sshfs_info.st_gid == stat_xrosfs_info.st_gid
        assert stat_xrosfs_info.st_uid == 65534
        assert stat_xrosfs_info.st_gid == 1001

        with pytest.raises(OSError) as excinfo:
            assert os.chown(no_exist_file_xrosfs_path, 1000, 1001) is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
