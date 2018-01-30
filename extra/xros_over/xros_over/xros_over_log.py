# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.

import sys
import argparse


def init_tail_loggers(processnames):
    from logging import getLogger, StreamHandler, Formatter, INFO
    ret = {}

    ch = StreamHandler()
    ch.setLevel(INFO)
    formatter = Formatter('%(asctime)s %(name)s: %(message)s')
    ch.setFormatter(formatter)
    ch.terminator = ''

    for processname in processnames:
        logger = getLogger(processname)
        logger.setLevel(level=INFO)

        logger.addHandler(ch)  # Is it okay to recycle handler?
        ret[processname] = logger

    return ret


def write_stdout(s):
    # only eventlistener protocol messages may be sent to stdout
    sys.stdout.write(s)
    sys.stdout.flush()


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()


def handle_main(tail_loggers):
    while 1:
        # transition from ACKNOWLEDGED to READY
        write_stdout('READY\n')

        # read header line and print it to stderr
        line = sys.stdin.readline()
        # write_stderr(line)

        # read event payload and print it to stderr
        headers = dict([x.split(':') for x in line.split()])
        data = sys.stdin.read(int(headers['len']))

        data_lines = data.split('\n', 1)
        attrs = dict([x.split(':') for x in data_lines[0].split()])

        # timestamp = datetime.now().replace(microsecond=0).isoformat(' ')
        processname = attrs['processname']
        if processname in tail_loggers:
            tail_loggers[processname].info(data_lines[1])

        # transition from READY to ACKNOWLEDGED
        write_stdout('RESULT 2\nOK')


def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        description='Gather specificated process logs and output to stderr'
    )
    parser.add_argument('-p', '--processnames',
                        nargs='+',
                        # dest='processnames',
                        metavar='processnames',
                        default=[],
                        help='list of processname that gathering target')
    args = parser.parse_args(sys.argv[1:])
    handle_main(init_tail_loggers(args.processnames))


if __name__ == '__main__':
    main()
