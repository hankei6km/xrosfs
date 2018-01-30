# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import stat
import pytest


class TestChmod():

    test_file = ('chmod', 'test.txt')
    no_exist_xrosfs_file = ('chmod', 'no_exist.txt')

    def test_chmod(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_file)
        test_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_file)
        no_exist_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_xrosfs_file)

        assert os.access(test_file_sshfs_path, os.X_OK) is False
        assert os.access(test_file_xrosfs_path, os.X_OK) is False

        assert os.chmod(test_file_sshfs_path, stat.S_IEXEC) is None
        assert os.chmod(test_file_xrosfs_path, stat.S_IEXEC) is None

        assert os.access(test_file_sshfs_path, os.X_OK)
        assert os.access(test_file_xrosfs_path, os.X_OK)
        assert os.access(test_file_sshfs_path, os.X_OK) == \
            os.access(test_file_xrosfs_path, os.X_OK)

        with pytest.raises(OSError) as excinfo:
            assert os.chmod(no_exist_file_xrosfs_path, stat.S_IEXEC) is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
