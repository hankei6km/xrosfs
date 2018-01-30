# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestReaddir():

    no_exist_file = ('readdir', 'no_exist.txt')

    def test_readdir(self, mnt_sshfs_path, mnt_xrosfs_path):
        no_exist_file_path = \
            os.path.join(mnt_xrosfs_path, *self.no_exist_file)

        ls_sshfs = os.listdir(
            os.path.join(mnt_sshfs_path, 'readdir'))
        ls_xrosfs = os.listdir(os.path.join(
            mnt_xrosfs_path, 'readdir'))
        assert ls_sshfs == ls_xrosfs

        with pytest.raises(OSError) as excinfo:
            assert os.listdir(no_exist_file_path)
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
