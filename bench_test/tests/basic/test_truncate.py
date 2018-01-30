# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

# Test truncate with open and releasei and create.

import os


class TestTruncate():

    test_file = ('truncate', 'test.txt')
    no_exist_file = ('truncate', 'no_exist.txt')

    def test_truncate(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_file)
        no_exist_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.no_exist_file)
        test_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_file)
        no_exist_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_file)

        with open(test_file_sshfs_path, 'w') as fd_sshfs, \
                open(test_file_xrosfs_path, 'w') as fd_xrosfs:

            fd_sshfs.truncate(100)
            fd_xrosfs.truncate(100)
            assert os.path.getsize(fd_sshfs.fileno()) == \
                os.path.getsize(fd_xrosfs.fileno())
            assert os.path.getsize(fd_xrosfs.fileno()) == 100

            fd_sshfs.truncate(55)
            fd_xrosfs.truncate(55)
            assert os.path.getsize(fd_sshfs.fileno()) == \
                os.path.getsize(fd_xrosfs.fileno())
            assert os.path.getsize(fd_xrosfs.fileno()) == 55

        with open(no_exist_file_sshfs_path, 'w') as fd_sshfs, \
                open(no_exist_file_xrosfs_path, 'w') as fd_xrosfs:

            fd_sshfs.truncate(100)
            fd_xrosfs.truncate(100)
            assert os.path.getsize(fd_sshfs.fileno()) == \
                os.path.getsize(fd_xrosfs.fileno())
            assert os.path.getsize(fd_xrosfs.fileno()) == 100
