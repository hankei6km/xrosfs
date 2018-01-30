ARG BASE_IMAGE
FROM $BASE_IMAGE

ARG USER=pdu

# Prepare to add vscode repository
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
                apt-transport-https \
                curl \
                gpg \
	&& rm -rf /var/lib/apt/lists/*

# Add vscode repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
RUN mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
RUN sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list'

# Install dev tools(editor, dvcs, etc) to global environment.
RUN apt-get update && apt-get install -y --no-install-recommends \
                bash-completion \
                cifs-utils \
                git \
		iputils-ping \
                netbase \
                pandoc \
                procps \
                sshfs \
                sudo \
                vim-nox

# Install vscode and depencies(to launch over vnc)
RUN apt-get install -y --no-install-recommends \
                code \
                libasound2 \
                libgtk2.0 \
                libx11-xcb1 \
                libxss1 \
                libxtst6 \
                python3-venv


RUN rm -rf /var/lib/apt/lists/*

# Install dev tools(linter, unit test, etc.) to python3 global environment
RUN pip3 install autopep8 \
    &&  pip3 install flake8 \
    && pip3 install jedi \
    && pip3 install pytest \
    && pip3 install pytest-asyncio \
    && pip3 install pytest-cov \
    && pip3 install pytest-runner \
    && pip3 install pytest-watch \
    && pip3 install pypandoc

# Set `user_allow_other` to fuse.conf
RUN echo 'user_allow_other' >> /etc/fuse.conf

# Add docker group(gid is same docker host) and add user(grant access docker daemon).
RUN groupadd -g 996 docker && useradd -d /home/${USER} -g users -G docker -u 1000 -m -s /bin/bash ${USER}

# Grant ${USER} to run mount/umount
# (need to mount nfs at bench test and chown).
# edit sudoers from scritp(https://stackoverflow.com/questions/323957/how-do-i-edit-etc-sudoers-from-a-script)
RUN echo 'Cmnd_Alias BENCH_UTIL = /bin/mount, /bin/umount\npdu     ALL=(ALL) NOPASSWD:BENCH_UTIL\n' | EDITOR="tee -a" visudo

WORKDIR /home/${USER}

# Prepare user's devlopment environment.
USER ${USER}

# Setup python3 environment for user(to use pyton3 in vscode)
RUN mkdir /home/${USER}/py3env \
    && python3 -m venv --system-site-packages /home/${USER}/py3env

# Setup vscode for user.
# Install extensionts.
RUN code --install-extension ms-python.python \
    && code --install-extension vscodevim.vim

# Setup vim for user.
COPY vimrc /home/${USER}/.vimrc
RUN mkdir /home/${USER}/.vim
RUN git clone https://github.com/VundleVim/Vundle.vim.git /home/${USER}/.vim/bundle/Vundle.vim
RUN vim +PluginInstall +qall
# RUN vim -S pyclewn-2.3.vmb -c ':quit'

# Setup mountpoint
RUN mkdir /home/${USER}/mnt

USER root

# Memo:
# 
# Mount xrosfs project directory to home directory on container
# in development phase.
#
# ie.
# $ cd path/to/xrosfs
# # docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock --privileged -v ${PWD}:/home/pdu/python -u pdu --name xrosfs-dev IMAGE [(COMMAND)] [ARGS...]
