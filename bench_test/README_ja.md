# Bench Test

sshfs と xrofs でマウントしたファイルシステム上で実際のファイル操作(`read`
`write` 等)を実行し、その結果を比較することでテストを実施.


## テスト環境の準備

sshfs と xrosfs の接続先サーバーは Docker コンテナとして実行されるため、
後述の `bootstrap.sh ` が Docker コンテナの起動等を行える環境が必要となる.

また、sshfs と xrosfs 実行環境が必要となるため、それぞれを事前にインストール.
(xrosfs ライブラリは `bootstrap.sh` 内からインストールされるが、FUSE 関連は手動でインストールする必要がある)


## テストの実行

通常のベンチテストを実行する場合は、プロジェクト内の `/bench_test` ディレクトリで以下のコマンドを実行.

```
# ./bootstrap.sh
```

pytest のオプションを指定.

```
# ./bootstrap.sh --pytest-opts '-x'
```

mount オプションを指定.
```
# XROSFS_BENCH_XROSFS_MOUNT_OPTS="-o umask=0002" XROSFS_BENCH_SSHFS_MOUNT_OPTS="-o umask=0002" ./bootstrap.sh
```

コンテナのイメージを指定.

```
# ./bootstrap.sh hankei6km/xrosfs-bench:0.1.0-centos
```

指定可能なイメージは
[hankei6km/xrosfs-bench Tags](https://hub.docker.com/r/hankei6km/xrosfs-bench/tags/)
から確認できる.


## その他

* 現在のバージョンでは、busybox(alpine 等) を元にしたイメージで実行するとテストは失敗する.
* 接続先サーバーのコンテナ起動用に pull されたイメージは手動で削除する必要がある.
* travis-ci 上では sshfs のリネーム処理において、権限関連のエラーが発生する(`mv path/to/foo/file /path/to/bar/file` のような処理でエラーとなる).
暫定的に、環境変数 `XROSFS_BENCH_AVOID_RNAME_DIR=1` をセットしてから実行すると回避するようになっている.
