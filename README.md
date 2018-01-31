# XrosFS

Mount a Running Docker Container File Sytem via FUSE.

* No requirement to install additional agents to container side. it's only required to have permitted to `docker exec` command.
* Docker container [xros-over-sshfs](https://hub.docker.com/r/hankei6km/xros-over-sshfs/) that mount other containers file system automatically  by XrosFS with autofs and sshfs is released.


## Requirements

### Docker Host Side

* Python 3.5 or later
* FUSE 2.6 (or later)
* Permitted to execute `$ docker exec`

### Docker Container Side

* Shell (`ash` or `bash`) and some commands(`test`, `stat`, `dd` `base64` etc.)
(Usually, they are already installed plain image of alpine, debian etc.)


## Installation

```bash
pip install xrosfs
```

## Usage

Mount `/` of `container1` to `~/mnt`.

```bash
$ xrosfs container1:/ ~/mnt
```

In above step, xrosfs connect to `container1` as `root` user.
Pass `user@container1:/` to xrosfs, if you want to connect as other users.


## Known Issues

* Bad response time in operates.
* Some operations methods are not full implemented yet(`flush(fsync)` `utimens` etc.).


## License

Copyright (c) 2018 hankei6km

Licensed under the MIT License. See LICENSE.txt in the project root.
