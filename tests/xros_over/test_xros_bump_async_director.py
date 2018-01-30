# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import threading
import asyncio
from unittest import mock
import pytest
from extra.xros_over.xros_over.xros_bump import AsyncDirector

Mock = mock.Mock


def get_event(action, name):
    return {
        'Action': action,
        'Actor': {
            'Attributes': {
                'name': name
            }
        }
    }


class TestAsyncDirector():
    pytestmark = pytest.mark.asyncio

    async def test_loop(self, event_loop):
        def gen(filters, decode):
            yield get_event('start', 'container')
            yield get_event('unpause', 'container')
            yield get_event('stop', 'container')
            yield get_event('pause', 'container')
            yield get_event('die', 'container')
            yield get_event('kill', 'container')
        dirs = iter([
            'add',
            'add',
            'remove',
            'remove',
            'remove',
            'remove',
            'end'
        ])

        client = Mock()
        client.events = gen
        async for event in AsyncDirector(client, loop=event_loop):
            assert event['Directive'] == next(dirs)
        assert next(dirs) == 'end'

    async def test_loop_non_block(self, event_loop):
        lock = threading.Lock()

        async def future_release():
            await asyncio.sleep(0)
            lock.release()
            return True
        future = asyncio.ensure_future(future_release())

        def gen(filters, decode):
            assert lock.acquire(blocking=False) is False
            while not lock.acquire(blocking=False):
                None
            yield get_event('stop', 'container')

        client = Mock()
        client.events = gen

        ad = AsyncDirector(client, loop=event_loop)
        lock.acquire()
        assert (await ad.__anext__())['Directive'] == 'remove'
        assert await future is True
