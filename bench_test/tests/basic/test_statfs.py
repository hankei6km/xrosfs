# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os


class TestStatfs():

    test_dir = ['statfs']
    no_exist_file = ('access', 'no_exist.txt')

    def test_statfs(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_dir)
        test_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_dir)

        statfs_sshfs_info = os.statvfs(test_sshfs_path)
        statfs_xrosfs_info = os.statvfs(test_xrosfs_path)

        assert statfs_sshfs_info == statfs_xrosfs_info
