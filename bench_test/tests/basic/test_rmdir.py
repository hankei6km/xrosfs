# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import shutil
import pytest


class TestReadlink():

    test_empty_dir = ('rmdir', 'dir_empty')
    test_normal_dir = ('rmdir', 'dir_normal')

    no_exist_file = ('readlink', 'no_exist.txt')

    def test_readlink(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_empty_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_empty_dir)
        test_normal_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_normal_dir)

        test_empty_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_empty_dir)
        test_normal_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_normal_dir)

        # rmdir dir_empty
        assert os.access(test_empty_sshfs_path, os.F_OK)
        os.rmdir(test_empty_sshfs_path)
        assert os.access(test_empty_sshfs_path, os.F_OK) is False

        assert os.access(test_empty_xrosfs_path, os.F_OK)
        os.rmdir(test_empty_xrosfs_path)
        assert os.access(test_empty_xrosfs_path, os.F_OK) is False

        # rmdir dir_normal -> failed
        with pytest.raises(OSError) as excinfo_sshfs:
            os.rmdir(test_normal_sshfs_path)
        with pytest.raises(OSError) as excinfo_xrosfs:
            os.rmdir(test_normal_xrosfs_path)
        # 'OSError: [Errno 39] Directory not empty:'
        assert excinfo_sshfs.typename == excinfo_xrosfs.typename
        assert excinfo_sshfs.value.errno == excinfo_xrosfs.value.errno
        assert excinfo_sshfs.value.strerror == excinfo_xrosfs.value.strerror

        # rmdir dir_normal -> success
        assert os.access(test_normal_sshfs_path, os.F_OK)
        shutil.rmtree(test_normal_sshfs_path)
        assert os.access(test_normal_sshfs_path, os.F_OK) is False

        assert os.access(test_normal_xrosfs_path, os.F_OK)
        shutil.rmtree(test_normal_xrosfs_path)
        assert os.access(test_normal_xrosfs_path, os.F_OK) is False

        with pytest.raises(OSError) as excinfo:
            assert os.rmdir(test_empty_xrosfs_path) is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
