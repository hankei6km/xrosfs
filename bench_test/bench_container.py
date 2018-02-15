# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import os
import re
# from subprocess import Popen
import shlex
import time
import docker


class BaseEnv:
    def __init__(self):
        self.client = docker.from_env()
        self.container_id = self.get_own_container_id()
        self.is_in_container = self.container_id != ''
        self.connected_netwrok = self.get_connected_network()

    def get_own_container_id(self):
        ret = ''

        try:
            with open('/proc/self/cgroup', 'r') as fd:
                rec = fd.readline()
                while len(rec) > 0 and ret == '':
                    fld = rec.split(':')
                    if len(fld) == 3:
                        container_id = fld[2].split('/')
                        if len(container_id) == 3 and \
                                container_id[1] == 'docker':
                            ret = container_id[2].rstrip()
                    rec = fd.readline()

        except BaseException:
            ret = ''

        return ret

    def get_connected_network(self):
        ret = ''

        if self.is_in_container:
            container_info = \
                self.client.api.inspect_container(self.container_id)
            networks = \
                tuple(container_info['NetworkSettings']['Networks'].keys())
            if len(networks) == 1:
                ret = networks[0]

        return ret


class Bench:
    def __init__(self, bench_container_image):
        self.bench_container_image = bench_container_image
        self.base_env = BaseEnv()
        self.network = self.base_env.connected_netwrok
        if self.network == '':
            # present environment is not in docker container.
            self.network = 'bridge'

        self.client = docker.from_env()
        self.bench_container = None
        self._running = False
        self.mountpoints = []

    sshfs_mount_retry_lim = 10
    sshfs_mount_retry_interval = 3
    sshfs_mount_opts_var_name = 'XROSFS_BENCH_SSHFS_MOUNT_OPTS'
    xrosfs_mount_retry_lim = 10
    xrosfs_mount_retry_interval = 3
    xrosfs_mount_opts_var_name = 'XROSFS_BENCH_XROSFS_MOUNT_OPTS'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.umount_all()
        self.stop()
        return False

    def get_container_ip_address(self):
        ret = ''

        container_info = self.client.api.inspect_container(self.container.id)
        ret = container_info[
            'NetworkSettings']['Networks'][self.network]['IPAddress']

        return ret

    def run(self):
        # self.network = network
        self.container = \
            self.client.containers.run(self.bench_container_image,
                                       privileged=True,
                                       name='xrosfs-bench',
                                       network=self.network,
                                       hostname='xrosfs-bench',
                                       remove=True,
                                       detach=True)

        # wait nfs ready to connect from client.
        # last_log = self.container.logs(tail=1)
        # while last_log != b'rpc.mountd: Version 1.3.3 starting\n':
        #     time.sleep(1)
        #     print('wait starting rpc.mountd..')
        #     # print(last_log)
        #     last_log = self.container.logs(tail=1)

    def stop(self):
        self.container.stop()

    def _get_mount_opts_from_env(self, var_name):
        ret = []
        if var_name in os.environ:
            opts = [
                re.sub('^ | $', '', i)
                for i in os.environ[var_name].split('-o') if i != ''
            ]
            for i in opts:
                ret.append('-o')
                ret.append(i)

        return ret

    def mount_sshfs(self, user, server_path, mountpoint, passwd=''):
        opts = [
            '-o',
            'StrictHostKeyChecking=no',
            '-o',
            'UserKnownHostsFile=/dev/null',
            '-o',
            'allow_other',
            '-o',
            'password_stdin'
        ] + self._get_mount_opts_from_env(self.sshfs_mount_opts_var_name)
        srv_ip = self.get_container_ip_address()
        echo_cmd = ['echo',
                    passwd] if passwd else []
        mnt_cmd = ['sshfs',
                   user + '@' + srv_ip + ':' + server_path,
                   mountpoint] + opts
        cmd = ' '.join([shlex.quote(i) for i in echo_cmd]) + \
            '|' + \
            ' '.join([shlex.quote(i) for i in mnt_cmd])

        retry_cnt = 0
        cmd_ret = os.system(cmd)
        while cmd_ret != 0 and retry_cnt < self.sshfs_mount_retry_lim:
            retry_cnt = retry_cnt + 1
            time.sleep(self.sshfs_mount_retry_interval)
            cmd_ret = os.system(cmd)
        self.mountpoints.append(mountpoint)

    def mount_xrosfs(self, user, server_path, mountpoint):
        tmp = [
            'python',
            '-m',
            'xrosfs',
            user + '@' + self.container.name + ':' + server_path,
            mountpoint
        ] + self._get_mount_opts_from_env(self.xrosfs_mount_opts_var_name)
        cmd = ' '.join([shlex.quote(i) for i in tmp])

        retry_cnt = 0
        cmd_ret = os.system(cmd)
        while cmd_ret != 0 and retry_cnt < self.xrosfs_mount_retry_lim:
            retry_cnt = retry_cnt + 1
            time.sleep(self.xrosfs_mount_retry_interval)
            cmd_ret = os.system(cmd)
        self.mountpoints.append(mountpoint)

    def umount_all(self):
        for i in self.mountpoints:
            tmp = ['fusermount',
                   '-u',
                   i]
            cmd = ' '.join([shlex.quote(i) for i in tmp])
            os.system(cmd)


if __name__ == '__main__':  # pragma: no cover.
    bench = Bench()
    bench.run()
    print(bench.get_container_ip_address())
    time.sleep(3)
    bench.mount_sshfs('./mnt/sshfs')
    bench.mount_xrosfs('./mnt/xrosfs')
    time.sleep(3)
    bench.umount_sshfs()
    bench.umount_xrosfs()
    bench.stop()
