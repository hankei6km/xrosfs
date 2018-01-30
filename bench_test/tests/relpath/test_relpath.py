# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import filecmp


class TestReadWrite():

    test_file = ('test.txt')

    def test_read_write(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, self.test_file)

        test_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, self.test_file)

        with open(test_file_xrosfs_path, 'r') as fd:
            assert fd.read() == 'mounted relpath\n'
        assert filecmp.cmp(test_file_sshfs_path, test_file_xrosfs_path) is True
