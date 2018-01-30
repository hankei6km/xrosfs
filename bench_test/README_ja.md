# Bench Test

sshfs と xrofs でマウントしたファイルシステム上で実際のファイル操作(`read`
`write` 等)を実行し、その結果を比較することでテストを実施.


## テスト環境の準備

ベンチテスト用の Docker コンテナが必要になるため、プロジェクト内の `/docker` ディレクトリで以下のコマンドを実行し、イメージを作成.

```bash
# ./build-bench-img.sh xrosfs-bench 1.1/stretch-slim
```

また、sshfs と xrosfs 実行環境が必要となるため、それぞれを事前にインストール.
(xrosfs ライブラリは `bootstrap.sh` 内からインストールされるが、FUSE 関連は手動でインストールする必要がある)



## テストを実行

通常のベンチテストを実行する場合は、プロジェクト内の `/bench_test` ディレクトリで以下のコマンドを実行.

```bash
# ./bootstrap.sh
```

pytest のオプションを指定.

```bash
# ./bootstrap.sh --pytest-opts '-x'
```

コンテナのイメージを指定(事前にイメージを作成しておく必要がある).

```bash
# ./bootstrap.sh xrosfs-bench:1.1-alpine
```

## その他

現在のバージョンでは、busybox(alpine 等) を元にしたイメージで実行するとテストは失敗する.
