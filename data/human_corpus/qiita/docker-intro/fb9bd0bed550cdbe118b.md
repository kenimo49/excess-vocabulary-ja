![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/527226/f666381a-63ce-ecbc-132a-36a32c8868e3.png)
# はじめに

LocalStack であれば、 AWS のリソースの動作をローカルマシンでテストすることができる、ということを聞き、入門してみました。

https://localstack.cloud/

やってみることとしては、LocalStack を Docker Compose で起動してみます。
docker-compose.yml について、Amazon DynamoDB を動作させるための設定をして、 LocalStack を起動した後、 AWS CLI を利用した操作を試せるようにします。 

## 環境

- MacBook Pro (Intel)、macOS Big Sur 11.6
- Docker Desktop 4.7.0
    - Docker Engine 20.10.14

## 構成図

簡単ですが、構成図です。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/527226/9a7b24f9-468e-a5fc-f5cf-de86e27de28c.png)

## 目次

1. [LocalStack の概要](#1-localstack-の概要)
1. [docker-compose.yml の作成](#2-docker-composeyml-の作成)
1. [LocalStack の起動](#3-localstack-の起動)

# 1. LocalStack の概要

LocalStack の概要を確認します。

## 1-1. LocalStack とは

LocalStack は、ノートパソコンや CI 環境上で動作する、クラウドサービスのエミュレータです。

https://localstack.cloud/

- LocalStack を使えば、リモートのクラウドプロバイダ（AWSなど）に接続することなく、 AWS アプリケーションをローカルマシンで実行できます。
- 使えるようになれば、テストや開発ワークフローのスピードアップと簡素化が期待できます。
- LocalStack でサポートしている AWS API（エミュレータとして利用できる AWS サービス）は、以下のページで確認できます。
    
https://docs.localstack.cloud/user-guide/aws/feature-coverage/
    
- 個人利用の場合、無料版（Community）と、有料版（Pro）があります。Pro は、 Community よりも利用できる AWS サービスが多いなど、多機能です。
    
    [](https://localstack.cloud/pricing/)
    

## 1-2. インストール方法の種類の確認

LocalStack の公式ドキュメントでは、提供されているインストール方法として、以下の 5 つが紹介されています。

- LocalStack CLI
- LocalStack Cockpit
- Docker
- **Docker-Compose**
- Helm

LocalStack CLI から始めるのが簡単でおすすめ、とドキュメント内では書いてあり、そちらでも実行してみましたが、今回の記事では、 **Docker-Compose** を選択しています。（ LocalStack CLI から始めたら、めっちゃ手こずりました。）

https://docs.localstack.cloud/getting-started/installation/#docker-compose

# 2. docker-compose.yml の作成

docker-compose.yml の作成して、その設定内容を説明します。

## 2-1. docker-compose.yml の作成

**docker-compose.yml** を作成します。（LocalStack は Docker コンテナで動作させるようです。）

```yaml:docker-compose.yml
version: '3.8'

services:
  localstack:
    container_name: "${LOCALSTACK_DOCKER_NAME-localstack_main}"
    image: localstack/localstack:latest
    ports:
      - 4566:4566
    environment:
      - SERVICES=dynamodb
      - PERSISTENCE=1
    volumes:
      - "${LOCALSTACK_VOLUME_DIR:-./volume}:/var/lib/localstack"
```

## 2-2. 設定内容の説明

### `container_name`

```yaml
    container_name: "${LOCALSTACK_DOCKER_NAME-localstack_main}"
```

- Docker コンテナ名を指定します。
- `localstack_main` 以外のコンテナ名にする場合、例えば下記のように **.env** ファイルに書き込みます。
    
    ```bash:.env
    LOCALSTACK_DOCKER_NAME=localstack_dynamodb
    ```
    

### `image`

```yaml
    image: localstack/localstack:latest
```

- Docker のベースイメージは、 **localstack/localstack** を使用します。
    - Docker Hub で確認してみます。
        
https://hub.docker.com/r/localstack/localstack
        

### `environment`

```yaml
    environment:
      - SERVICES=dynamodb
      - PERSISTENCE=1
```

- `SERVICES`
    - 起動する AWS CLI サービス名のカンマ区切りリストです。デフォルトでは、すべてのサービスがロードされ、そのサービスに対する最初のリクエストで開始されます。
    - 今回は `dynamodb` のみにしています。
- `PERSISTENCE`
    - 永続化を有効にします。 LocalStack ボリューム内の **state** ディレクトリに保存されます。永続化が無効である場合、Dockerコンテナの停止や削除をする際、データは保存されません。
- 一度書いたけど削除したもの
    - `DATA_DIR`
        
        ```yaml
              - DATA_DIR=/var/lib/localstack/data
        ```
        
        - このオプションは LocalStack v1 以降非推奨で、設定は無視され、 `PERSISTENCE=1` が設定されます。そのため、 `PERSISTENCE=1` に書き換えました。

### `volumes`

```yaml
volumes:
  - "${LOCALSTACK_VOLUME_DIR:-./volume}:/var/lib/localstack"
```

**LocalStack volume** が、ホストからコンテナの **/var/lib/localstack** にマウントされている必要があるため記述をします。

https://docs.localstack.cloud/references/filesystem/#localstack-volume

# 3. LocalStack の起動

LocalStack の起動させて、起動させると生成されるディレクトリとファイルの確認、イメージ生成時に、インストールのされている主要なツールの確認をします。

## 3-1. LocalStack の起動

Docker Desktop を起動してから、 **docker-compose.yml** のあるディレクトリで、下記コマンドを実行して、 LocalStack を起動します。

```bash
docker compose up -d
```

```bash:実行時ログ
# r_yamate @ mbp in ~/Documents/code/localstack_dynamodb [20:29:20]
$ docker compose up -d
[+] Running 2/2
 ⠿ Network localstack_dynamodb_default  Created                                                                                                                                                            0.2s
 ⠿ Container localstack_dynamodb        Started
```

Docker コンテナのステータスを確認します。

```bash
docker compose ps
```
 
```bash:実行時ログ
# r_yamate @ mbp in ~/Documents/code/localstack_dynamodb [20:30:38]
$ docker compose ps
NAME                  COMMAND                  SERVICE             STATUS              PORTS
localstack_dynamodb   "docker-entrypoint.sh"   localstack          running (healthy)   0.0.0.0:4566->4566/tcp
```
    

## 3-2. 生成されたディレクトリとファイルの確認

生成されたディレクトリとファイルを確認します。

```bash
# r_yamate @ mbp in ~/Documents/code/localstack_dynamodb [20:33:14]
$ tree
.
├── docker-compose.yml
└── volume
    ├── cache
    │   ├── machine.json
    │   ├── server.test.pem
    │   ├── server.test.pem.crt
    │   ├── server.test.pem.key
    │   └── service-catalog-1_2_1_dev-1_27_96.pickle
    ├── lib
    ├── logs
    │   ├── localstack_infra.err
    │   └── localstack_infra.log
    ├── state
    │   └── startup_info.json
    └── tmp

6 directories, 9 files
```

- **volume**
    - Docker 内の **/var/lib/localstack** にマウントされている LocalStack volume ディレクトリのルート
- **cache**
    - LocalStack の実行後も残ることが期待される一時的なデータ（LocalStackの起動時や停止時にはクリアされない）
- **lib**
    - 可変パッケージ (拡張機能や遅延ロードされたサードパーティ依存パッケージなど)
- **logs**
    - 最近実行された LocalStack のログ
- **state**
    - OpenSearch クラスタデータなど、永続化が有効なサービスの状態を保持します。
- **tmp**
    - LocalStack の実行に残らないと予想される一時的なデータ（ LocalStack の起動時または停止時にクリアされる場合があります。）

https://docs.localstack.cloud/references/filesystem/#localstack-volume-directory

## 3-3. インストールされている主要なツールの確認

ベースイメージ localstack/localstack からの生成時にインストールされている、主要なツールを確認します。

下記のコマンドで Docker コンテナ内に入ります。

```bash
docker compose exec localstack /bin/bash
```

```bash:実行時ログ
# r_yamate @ mbp in ~/Documents/code/localstack_dynamodb [20:33:52]
$ docker compose exec localstack /bin/bash
root@f57ea9691b28:/opt/code/localstack#
```

### Python

Python のバージョンを確認します。

```bash
python -V
```
    
```bash:実行時ログ
root@5c25a740554a:/opt/code/localstack# python -V
Python 3.10.8
```

### pip

pipは、 Python パッケージのインストールなどを行うユーティリティです。

https://www.python.jp/install/macos/pip.html

pip のバージョンを確認します。

```bash
pip -V
```
    
```bash:実行時ログ
root@f57ea9691b28:/opt/code/localstack# pip -V
pip 22.2.2 from /usr/local/lib/python3.10/site-packages/pip (python 3.10)
```

### AWS CLI

AWS CLI は、AWS サービスをコマンドラインから管理するツールです。

https://aws.amazon.com/jp/cli/

AWS CLI のバージョンを確認します。

```bash
aws --version
```
 
```bash:実行時ログ
root@f57ea9691b28:/opt/code/localstack# aws --version
aws-cli/1.27.9 Python/3.10.8 Linux/5.10.104-linuxkit botocore/1.29.9
```
    

AWS CLI が pip でインストールされているかを確認します。

```bash
pip list | grep aws
```

```bash:実行時ログ
root@f57ea9691b28:/opt/code/localstack# pip list | grep aws
awscli             1.27.9
awscli-local       0.20

[notice] A new release of pip available: 22.2.2 -> 22.3.1
[notice] To update, run: pip install --upgrade pip
```

### awscli-local

インストール済みのパッケージの詳細確認する `pip show` コマンドで、 `awscli-local` について確認します。

```bash
pip show awscli-local
```

```bash:実行時ログ
root@f57ea9691b28:/opt/code/localstack# pip show awscli-local
Name: awscli-local
Version: 0.20
Summary: Thin wrapper around the "aws" command line interface for use with LocalStack
Home-page: https://github.com/localstack/awscli-local
Author: LocalStack Team
Author-email: info@localstack.cloud
License: Apache License 2.0
Location: /usr/local/lib/python3.10/site-packages
Requires: localstack-client
Required-by:
```

https://github.com/localstack/awscli-local

GitHub の README にあるとおり、 `awslocal` コマンドを利用することによって、

次のコマンドの代わりに、

```bash
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

以下のように書くことができます。

```bash
awslocal dynamodb list-tables
```

```bash:実行時ログ
root@f57ea9691b28:/opt/code/localstack# awslocal dynamodb list-tables
{
    "TableNames": []
}
```

# おわりに

LocalStack を Docker Compose で起動してみました。

docker-compose.yml について、 AWS CLI を利用して、 Amazon DynamoDB を動作させるための設定をしたので、以下の記事で DynamoDB を操作します。

https://qiita.com/ryamate/items/b54b373897f07ee7ff25

ありがとうございました。

## 参考

https://localstack.cloud/

https://hub.docker.com/r/localstack/localstack

https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/Introduction.html

https://dk521123.hatenablog.com/entry/2020/12/16/211127

https://qiita.com/fujimo096/items/c890816dd395b76beae4

https://circleci.com/ja/blog/what-is-yaml-a-beginner-s-guide/
