# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


class TestReadlink():

    target_file = ('readlink', 'tgt', 'target.txt')
    outer_target_file = ('..', '..', 'outer_target.txt')

    link_rel_file = ('readlink', 'link_rel.txt')
    link_abs_file = ('readlink', 'link_abs.txt')
    link_outer_file = ('readlink', 'link_outer.txt')

    no_exist_file = ('readlink', 'no_exist.txt')

    def test_readlink(self,
                      export_sshfs_path,
                      export_xrosfs_path,
                      mnt_path,
                      mnt_sshfs_path,
                      mnt_xrosfs_path):
        outer_target_path = \
            os.path.join(*self.outer_target_file)
        target_rel_path = \
            os.path.join(*self.target_file[-2:])

        target_container_sshfs_path = \
            os.path.join(export_sshfs_path, *self.target_file)
        target_host_sshfs_path = \
            os.path.join(mnt_sshfs_path, *self.target_file)

        link_sshfs_rel_path = \
            os.path.join(mnt_sshfs_path, *self.link_rel_file)
        link_sshfs_abs_path = \
            os.path.join(mnt_sshfs_path, *self.link_abs_file)
        link_sshfs_outer_path = \
            os.path.join(mnt_sshfs_path, *self.link_outer_file)

        target_container_xrosfs_path = \
            os.path.join(export_xrosfs_path, *self.target_file)
        target_host_xrosfs_path = \
            os.path.join(mnt_xrosfs_path, *self.target_file)

        link_xrosfs_rel_path = \
            os.path.join(mnt_xrosfs_path, *self.link_rel_file)
        link_xrosfs_abs_path = \
            os.path.join(mnt_xrosfs_path, *self.link_abs_file)
        link_xrosfs_outer_path = \
            os.path.join(mnt_xrosfs_path, *self.link_outer_file)

        no_exist_file_path = os.path.join(mnt_xrosfs_path, *self.no_exist_file)

        # check link to
        assert os.readlink(link_sshfs_rel_path) == target_rel_path
        assert os.readlink(link_sshfs_abs_path) == target_container_sshfs_path
        assert os.readlink(link_sshfs_outer_path) == outer_target_path

        assert os.readlink(link_xrosfs_rel_path) == target_rel_path
        assert os.readlink(link_xrosfs_abs_path) == \
            target_container_xrosfs_path
        assert os.readlink(link_xrosfs_outer_path) == outer_target_path

        # check read content from target file via link
        with open(target_host_sshfs_path, 'r') as fd:
            target_content = fd.read()
        with open(link_sshfs_rel_path, 'r') as fd:
            assert fd.read() == target_content

        with open(target_host_xrosfs_path, 'r') as fd:
            target_content = fd.read()
        with open(link_xrosfs_rel_path, 'r') as fd:
            assert fd.read() == target_content

        # check link out
        # (be careful, not exist link to abs path on host filesystem)
        with pytest.raises(OSError) as excinfo_sshfs:
            with open(link_sshfs_abs_path, 'r') as fd:
                assert fd.read() == target_content
        with pytest.raises(OSError) as excinfo_xrosfs:
            with open(link_xrosfs_abs_path, 'r') as fd:
                assert fd.read() == target_content
        # 'FileNotFoundError: [Errno 2] No such file or directory:'
        assert excinfo_sshfs.typename == excinfo_xrosfs.typename
        assert excinfo_sshfs.value.errno == excinfo_xrosfs.value.errno
        assert excinfo_sshfs.value.strerror == excinfo_xrosfs.value.strerror

        # check read content from target outer mount point
        with open(link_sshfs_outer_path, 'r') as fd:
            assert fd.read() == 'outer target on host'
        with open(link_xrosfs_outer_path, 'r') as fd:
            assert fd.read() == 'outer target on host'

        with pytest.raises(OSError) as excinfo:
            assert os.readlink(no_exist_file_path) is None
        assert 'FileNotFoundError: [Errno 2] No such file or directory:'\
               in str(excinfo)
