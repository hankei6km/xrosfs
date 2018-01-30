# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestGetattr():

    test_file = ('getattr', 'test.txt')
    no_exist_file = ('getattr', 'no_exist.txt')
    keys = ('st_mode',
            # 'st_ino',
            # 'st_dev',
            'st_nlink',
            'st_uid',
            'st_gid',
            'st_size',
            # 'st_atime',
            # 'st_mtime',
            # 'st_ctime'
            )

    def test_getattr(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_file_sshfs_path = os.path.join(mnt_sshfs_path, *self.test_file)
        test_file_xrosfs_path = os.path.join(mnt_xrosfs_path, *self.test_file)

        no_exist_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_file)

        stat_sshfs_info = os.stat(test_file_sshfs_path)
        stat_sshfs_dict = {
            key: getattr(stat_sshfs_info, key) for key in self.keys
        }
        stat_xrosfs_info = os.stat(test_file_xrosfs_path)
        stat_xrosfs_dict = {
            key: getattr(stat_xrosfs_info, key) for key in self.keys
        }
        assert stat_xrosfs_info.st_atime != 0
        assert stat_xrosfs_info.st_mtime != 0
        assert stat_xrosfs_info.st_ctime != 0
        assert stat_sshfs_dict == stat_xrosfs_dict
        assert isinstance(stat_xrosfs_info, os.stat_result)

        with pytest.raises(OSError) as excinfo:
            assert os.stat(no_exist_file_xrosfs_path)
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
