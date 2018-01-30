ARG BASE_IMAGE=python:3-slim-stretch
FROM $BASE_IMAGE
ENV LANG C.UTF-8

ARG CONTAINERS_PATH=/containers
ARG ROOTPW=root
ARG XROS_USER=xrosfs
ARG XROS_USERPW=xrosfs
ENV CONTAINERS_PATH=${CONTAINERS_PATH}
ENV ROOTPW=${ROOTPW}
ENV XROS_USER=${XROS_USER}
ENV XROS_USERPW=${XROS_USERPW}
ENV BUMP_AT_CONTAINER_AWAKENS=0
ENV AUTOFS_TIMEOUT=300
ENV DOCKER_HOST=

# Temporary install xrosfs(Replatce regular setup code later)
COPY xrosfs-0.1.tar.gz /tmp/
RUN pip install /tmp/xrosfs-0.1.tar.gz
# Temporary install xros_over(Replatce regular setup code later)
COPY xros_over-0.1.tar.gz /tmp/
RUN pip install /tmp/xros_over-0.1.tar.gz

# Install and setup sshd.
# https://hub.docker.com/r/rastasheep/ubuntu-sshd/~/dockerfile/
# and autofs
# and fuse
# and supervisor
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
                autofs \
                fuse \
                openssh-server \
                supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install python modules.
# RUN pip install fusepy && \
#     pip install docker

RUN mkdir /var/run/sshd

# `PermitRootLogin` line comment outed of config in debian strech.
RUN sed -ri 's/^#PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

RUN rm /etc/ssh/ssh_host_*

EXPOSE 22

# Prepare mount point and export direcorty.
RUN mkdir -p ${CONTAINERS_PATH}

# Temporary setup autofs(Replatce regular setup code later)
RUN mkdir -p /etc/auto.master.d
RUN echo "${CONTAINERS_PATH}  program:/usr/local/bin/xros_map" > /etc/auto.master.d/xros-over.autofs
RUN sed -e 's/^\(+auto.master\)/# \1/' -i /etc/auto.master
# RUN sed -e "s/^#\/misc.\+$/\\${CONTAINERS_PATH}  program:\/opt\/xrosfs\/tools\/xros_map.py/" -i /etc/auto.master
# RUN echo '* -fstype=fuse,rw,allow_other :xrosfs\#root@&\:/' > /etc/auto.xrosover

# Temporary setup supervisor(Replatce regular setup code later)
COPY tmp/xros_over.conf /etc/supervisor/conf.d/
COPY tmp/event_listener.conf /etc/supervisor/conf.d/
COPY tmp/start.sh /tmp/start.sh
COPY tmp/xros_tldr /usr/local/bin/

# CMD ["/usr/sbin/sshd", "-D"]
# CMD ["/usr/bin/python2", "/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
CMD ["bash", "/tmp/start.sh"]
