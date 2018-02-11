# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import argparse
import shutil
import time
# import docker
# from pathlib import Path
import pytest
from bench_container import Bench


def main():
    # Parse args
    parser = argparse.ArgumentParser(
        description='Test actually file operations on FUSE in bench continer',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('bench_container_image',
                        type=str,
                        nargs='?',
                        default='hankei6km/xrosfs-bench:latest',
                        metavar='bench container image',
                        help='Docker Image of bench container')
    parser.add_argument('--pytest-opts',
                        dest='pytest_opts',
                        metavar='',
                        action='append',
                        default=[],
                        help='options to pytest')

    args = parser.parse_args()
    bench_container_image = args.bench_container_image
    pytest_opts = args.pytest_opts

    # Setup paths
    script_path = os.path.dirname(os.path.realpath(__file__))
    mnt_path = os.path.join(script_path, 'mnt')
    mnt_basic_path = os.path.join(mnt_path, 'basic')
    mnt_basic_sshfs_path = os.path.join(mnt_path, *('basic', 'sshfs'))
    mnt_basic_xrosfs_path = os.path.join(mnt_path, *('basic', 'xrosfs'))
    mnt_relpath_path = os.path.join(mnt_path, 'relpath')
    mnt_relpath_sshfs_path = os.path.join(mnt_path, *('relpath', 'sshfs'))
    mnt_relpath_xrosfs_path = os.path.join(mnt_path, *('relpath', 'xrosfs'))
    mnt_useruri_path = os.path.join(mnt_path, 'useruri')
    mnt_useruri_sshfs_path = os.path.join(mnt_path, *('useruri', 'sshfs'))
    mnt_useruri_xrosfs_path = os.path.join(mnt_path, *('useruri', 'xrosfs'))

    # Create test files and directories
    os.system(os.path.join(script_path, 'setup.sh'))
    if os.path.exists(mnt_path):
        shutil.rmtree(mnt_path)
    os.mkdir(mnt_path)
    os.mkdir(mnt_basic_path)
    os.mkdir(mnt_basic_sshfs_path)
    os.mkdir(mnt_basic_xrosfs_path)
    os.mkdir(mnt_relpath_path)
    os.mkdir(mnt_relpath_sshfs_path)
    os.mkdir(mnt_relpath_xrosfs_path)
    os.mkdir(mnt_useruri_path)
    os.mkdir(mnt_useruri_sshfs_path)
    os.mkdir(mnt_useruri_xrosfs_path)
    # Prepare test data that use in `basic/test_readlink.py`.
    # It could not include setup script int bench container.
    with open(os.path.join(mnt_basic_path, 'outer_target.txt'), 'w') as fd:
        txt = 'outer target on host'
        fd.write(txt)

    # Run bench container
    bench = Bench(bench_container_image)
    with Bench(bench_container_image) as bench:
        bench.run()

        # Mount bench via /sshfs/xrosfs
        bench.mount_sshfs(
            'root', '/export/sshfs', mnt_basic_sshfs_path, passwd='root'
        )
        bench.mount_sshfs(
            'root', 'sshfs', mnt_relpath_sshfs_path, passwd='root'
        )
        bench.mount_sshfs(
            'pdu', 'sshfs', mnt_useruri_sshfs_path, passwd='passwordpassword'
        )
        bench.mount_xrosfs('root', '/export/xrosfs', mnt_basic_xrosfs_path)
        bench.mount_xrosfs('root', 'xrosfs', mnt_relpath_xrosfs_path)
        bench.mount_xrosfs('pdu', 'xrosfs', mnt_useruri_xrosfs_path)
        # while not os.path.exists(os

        time.sleep(3)
        # os.system('ls ' + os.path.join(mnt_sshfs_path, 'readdir'))

        # Run test
        tests_path = os.path.join(script_path, 'tests')
        pytest.main(pytest_opts + [tests_path])
        # TODO: Support to run and watch tests with pytest_watch


if __name__ == '__main__':  # pragma: no cover.
    main()
