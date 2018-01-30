# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import pytest

from xrosfs.args import parse


class TestArgs():

    def test_valid_args(self):
        mount_args = parse(['user@container:/path/to', '/mnt'])
        assert mount_args.foreground is False
        assert mount_args.debug is False
        assert mount_args.mount_opts == {}
        assert mount_args.user == 'user'
        assert mount_args.container == 'container'
        assert mount_args.server_path == '/path/to'
        assert mount_args.mountpoint == '/mnt'

    def test_user_none(self):
        mount_args = parse(['container:/path/to', '/mnt'])
        assert mount_args.foreground is False
        assert mount_args.debug is False
        assert mount_args.mount_opts == {}
        assert mount_args.user == ''
        assert mount_args.container == 'container'
        assert mount_args.server_path == '/path/to'
        assert mount_args.mountpoint == '/mnt'

    def test_server_path_none(self):
        mount_args = parse(['user@container:', '/mnt'])
        assert mount_args.foreground is False
        assert mount_args.debug is False
        assert mount_args.mount_opts == {}
        assert mount_args.user == 'user'
        assert mount_args.container == 'container'
        assert mount_args.server_path == ''
        assert mount_args.mountpoint == '/mnt'

    def test_server_path_rel(self):
        mount_args = parse(['user@container:path/to', '/mnt'])
        assert mount_args.foreground is False
        assert mount_args.debug is False
        assert mount_args.mount_opts == {}
        assert mount_args.user == 'user'
        assert mount_args.container == 'container'
        assert mount_args.server_path == 'path/to'
        assert mount_args.mountpoint == '/mnt'

    def test_foreground(self):
        mount_args = parse(['-f', 'user@container:path/to', '/mnt'])
        assert mount_args.foreground is True
        assert mount_args.debug is False
        assert mount_args.mount_opts == {}
        assert mount_args.user == 'user'
        assert mount_args.container == 'container'
        assert mount_args.server_path == 'path/to'
        assert mount_args.mountpoint == '/mnt'

    def test_debug(self):
        mount_args = parse(['-f', '-d', 'user@container:path/to', '/mnt'])
        assert mount_args.foreground is True
        assert mount_args.debug is True
        assert mount_args.mount_opts == {'debug': True}
        assert mount_args.user == 'user'
        assert mount_args.container == 'container'
        assert mount_args.server_path == 'path/to'
        assert mount_args.mountpoint == '/mnt'

    def test_password(self):
        with pytest.raises(SystemExit) as excinfo:
            parse(['user:pass@container:path/to', '/mnt'])
        assert 'Password is not supported:' in str(excinfo)

    def test_invalid_container(self):
        with pytest.raises(SystemExit) as excinfo:
            parse(['user@container/path/to', '/mnt'])
        assert 'Invalid format(bottom of container is not' in str(excinfo)
        with pytest.raises(SystemExit) as excinfo:
            parse(['user@container', '/mnt'])
        assert 'Invalid format(bottom of container is not' in str(excinfo)

    def test_mountpoint_none(self):
        with pytest.raises(SystemExit):
            parse(['user@container:'])

    def test_mount_opts(self):
        mount_args = parse([
            'user@container:path/to', '/mnt',
            '-o', 'allow_other'
        ])
        assert mount_args.foreground is False
        assert mount_args.debug is False
        assert mount_args.user == 'user'
        assert mount_args.container == 'container'
        assert mount_args.server_path == 'path/to'
        assert mount_args.mountpoint == '/mnt'
        assert mount_args.mount_opts == {'allow_other': True}

        mount_args = parse([
            'user@container:path/to', '/mnt',
            '--opts', 'allow_other,default_permissions'
        ])
        assert mount_args.mount_opts == {
            'allow_other': True,
            'default_permissions': True
        }

        mount_args = parse([
            'user@container:path/to', '/mnt',
            '--opts', 'default_permissions',
            '--opts', 'allow_other'
        ])
        assert mount_args.mount_opts == {
            'allow_other': True,
            'default_permissions': True
        }

        mount_args = parse([
            'user@container:path/to', '/mnt',
            '-o', 'default_permissions=true',
            '--opts', 'allow_other'
        ])
        assert mount_args.mount_opts == {
            'allow_other': True,
            'default_permissions': True
        }

        mount_args = parse([
            'user@container:path/to', '/mnt',
            '-o', 'default_permissions=false',
            '--opts', 'allow_other=foo'
        ])
        assert mount_args.mount_opts == {
            'allow_other': 'foo',
            'default_permissions': False
        }
