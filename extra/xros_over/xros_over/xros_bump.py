# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import sys
import argparse
import asyncio
import functools
from distutils.util import strtobool

import docker


def init_logger(timestamp=True, debug=False, verbose=False):
    from logging import getLogger, \
        StreamHandler, \
        Formatter, \
        DEBUG, \
        INFO, \
        WARNING

    level = WARNING
    if debug:
        level = DEBUG
    elif verbose:
        level = INFO

    logger = getLogger(__name__)
    logger.setLevel(level=level)

    ch = StreamHandler()
    ch.setLevel(level)
    formater_str = '%(name)s:%(lineno)d: %(message)s'
    if timestamp:
        formater_str = '%(asctime)s %(name)s:%(lineno)d: %(message)s'
    formatter = Formatter(formater_str)
    ch.setFormatter(formatter)
    # ch.terminator = ''

    logger.addHandler(ch)

    return logger


def debounce(timeout, cb, loop=asyncio.get_event_loop()):
    handle = None

    def _cb():
        nonlocal handle
        cb()
        handle = None

    def trigger():
        nonlocal handle
        if handle is not None:
            handle.cancel()
        handle = loop.call_later(timeout, _cb)

    return trigger


def _list_dir_path_to_container(bump_path):
    ret = []
    try:
        ret = os.listdir(bump_path)
    except OSError as exc:
        ret = exc
    except FileNotFoundError as exc:
        ret = exc
    return ret


def _probe_path_to_container(loop, bump_path):
    future = loop.run_in_executor(
        None,
        functools.partial(_list_dir_path_to_container, bump_path)
    )
    # future.add_done_callback(lambda future: future.result())
    return future


