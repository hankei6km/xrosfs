# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 hankei6km
# Licensed under the MIT License. See LICENSE.txt in the project root.


def init_logger(
        name,
        add_handler=False,
        timestamp=False,
        debug=False,
        verbose=False
):
    from logging import getLogger, \
        StreamHandler, \
        Formatter, \
        DEBUG, \
        INFO, \
        WARNING

    logger = getLogger(name)

    if add_handler:
        logger.propagate = False

        level = WARNING
        if debug:
            level = DEBUG
        elif verbose:
            level = INFO

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
