# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestRename():

    test_root = tuple('rename')
    test_old_file = ('rename', 'test_old.txt')
    test_new_file = ('rename', 'test_new.txt')
    test_dir_old_file = ('rename', 'old', 'test.txt')
    test_dir_new_file = ('rename', 'new', 'test.txt')

    no_exist_xrosfs_file = ('rename', 'no_exist_xrosfs.txt')

    def test_rename(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_root_sshfs_path =  \
            os.path.join(mnt_sshfs_path, *self.test_root)
        test_old_sshfs_file_path =  \
            os.path.join(mnt_sshfs_path, *self.test_old_file)
        test_new_sshfs_file_path = \
            os.path.join(mnt_sshfs_path, *self.test_new_file)
        test_dir_old_sshfs_file_path = \
            os.path.join(mnt_sshfs_path, *self.test_dir_old_file)
        test_dir_new_sshfs_file_path =  \
            os.path.join(mnt_sshfs_path, *self.test_dir_new_file)

        test_root_xrosfs_path =  \
            os.path.join(mnt_xrosfs_path, *self.test_root)
        test_old_xrosfs_file_path =  \
            os.path.join(mnt_xrosfs_path, *self.test_old_file)
        test_new_xrosfs_file_path = \
            os.path.join(mnt_xrosfs_path, *self.test_new_file)
        test_dir_old_xrosfs_file_path = \
            os.path.join(mnt_xrosfs_path, *self.test_dir_old_file)
        test_dir_new_xrosfs_file_path =  \
            os.path.join(mnt_xrosfs_path, *self.test_dir_new_file)

        no_exist_xrosfs_file_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_xrosfs_file)

        # rename file name
        assert os.access(test_old_sshfs_file_path, os.F_OK)
        assert os.access(test_new_sshfs_file_path, os.F_OK) is False
        assert os.access(test_old_xrosfs_file_path, os.F_OK)
        assert os.access(test_new_xrosfs_file_path, os.F_OK) is False

        assert os.rename(
            test_old_sshfs_file_path, test_new_sshfs_file_path) is None
        assert os.rename(
            test_old_xrosfs_file_path, test_new_xrosfs_file_path) is None

        assert os.access(test_old_sshfs_file_path, os.F_OK) is False
        assert os.access(test_new_sshfs_file_path, os.F_OK)
        assert os.access(test_old_xrosfs_file_path, os.F_OK) is False
        assert os.access(test_new_xrosfs_file_path, os.F_OK)

        # rename dir name
        assert os.access(test_dir_old_sshfs_file_path, os.F_OK)
        assert os.access(test_dir_new_sshfs_file_path, os.F_OK) is False
        assert os.access(test_dir_old_xrosfs_file_path, os.F_OK)
        assert os.access(test_dir_new_xrosfs_file_path, os.F_OK) is False

        sshfs_rename_permit_err = False
        try:
            assert os.rename(os.path.dirname(test_dir_old_sshfs_file_path),
                             os.path.dirname(test_dir_new_sshfs_file_path)
                             ) is None

        except OSError as exc:
            sshfs_rename_permit_err = True
            # `mv /path/to/foo/file /path/to/bar/file` to be permit error
            # on travis-ci.
            # local environment(ubuntu trusty container on arch linux)
            # had permits above case. why??
            # therefore, avoid rename dir test at permit error occrured
            sshfs_rename_permit_err = True
            if 'XROSFS_BENCH_AVOID_RNAME_DIR' in os.environ:
                None
            else:
                raise exc

        if not sshfs_rename_permit_err:
            assert os.rename(os.path.dirname(test_dir_old_xrosfs_file_path),
                             os.path.dirname(test_dir_new_xrosfs_file_path)
                             ) is None

            assert os.access(test_dir_old_sshfs_file_path, os.F_OK) is False
            assert os.access(test_dir_new_sshfs_file_path, os.F_OK)
            assert os.access(test_dir_old_xrosfs_file_path, os.F_OK) is False
            assert os.access(test_dir_new_xrosfs_file_path, os.F_OK)

        # compare filename on sshfs/ and xrosfs/
        all_sshfs = [
            os.path.join(test_root.replace(test_root_sshfs_path, ''), name)
            for test_root, dirname, filename in os.walk(test_root_sshfs_path)
            for name in filename
        ]
        all_xrosfs = [
            os.path.join(test_root.replace(test_root_xrosfs_path, ''), name)
            for test_root, dirname, filename in os.walk(test_root_xrosfs_path)
            for name in filename
        ]

        assert all_sshfs == all_xrosfs

        with pytest.raises(OSError) as excinfo:
            assert os.rename(no_exist_xrosfs_file_path,
                             no_exist_xrosfs_file_path + '_test') is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
