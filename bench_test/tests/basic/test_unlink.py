# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestUnlink():

    test_xrosfs_file = ('unlink', 'test.txt')
    no_exist_xrosfs_file = ('unlink', 'no_exist.txt')

    def test_unlink(self, mnt_xrosfs_path):
        test_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_xrosfs_file)
        no_exist_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_xrosfs_file)

        # not compare results with sshfs
        assert os.access(test_file_xrosfs_path, os.F_OK)
        assert os.unlink(test_file_xrosfs_path) is None
        assert os.access(test_file_xrosfs_path, os.F_OK) is False

        with pytest.raises(OSError) as excinfo:
            assert os.unlink(no_exist_file_xrosfs_path) is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
