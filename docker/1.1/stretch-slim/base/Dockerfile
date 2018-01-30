FROM debian:stretch-slim
# Build python environment from distro image.
# Couldn't install pdb-clone package in python official image
# (offical image removed `test` package that required `pdb-clone`). 

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
                fuse \
                python3 \
                python3-pip \
                python3-setuptools \
                python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/easy_install3 /usr/bin/easy_install
#RUN pip install -U pip

RUN pip install fusepy
RUN pip install docker

# Memo:
# 
# require options `--privileged` and
#  `-v /var/run/docker.sock:/var/run/docker.sock`
# at `docker run` to connect docker daemon and mount fuse-fs.
#
# ie.
# # docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock --privileged --name xrosfs IMAGE [(COMMAND)] [ARGS...]
