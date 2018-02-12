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
