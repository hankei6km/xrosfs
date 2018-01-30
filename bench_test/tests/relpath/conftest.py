# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
from pathlib import Path
import pytest


@pytest.fixture
def mnt_path():
    return os.path.join(
        # https://stackoverflow.com/questions/27844088/python-get-directory-two-levels-up
        str(Path(os.path.realpath(__file__)).parents[2]),
        *('mnt', 'relpath')
    )


@pytest.fixture
def mnt_sshfs_path():
    return os.path.join(mnt_path(), 'sshfs')


@pytest.fixture
def mnt_xrosfs_path():
    return os.path.join(mnt_path(), 'xrosfs')
