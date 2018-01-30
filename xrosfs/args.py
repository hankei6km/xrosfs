# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import sys
import os
import configparser
import pkg_resources
import argparse
import shlex
# from urllib.parse import urlparse
# import re

metadata = {
    'name': 'xrosfs',
    'description': 'Mount a Running Docker Container File Sytem via FUSE',
    'version': ''
}

try:
    script_path = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(script_path), 'setup.cfg'))
    metadata['version'] = config['metadata']['version']
except KeyError:
    None

try:
    metadata['version'] = pkg_resources.get_distribution(
        metadata['name']
    ).version
except pkg_resources.DistributionNotFound:
    None

acceptable_mount_opts = ['allow_other', 'default_permissions', 'debug']


# https://stackoverflow.com/questions/41008269/python-argparse-assertionerror-from-metavar-userhostfile
class UsageFormatterTarget(argparse.HelpFormatter):
    def _format_usage(self, usage, actions, groups, prefix):
        result = super(UsageFormatterTarget, self)._format_usage(
            usage, actions, groups, prefix)
        return result.format(target='[user@]container:[dir]')


parser = argparse.ArgumentParser(prog=metadata['name'],
                                 description=metadata['description'],
                                 formatter_class=UsageFormatterTarget)

parser.add_argument('--version',
                    action='version',
                    version='%(prog)s version ' + metadata['version'])

parser.add_argument('-f',
                    dest='foreground',
                    action='store_true',
                    help='foreground operation')

parser.add_argument('-d',
                    dest='debug',
                    action='store_true',
                    help='enable debug output (implies -f)')

parser.add_argument('-o', '--opts',
                    dest='mount_opts',
                    metavar='opts',
                    action='append',
                    default=[],
                    help='mount options'
                    '(the only effective options is'
                    ' `{}` in present version)'.format(
                        ','.join(acceptable_mount_opts)
                    ))

parser.add_argument('target',
                    type=str,
                    # nargs=1,
                    # metavar='[user@]container:[dir]'
                    metavar='{target}'
                    )

parser.add_argument('mountpoint',
                    type=str)


class ArgsResult():
    __slots__ = [
        'foreground',
        'debug',
        'mount_opts',

        'user',
        'container',
        'server_path',
        'mountpoint'
    ]

    def __init__(self, foreground, debug, mount_opts,
                 user, container, server_path, mountpoint):
        self.foreground = foreground
        self.debug = debug
        self.mount_opts = mount_opts

        self.user = user
        self.container = container
        self.server_path = server_path
        self.mountpoint = mountpoint


def split_target(target):
    t = target.split('@', 1)
    if len(t) > 1:
        user = t[0]
        u = user.split(':', 1)
        if len(u) > 1:
            sys.exit('Password is not supported: ' + user)
        device = t[1]
    else:
        user = ''
        device = t[0]

    t = device.split(':')
    if len(t) == 2:
        container = t[0]
        server_path = t[1]
    else:
        sys.exit('Invalid format(bottom of container is not \':\'): ' + target)

    return (user, container, server_path)


def parse_opts(opts):
    ret = {}
    lexer = shlex.shlex(','.join(opts))
    lexer.whitespace = ','
    lexer.whitespace_split = True
    for o in lexer:
        kv = o.split('=', 1)
        k = kv[0]
        if k in acceptable_mount_opts:
            if len(kv) > 1:
                v = (kv[1])
                lv = v.lower()
                if lv == 'true':
                    v = True
                elif lv == 'false':
                    v = False
            else:
                v = True
            ret[k] = v
    return ret


def parse(argv):
    args = parser.parse_args(argv)

    # split target to "[user]" "container" "/path/to".
    user, container, server_path = split_target(args.target)

    # build opts dict(ie. `{'allow_other: True}`)
    mount_opts = parse_opts(args.mount_opts)

    # set debgu option by '-d'.
    if args.debug:
        mount_opts['debug'] = True

    return ArgsResult(
        foreground=args.foreground,
        debug=args.debug,
        mount_opts=mount_opts,
        user=user,
        container=container,
        server_path=server_path,
        mountpoint=args.mountpoint
    )


if __name__ == '__main__':  # pragma: no cover.
    mount_args = parse(sys.argv[1:])

    print('foreground: ' + str(mount_args.foreground))
    print('mount_opts: ' + str(mount_args.mount_opts))

    print('user: ' + mount_args.user)
    print('container: ' + mount_args.container)
    print('server_path: ' + mount_args.server_path)
    print('mountpoint: ' + mount_args.mountpoint)
