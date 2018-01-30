# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
from unittest import mock
import pytest
import asyncio
from extra.xros_over.xros_over.xros_bump import \
    _probe_path_to_container, BumpContainer

Mock = mock.Mock


def get_event(directive, name):
    return {
        'Directive': directive,
        'Actor': {
            'Attributes': {
                'name': name
            }
        }
    }


class TestDebounceFuture():
    pytestmark = pytest.mark.asyncio

    async def test_bump_path(self, event_loop):
        export_path = os.path.join('/', 'export')
        name = 'container2'
        with BumpContainer(export_path, loop=event_loop) as bc:
            assert bc._bump_path(get_event('add', name)) == \
                os.path.join(export_path, name)

    async def test_probe_path_to_container(self, event_loop):
        with mock.patch('os.listdir') as mock_listdir:
            _probe_path_to_container(event_loop, '/path/to')
            mock_listdir.assert_called_once_with('/path/to')

    async def test_bump(self, event_loop):
        export_path = os.path.join('/', 'export')
        name = 'container2'
        event_add = get_event('add', name)
        event_del = get_event('del', name)
        with BumpContainer(
                export_path,
                bump_at_container_awaken=True,
                loop=event_loop
        ) as bc:
            with mock.patch(
                    'extra.xros_over.xros_over'
                    '.xros_bump._list_dir_path_to_container'
            ) as mock_listdir:
                mock_listdir.return_value = {
                    'test': 'add'
                }

                async def async_side_effect_umount(bump_path):
                    return {
                        'test': 'del'
                    }
                bc._umount_container_name = Mock(
                    side_effect=async_side_effect_umount
                )

                assert await bc.bump(event_add) == {
                    '_debug': {'test': 'add'}
                }
                assert await bc.bump(event_del) == {
                    '_debug': {'test': 'del'}
                }

                mock_listdir.assert_called_once_with(
                    os.path.join(export_path, 'container2')
                )
                bc._umount_container_name.assert_called_once_with(
                    os.path.join(export_path, 'container2')
                )

    async def test_bump_skip(self, event_loop):
        export_path = os.path.join('/', 'export')
        name = 'container2'
        event = get_event('add', name)
        with BumpContainer(
                export_path,
                bump_at_container_awaken=False,
                loop=event_loop
        ) as bc:
            with mock.patch(
                    'extra.xros_over.xros_over'
                    '.xros_bump._list_dir_path_to_container'
            ) as mock_listdir:
                mock_listdir.return_value = {
                    'test': 'test value'
                }
                assert await bc.bump(event) == {
                    'skipped': 'container2:add'
                }
                assert await bc.bump(event) == {
                    'cancelled': 'container2:add'
                }
                assert await bc.bump(event) == {
                    'cancelled': 'container2:add'
                }

    async def test_bump_cancel(self, event_loop):
        export_path = os.path.join('/', 'export')
        name = 'container2'
        event = get_event('add', name)
        with BumpContainer(
                export_path,
                bump_at_container_awaken=True,
                loop=event_loop
        ) as bc:
            with mock.patch(
                    'extra.xros_over.xros_over'
                    '.xros_bump._list_dir_path_to_container'
            ) as mock_listdir:
                mock_listdir.return_value = {
                    'test': 'test value'
                }
                assert await bc.bump(event) == {
                    '_debug': {'test': 'test value'}
                }
                assert await bc.bump(event) == {
                    'cancelled': 'container2:add'
                }
                assert await bc.bump(event) == {
                    'cancelled': 'container2:add'
                }

    async def test_bump_not_cancel(self, event_loop):
        export_path = os.path.join('/', 'export')
        name = 'container2'
        event = get_event('add', name)
        with BumpContainer(
                export_path,
                timeout=0.1,
                bump_at_container_awaken=True,
                loop=event_loop
        ) as bc:
            with mock.patch(
                    'extra.xros_over.xros_over'
                    '.xros_bump._list_dir_path_to_container'
            ) as mock_listdir:
                mock_listdir.return_value = {
                    'test': 'test value'
                }
                assert await bc.bump(event) == {
                    '_debug': {'test': 'test value'}
                }
                await asyncio.sleep(0.2)
                assert await bc.bump(event) == {
                    '_debug': {'test': 'test value'}
                }
                assert await bc.bump(event) == {
                    'cancelled': 'container2:add'
                }
