# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

# Test read and write with open and release.

import os
import io
import filecmp
import pytest


class TestReadWrite():

    test_sshfs_file = ('read_write', 'test_sshfs.txt')
    test_xrosfs_file = ('read_write', 'test_xrosfs.txt')

    def create_test_file(self, file_path):
        with open(file_path, 'w') as fd:
            fd.write('01234567')
            fd.seek(5, 0)
            fd.write('ABCDEFG')

    def read_part_of_test_file(self, file_path):
        ret = ''
        with open(file_path, 'r') as fd:
            fd.seek(3, 0)
            ret = fd.read(4)
        return ret

    def read_writing_test_file(self, file_path):
        ret = ''
        with open(file_path, 'r+') as fd:
            ret = fd.read(4)
        return ret

    def write_additional_data_test_file(self, file_path):
        with open(file_path, 'w+') as fd:
            fd.write('add')

    def trunc_write_data_test_file(self, file_path):
        with open(file_path, 'w') as fd:
            fd.write('trunk')

    def append_data_test_file(self, file_path):
        with open(file_path, 'a') as fd:
            fd.write('append')

    def write_to_rdonly(self, file_path):
        with open(file_path, 'r') as fd:
            fd.write('fail?')

    def open_excl_test_file(self, file_path):
        # f = os.open(file_path, os.O_EXCL | os.O_CREAT)
        # os.close(f)
        ret = ''
        with open(file_path, 'x') as fd:
            ret = fd.read(4)
        return ret

    def test_read_write(self, mnt_sshfs_path, mnt_xrosfs_path):
        test_file_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.test_sshfs_file)
        self.create_test_file(test_file_sshfs_path)

        test_file_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.test_xrosfs_file)
        self.create_test_file(test_file_xrosfs_path)

        assert filecmp.cmp(test_file_sshfs_path, test_file_xrosfs_path) is True
        assert self.read_part_of_test_file(test_file_xrosfs_path) != ''
        assert self.read_part_of_test_file(test_file_sshfs_path) == \
            self.read_part_of_test_file(test_file_xrosfs_path)

        assert self.read_writing_test_file(test_file_sshfs_path) == \
            self.read_writing_test_file(test_file_xrosfs_path)

        self.write_additional_data_test_file(test_file_sshfs_path)
        self.write_additional_data_test_file(test_file_xrosfs_path)
        assert filecmp.cmp(test_file_sshfs_path, test_file_xrosfs_path) is True

        self.trunc_write_data_test_file(test_file_sshfs_path)
        self.trunc_write_data_test_file(test_file_xrosfs_path)
        assert filecmp.cmp(test_file_sshfs_path, test_file_xrosfs_path) is True

        self.append_data_test_file(test_file_sshfs_path)
        self.append_data_test_file(test_file_xrosfs_path)
        assert filecmp.cmp(test_file_sshfs_path, test_file_xrosfs_path) is True

        with pytest.raises(io.UnsupportedOperation) as excinfo:
            self.write_to_rdonly(test_file_sshfs_path)
        assert 'not writable' in str(excinfo)
        with pytest.raises(io.UnsupportedOperation) as excinfo:
            self.write_to_rdonly(test_file_xrosfs_path)
        assert 'not writable' in str(excinfo)
        assert filecmp.cmp(test_file_sshfs_path, test_file_xrosfs_path) is True

        with pytest.raises(FileExistsError) as excinfo:
            self.open_excl_test_file(test_file_sshfs_path)
        assert 'File exists' in str(excinfo)
        with pytest.raises(FileExistsError) as excinfo:
            # I thought that this test will not pass.
            # Did handle `O_EXCL` falg in local(host) side by FUSE?
            # xrosfs does not handle their(`O_EXCL` and more) flags at open
            # on remote(container) side...
            self.open_excl_test_file(test_file_xrosfs_path)
        assert 'File exists' in str(excinfo)
