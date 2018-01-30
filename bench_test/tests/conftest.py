# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import pytest


@pytest.fixture
def export_path():
    return os.path.join('/', '/export')


@pytest.fixture
def export_sshfs_path():
    return os.path.join(export_path(), 'sshfs')


@pytest.fixture
def export_xrosfs_path():
    return os.path.join(export_path(), 'xrosfs')
