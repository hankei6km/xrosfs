# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os


class TestAccess():

    test_file = ('access', 'test.txt')
    test_x_file = ('access', 'test_x.txt')
    no_exist_file = ('access', 'no_exist.txt')

    def test_access(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_file)
        test_x_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_x_file)
        no_exist_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.no_exist_file)

        test_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_file)
        test_x_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_x_file)
        no_exist_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_file)

        # Check test data is exist separataly sshfs/xrofs
        assert os.access(test_file_sshfs_path, os.F_OK)
        assert os.access(test_file_xrosfs_path, os.F_OK)

        assert os.access(test_file_sshfs_path, os.F_OK) == \
            os.access(test_file_xrosfs_path, os.F_OK)
        assert os.access(test_file_sshfs_path, os.R_OK) == \
            os.access(test_file_xrosfs_path, os.R_OK)
        assert os.access(test_file_sshfs_path, os.W_OK) == \
            os.access(test_file_xrosfs_path, os.W_OK)
        assert os.access(test_file_sshfs_path, os.X_OK) == \
            os.access(test_file_xrosfs_path, os.X_OK)
        assert os.access(test_file_sshfs_path, os.R_OK | os.W_OK | os.X_OK) \
            == os.access(test_file_xrosfs_path, os.R_OK | os.W_OK | os.X_OK)
        assert os.access(test_file_sshfs_path, os.R_OK | os.W_OK) == \
            os.access(test_file_xrosfs_path, os.R_OK | os.W_OK)
        assert os.access(test_file_sshfs_path, os.R_OK | os.X_OK) == \
            os.access(test_file_xrosfs_path, os.R_OK | os.X_OK)
        assert os.access(test_file_sshfs_path, os.W_OK | os.X_OK) == \
            os.access(test_file_xrosfs_path, os.W_OK | os.X_OK)

        assert os.access(test_x_file_sshfs_path, os.X_OK) == \
            os.access(test_x_file_xrosfs_path, os.X_OK)
        assert os.access(test_x_file_sshfs_path, os.R_OK | os.W_OK | os.X_OK) \
            == os.access(test_x_file_xrosfs_path, os.R_OK | os.W_OK | os.X_OK)
        assert os.access(test_x_file_sshfs_path, os.R_OK | os.W_OK) == \
            os.access(test_x_file_xrosfs_path, os.R_OK | os.W_OK)
        assert os.access(test_x_file_sshfs_path, os.R_OK | os.X_OK) == \
            os.access(test_x_file_xrosfs_path, os.R_OK | os.X_OK)
        assert os.access(test_x_file_sshfs_path, os.W_OK | os.X_OK) == \
            os.access(test_x_file_xrosfs_path, os.W_OK | os.X_OK)

        assert os.access(no_exist_file_sshfs_path, os.F_OK) == \
            os.access(no_exist_file_xrosfs_path, os.F_OK)
        assert os.access(no_exist_file_sshfs_path, os.R_OK) == \
            os.access(no_exist_file_xrosfs_path, os.R_OK)
        assert os.access(no_exist_file_sshfs_path, os.W_OK) == \
            os.access(no_exist_file_xrosfs_path, os.W_OK)
        assert os.access(no_exist_file_sshfs_path, os.X_OK) == \
            os.access(no_exist_file_xrosfs_path, os.X_OK)
        assert os.access(no_exist_file_sshfs_path,
                         os.R_OK | os.W_OK | os.X_OK) == \
            os.access(no_exist_file_xrosfs_path, os.R_OK | os.W_OK | os.X_OK)
        assert os.access(no_exist_file_sshfs_path, os.R_OK | os.W_OK) == \
            os.access(no_exist_file_xrosfs_path, os.R_OK | os.W_OK)
        assert os.access(no_exist_file_sshfs_path, os.R_OK | os.X_OK) == \
            os.access(no_exist_file_xrosfs_path, os.R_OK | os.X_OK)
        assert os.access(no_exist_file_sshfs_path, os.W_OK | os.X_OK) == \
            os.access(no_exist_file_xrosfs_path, os.W_OK | os.X_OK)
