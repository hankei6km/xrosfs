# 各種 Docker コンテナ用イメージ作成

開発環境、テスト用等のコンテナに利用するイメージの作成.


## ディレクトリ構成

基本構成として `Version/Variant(Distro)` の下に用途別のディレクトリが配置される.

用途別のディレクトリ.
* base: xrosfs を実行するための最低限の環境(現在は dev 用の元にしているだけで、単独で利用することはない).
* dev: 上記の base に開発環境(エディタ、IDE、リンター、ユニットテスト等)を追加.
* bench: ベンチテスト用(詳細はプロジェクト内の `bench_test` ディレクトリを参照).
* xros-over-sshfs: xros-over with sshfs の実行環境.
* xros-over-samba: xros-over with samba の実行環境.


## イメージ作成スクリプト

* build-imgs.sh: base と dev イメージを作成.
* build-bench-img.sh: bench イメージを作成.
* build-xros-over-sshfs.sh: xros-over-sshfs イメージを作成.
* build-xros-over-samba.sh: xros-over-samba イメージを作成.

例

base と dev イメージ作成.
`xrosfs:1.1-stretch-slim` と `xrosfs-dev:1.1-stretch-slim` が作成される.

```bash
# ./build-imgs.sh xrosfs 1.1/stretch-slim/
```

`docker build` へシェル変数経由でオプションを渡す
(利用できるシェル変数については、各スクリプトのソースを参照).

```bash
# XROSFS_DOCKER_BUILD_DEV_OPTS="--no-cache" ./build-imgs.sh xrosfs 1.1/stretch-slim/
```


## その他

Debian stretch slim を元にしたイメージのみ、各用途用の `Dockerfile` を用意してある.  Alpine と CentOS を元にしたイメージは bench のみ用意してある.

なお、Alpine 上の Python で fusepy を実行する方法が不明ため、現状では Alpine ベースで xrosfs を実行するイメージを作成することは難しい.

