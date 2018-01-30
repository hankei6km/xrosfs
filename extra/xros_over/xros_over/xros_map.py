# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.


import os
import sys
import docker


def main():
    dir_name = sys.argv[1]

    # check container status.
    client = docker.from_env()
    is_running = False
    try:
        container = client.containers.get(dir_name)
        if container.status == 'running' and container.name == dir_name:
            is_running = True
    except docker.errors.NotFound:
        None

    if is_running:
        # Passed running container,
        # return record that mount container via xrosfs.
        print(
            '-fstype=fuse,rw,allow_other :xrosfs\#root@{}\:/'.
            format(container.name)
        )
    else:
        if dir_name in os.listdir(os.environ['CONTAINERS_PATH']):
            # Passed exist path but not container,
            # return record that always failed.
            print(
                '-fstype=fuse :false\#{}'.
                format(dir_name)
            )


if __name__ == '__main__':
    main()
