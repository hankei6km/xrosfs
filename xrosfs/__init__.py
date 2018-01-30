# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import sys
import logging
import logging.config
from .xrosfs import XrosFS
from docker import errors


def main(argv=sys.argv[1:]):
    import os
    from fuse import FUSE
    from .args import parse
    from .conshell import ConShell
    from .cmdbuilder import CmdBuilder

    mount_args = parse(argv)

    if mount_args.mount_opts.get('debug', False):
        # enable to output debug message from fuse.
        # (and from some modules. ie. docker etc.)
        logging.basicConfig(level=logging.DEBUG)

    shell = ConShell(mount_args.user)
    try:

        shell.connect(mount_args.container)
        cmd_builder = CmdBuilder()
        avail_cmds = shell.setup_avail_cmds(
            cmd_builder.require_cmds
        )
        cmd_builder.set_avail_cmds(avail_cmds)

        # normalize server_path(blank / rel path)
        server_path = mount_args.server_path
        if os.path.isabs(mount_args.server_path) is False:
            res = shell.entry(cmd_builder._get_homedir(), quote=False)
            server_path = os.path.join(
                res.stdout.split('\n', 1)[0],
                mount_args.server_path
            )
        server_path = os.path.normpath(server_path)

        # build fsname str(ie 'root@xros-bench:path/to')
        fsname = (mount_args.user if mount_args.user != '' else '') + \
            mount_args.container + ':' + mount_args.server_path

        FUSE(XrosFS(shell, cmd_builder, server_path),
             mount_args.mountpoint,
             nothreads=True,
             foreground=mount_args.foreground,
             # https://github.com/terencehonles/fusepy/wiki/Sharing-fusepy-mount-via-Samba
             # allow_other=True,
             fsname=fsname,
             **mount_args.mount_opts
             )

    except errors.NotFound as exc:
        print('No such container: {}'.format(mount_args.container))
        sys.exit(1)


__all__ = ['XrosFS', 'main']
