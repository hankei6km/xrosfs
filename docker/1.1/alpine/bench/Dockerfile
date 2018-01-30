FROM alpine
# test bench image(sshfs server)
ENV LANG C.UTF-8

ARG USER=pdu

# Install and setup sshd.
# https://hub.docker.com/r/ncc0706/alpine-sshd/~/dockerfile/
RUN apk update && apk upgrade \
    && apk add --no-cache --virtual .fetch-deps \
                openssh-server \
                openssh-sftp-server \
                supervisor \
    && mkdir -p /var/logs/supervisor \
    && mkdir -p /var/run/supervisor \
    && rm -rf /var/cache/apk/* /tmp/*

# RUN mkdir /var/run/sshd
# No generate hostkey in image.
# RUN ssh-keygen -A

RUN echo 'root:root' |chpasswd

# `PermitRootLogin` line comment outed of debian strech.
RUN sed -ri 's/^#PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config

EXPOSE 22

# Add test data owner
RUN adduser -D -G users -u 1000 ${USER} -s /bin/ash

RUN echo "${USER}"':passwordpassword' |chpasswd

# Prepare bench test directory and change owner
RUN mkdir -p /export/sshfs && \
    mkdir -p /export/xrosfs && \
    chown ${USER} /export && \
    chown ${USER} /export/sshfs && \
    chown ${USER} /export/xrosfs

# Prepare bench test data
USER ${USER}

RUN echo 'hello sshfs' > /export/sshfs/hello.txt && \
    echo 'hello xrosfs' > /export/xrosfs/hello.txt

COPY setup-bench-basic-data.sh /tmp/
RUN sh /tmp/setup-bench-basic-data.sh

COPY setup-bench-useruri-data.sh /tmp/
RUN sh /tmp/setup-bench-useruri-data.sh

USER root

COPY setup-bench-relpath-data.sh /tmp/
RUN sh /tmp/setup-bench-relpath-data.sh

COPY start.sh /tmp/

CMD ["sh", "/tmp/start.sh"]