class BumpContainer:
    def __init__(self, export_path,
                 bump_at_container_awaken=False,
                 timeout=30,
                 loop=asyncio.get_event_loop(),
                 logger=init_logger()):
        self._loop = loop
        self._logger = logger
        self._export_path = os.path.normpath(export_path)
        self._bump_at_container_awaken = bump_at_container_awaken
        # self._debounce = DebounceFuture(loop)
        self._persistent_stat = {}
        self._timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
        return False

    def _cleanup(self):
        # self._debounce._cleanup()
        None

    def _bump_path(self, event):
        return os.path.join(
            self._export_path,
            event['Actor']['Attributes']['name']
        )

    def _clear_stat(self, key):
        # https://stackoverflow.com/questions/11277432/how-to-remove-a-key-from-a-python-dictionary
        self._persistent_stat.pop(key, None)

    async def bump(self, event):
        ret = {}
        key = event['Actor']['Attributes']['name'] + ':' + event['Directive']
        if key in self._persistent_stat:
            self._persistent_stat[key]['trigger']()
            ret = {'cancelled': key}
        else:
            self._persistent_stat[key] = {
                'trigger': debounce(
                    self._timeout,
                    functools.partial(self._clear_stat, key),
                    loop=self._loop
                )
            }
            self._persistent_stat[key]['trigger']()

            bump_path = self._bump_path(event)
            _debug = {}
            if event['Directive'] == 'add':
                if self._bump_at_container_awaken:
                    _debug = await self._add_path_to_container(bump_path)
                    ret['_debug'] = _debug
                else:
                    ret = {'skipped': key}
            else:
                _debug = await self._del_path_to_container(bump_path)
                ret['_debug'] = _debug
        return ret

    async def _add_path_to_container(self, bump_path):
        self._logger.info(
            'bump:start add path={path}'.format(path=bump_path)
        )
        ret = await _probe_path_to_container(self._loop, bump_path)
        self._logger.info(
            'bump:end add path={path}'.format(path=bump_path)
        )
        return ret

    async def _del_path_to_container(self, bump_path):
        self._logger.info(
            'bump:start del path={path}'.format(path=bump_path)
        )
        ret = await self._umount_container_name(bump_path)
        self._loop.call_later(
            3,
            functools.partial(_probe_path_to_container, self._loop, bump_path)
        )
        # TODO: await call_later
        self._logger.info(
            'bump:end del path={path}'.format(path=bump_path)
        )
        return ret

    async def _umount_container_name(self, bump_path):
        self._logger.debug(
            'umount:start path={path}'.format(path=bump_path)
        )
        proc = await asyncio.create_subprocess_exec(
            *['/bin/fusermount', '-u', bump_path],
            # *['/usr/bin/sleep', '10'],
            # *['echo', bump_path],
            loop=self._loop,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout_data = await proc.stdout.readline()
        stdout_line = stdout_data.decode('ascii').rstrip()
        stderr_data = await proc.stdout.readline()
        stderr_line = stderr_data.decode('ascii').rstrip()
        await proc.wait()
        self._logger.debug(
            'umount:end path={path}'.format(path=bump_path)
        )
        return {
            'stdout': stdout_line,
            'stdoerr': stderr_line
        }


class AsyncDirector:
    def __init__(self, client, loop=asyncio.get_event_loop(),
                 logger=init_logger(),
                 *args, **kwargs):
        self._client = client
        self._events = self._client.events(
            filters=self._event_filters,
            decode=True
        )
        # self._executor = ThreadPoolExecutor(max_workers=1)
        self._loop = loop
        self._logger = logger

    _up_actions = ['start', 'unpause']
    _down_actions = ['stop', 'pause', 'die', 'kill']
    _event_filters = {
        "event": _up_actions + _down_actions,
        "type": [
            "container"
        ]
    }

    async def __aiter__(self):
        return self

    async def __anext__(self):
        event = await self._loop.run_in_executor(
            None,  # self._executor,
            self._next_event
        )
        self._logger.debug('raw event: ' + str(event))

        action = event['Action']
        # name = event['Actor']['Attributes']['name']

        ret = {
            'Directive': '',
            'Actor': event['Actor']
        }
        if action in self._up_actions:
            ret['Directive'] = 'add'
        elif action in self._down_actions:
            ret['Directive'] = 'remove'

        return ret

    def _next_event(self):
        try:
            return next(self._events)
        except StopIteration:
            raise StopAsyncIteration


async def async_loop(loop,
                     containers_path,
                     bump_at_container_awaken,
                     logger=init_logger()):
    ai = AsyncDirector(
        docker.from_env(),
    )
    bump = BumpContainer(
        containers_path,
        bump_at_container_awaken,
        timeout=30,
        loop=loop,
        logger=logger
    )

    def cb(event, future):
        logger.info(
            'event:end directive={directive}, name={name}'.format(
                directive=event['Directive'],
                name=event['Actor']['Attributes']['name']
            )
        )
        logger.debug(
            'event:result directive={directive},'
            'name={name} result={result}'.format(
                directive=event['Directive'],
                name=event['Actor']['Attributes']['name'],
                result=str(future.result())
            )
        )

    async for event in ai:
        logger.info(
            'event:start directive={directive}, name={name}'.format(
                directive=event['Directive'],
                name=event['Actor']['Attributes']['name']
            )
        )
        task = loop.create_task(bump.bump(event))
        task.add_done_callback(functools.partial(cb, event))


async def async_loop_multi():
    i = 0
    while True:
        print(i)
        i = i + 1
        await asyncio.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        description='Bump container to autofs to mount/umount by xrosfs'
    )
    parser.add_argument('-b', '--bump-at-container-awakens',
                        type=strtobool,
                        default=0,
                        metavar='',
                        help='auto mount at the container wakens')
    parser.add_argument('-c', '--containers',
                        metavar='containers path',
                        default='/containers',
                        help='containers path')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help='be verbose')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        default=False,
                        help='log debuging info')
    parser.add_argument('-t', '--timestamp',
                        action='store_true',
                        default=False,
                        help='render timestamp in log record')
    args = parser.parse_args(sys.argv[1:])

    logger = init_logger(
        timestamp=args.timestamp,
        debug=args.debug,
        verbose=args.verbose
    )

    containers_path = args.containers
    logger.info('start: containers_path={containers_path}'.format(
        containers_path=containers_path
    ))
    bump_at_container_awaken = args.bump_at_container_awaken == 1
    if bump_at_container_awaken:
        logger.info('start: bump at container awkens = enabled')
    loop = asyncio.get_event_loop()
    wait = asyncio.wait([
        async_loop(
            loop,
            containers_path,
            bump_at_container_awaken,
            logger=logger
        )
    ])
    # future = asyncio.Future()
    loop.run_until_complete(wait)
    loop.close()
    logger.info('close:')


if __name__ == '__main__':
    main()
