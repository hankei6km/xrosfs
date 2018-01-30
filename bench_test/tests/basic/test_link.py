# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestLink():

    test_root = ('symlink')
    test_file_target_file = ('link', 'file_target')
    test_file_name_file = ('link', 'file_name')

    no_exist_xrosfs_file = ('link', 'no_exist_xrosfs.txt')

    def test_link(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_file_target_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_file_target_file)
        test_file_name_sshfs_path =  \
            os.path.join(mnt_sshfs_path, *self.test_file_name_file)

        test_file_target_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_file_target_file)
        test_file_name_xrosfs_path =  \
            os.path.join(mnt_xrosfs_path, *self.test_file_name_file)

        no_exist_xrosfs_file_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_xrosfs_file)

        # check initial state
        assert os.stat(test_file_target_sshfs_path).st_nlink == 1
        assert os.stat(test_file_target_xrosfs_path).st_nlink == 1

        # create link to file
        assert os.link(test_file_target_sshfs_path,
                       test_file_name_sshfs_path) is None
        assert os.link(test_file_target_xrosfs_path,
                       test_file_name_xrosfs_path) is None

        # always st_link == 1 from sshfs ??
        # assert os.stat(test_file_target_sshfs_path).st_nlink == 2
        assert os.stat(test_file_target_xrosfs_path).st_nlink == 2
        with open(test_file_name_sshfs_path, 'r') as fd:
            assert fd.read() == 'target file\n'
        with open(test_file_name_xrosfs_path, 'r') as fd:
            assert fd.read() == 'target file\n'

        # unlink to file
        assert os.unlink(test_file_name_sshfs_path) is None
        assert os.unlink(test_file_name_xrosfs_path) is None

        assert os.stat(test_file_target_sshfs_path).st_nlink == 1

        # 'os.fsync' couldn't update count.
        # fd = os.open(test_file_target_xrosfs_path, os.O_WRONLY)
        # assert os.stat(test_file_target_xrosfs_path).st_nlink == 1
        # os.fsync(fd)
        # os.close(fd)
        #
        # `sync` or `sleep` could update count.
        # os.sync()
        # import time
        # time.sleep(1)
        #
        # assert os.stat(test_file_target_xrosfs_path).st_nlink == 1

        with pytest.raises(OSError) as excinfo:
            assert os.rename(no_exist_xrosfs_file_path,
                             no_exist_xrosfs_file_path + '_test') is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
