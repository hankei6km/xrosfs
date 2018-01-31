# XrosFS

XrosFS は稼働中の Docker コンテナのファイルシステムを FUSE 経由でマウントするツールです.

* コンテナ側へ追加のエージェント等をインストールする必要あはりません. `docker exec` が許可されていていれば利用できます.
* XrosFS と autofs、sshfs を組み合わせることで、他のコンテナを自動マウントするコンテナ([xros-over-sshfs](https://hub.docker.com/r/hankei6km/xros-over-sshfs/))も用意してあります.


## Requirements

### Docker ホスト側
* Python 3.5 以上
* FUSE 2.6 (or later)
* docker exec を実行できる権限

### Docker コンテナ側
* シェル(`ash` or `bash`)と基本的なツール(`test`,`stat`,`dd`, `base64` etc.)
(基本的には、alpine debian centos のプレーンイメージにインストールされています)


## Installation

```bash
pip install xrosfs
```

## Usage

`container1` の `/` を `~/mnt` へマウントする.

```bash
$ xrosfs container1:/ ~/mnt
```
なお、上記の例では `container1` へ `root` として接続しています.
接続するユーザーを指定する場合は、`user@container1:/` と記述します.


## Known Issues

* 動作が超絶遅いです.
* いくつかの操作メソッドは完全には実装されていません(`flush(fsync)` `utimens` 等).


## License

Copyright (c) 2018 hankei6km

Licensed under the MIT License. See LICENSE.txt in the project root.
