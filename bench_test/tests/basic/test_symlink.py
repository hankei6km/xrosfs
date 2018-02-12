# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestSymlink():

    test_root = ('symlink')
    test_dir_target_dir = ('symlink', 'dir_target')
    test_file_target_file = ('symlink', 'file_target')

    base_sshfs_dir = ('symlink')
    test_dir_name_sshfs_dir = ('symlink', 'dir_name_sshfs')
    test_file_name_sshfs_file = ('symlink', 'file_name_sshfs')

    base_xrosfs_dir = ('symlink')
    test_dir_name_xrosfs_dir = ('symlink', 'dir_name_xrosfs')
    test_file_name_xrosfs_file = ('symlink', 'file_name_xrosfs')

    root_sshfs = ('rename', 'sshfs')
    test_old_sshfs_file = ('rename', 'sshfs', 'test_old.txt')
    test_new_sshfs_file = ('rename', 'sshfs', 'test_new.txt')
    test_dir_old_sshfs_file = ('rename', 'sshfs', 'old', 'test.txt')
    test_dir_new_sshfs_file = ('rename', 'sshfs', 'new', 'test.txt')

    root_xrosfs = ('rename', 'xrosfs')
    test_old_xrosfs_file = ('rename', 'xrosfs', 'test_old.txt')
    test_new_xrosfs_file = ('rename', 'xrosfs', 'test_new.txt')
    test_dir_old_xrosfs_file = ('rename', 'xrosfs', 'old', 'test.txt')
    test_dir_new_xrosfs_file = ('rename', 'xrosfs', 'new', 'test.txt')

    no_exist_xrosfs_file = ('rename', 'no_exist_xrosfs.txt')

    def test_symlink(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_dir_target_rel_path =  \
            os.path.join(*self.test_dir_target_dir[-1:])
        test_file_target_rel_path =  \
            os.path.join(*self.test_file_target_file[-1:])

        root_sshfs_path = \
            os.path.join(mnt_xrosfs_path, self.test_root)
        test_dir_target_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_dir_target_dir)
        test_dir_name_sshfs_path =  \
            os.path.join(mnt_sshfs_path, *self.test_dir_name_sshfs_dir)
        test_file_name_sshfs_path =  \
            os.path.join(mnt_sshfs_path, *self.test_file_name_sshfs_file)

        root_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, self.test_root)
        test_dir_target_xrosfs_path =  \
            os.path.join(mnt_xrosfs_path, *self.test_dir_target_dir)
        test_dir_name_xrosfs_path =  \
            os.path.join(mnt_xrosfs_path, *self.test_dir_name_xrosfs_dir)
        test_file_name_xrosfs_path =  \
            os.path.join(mnt_xrosfs_path, *self.test_file_name_xrosfs_file)

        no_exist_xrosfs_file_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_xrosfs_file)

        # create symlink to direcotory
        assert os.symlink(test_dir_target_sshfs_path,
                          test_dir_name_sshfs_path) is None
        assert os.symlink(test_dir_target_xrosfs_path,
                          test_dir_name_xrosfs_path) is None
        stat_sshfs_info = \
            os.stat(test_dir_name_sshfs_path, follow_symlinks=False)
        stat_xrosfs_info = \
            os.stat(test_dir_name_xrosfs_path, follow_symlinks=False)
        assert stat_sshfs_info.st_mode == stat_xrosfs_info.st_mode
        assert os.path.islink(test_dir_name_sshfs_path) == \
            os.path.islink(test_dir_name_xrosfs_path)
        assert os.path.isdir(test_dir_name_sshfs_path) == \
            os.path.isdir(test_dir_name_xrosfs_path)
        ls_sshfs = sorted(os.listdir(test_dir_name_sshfs_path))
        ls_xrosfs = sorted(os.listdir(test_dir_name_xrosfs_path))
        assert len(ls_sshfs) > 0
        assert ls_sshfs == ls_xrosfs

        os.unlink(test_dir_name_sshfs_path)
        os.unlink(test_dir_name_xrosfs_path)

        # create symlink to direcotory(rel path)
        save_cwd = os.getcwd()
        os.chdir(root_sshfs_path)
        assert os.symlink(test_dir_target_rel_path,
                          test_dir_name_sshfs_path) is None
        os.chdir(root_xrosfs_path)
        assert os.symlink(test_dir_target_rel_path,
                          test_dir_name_xrosfs_path) is None
        os.chdir(save_cwd)
        ls_sshfs = sorted(os.listdir(test_dir_name_sshfs_path))
        ls_xrosfs = sorted(os.listdir(test_dir_name_xrosfs_path))
        assert len(ls_sshfs) > 0
        assert ls_sshfs == ls_xrosfs

        # create symlink to file(rel path)
        save_cwd = os.getcwd()
        os.chdir(root_sshfs_path)
        assert os.symlink(test_file_target_rel_path,
                          test_file_name_sshfs_path) is None
        os.chdir(root_xrosfs_path)
        assert os.symlink(test_file_target_rel_path,
                          test_file_name_xrosfs_path) is None
        os.chdir(save_cwd)
        with open(test_file_name_sshfs_path, 'r') as fd:
            assert fd.read() == 'target file\n'
        with open(test_file_name_xrosfs_path, 'r') as fd:
            assert fd.read() == 'target file\n'

        with pytest.raises(OSError) as excinfo:
            assert os.rename(no_exist_xrosfs_file_path,
                             no_exist_xrosfs_file_path + '_test') is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
