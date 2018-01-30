# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestMkdir():

    test_dir = ('mkdir', 'dir')
    test_dir_exist = ('mkdir', 'dir_exist')

    def test_mkdir(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_dir_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_dir)
        test_dir_exist_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_dir_exist)

        test_dir_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_dir)
        test_dir_exist_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_dir_exist)

        assert os.access(test_dir_sshfs_path, os.F_OK) is False
        os.mkdir(test_dir_sshfs_path)
        assert os.access(test_dir_sshfs_path, os.F_OK)

        assert os.access(test_dir_xrosfs_path, os.F_OK) is False
        os.mkdir(test_dir_xrosfs_path)
        assert os.access(test_dir_xrosfs_path, os.F_OK)

        assert os.stat(test_dir_sshfs_path).st_mode == \
            os.stat(test_dir_xrosfs_path).st_mode

        # mkdir to exist dir -> fail
        with pytest.raises(OSError) as excinfo_sshfs:
            os.mkdir(test_dir_exist_sshfs_path)
        with pytest.raises(OSError) as excinfo_xrosfs:
            os.mkdir(test_dir_exist_xrosfs_path)
        # 'FileExistsError: [Errno 17] File exists'
        assert excinfo_sshfs.typename == excinfo_xrosfs.typename
        assert excinfo_sshfs.value.errno == excinfo_xrosfs.value.errno
        assert excinfo_sshfs.value.strerror == excinfo_xrosfs.value.strerror
