# はじめに

AWS Opensearch をローカル環境で使えるよう設定します。
Opensearch を起動するために Docker を使います。

---

現在あるプロジェクトでdynamoDBを使っています。
しかし、dynamoDBは検索が不得意（RDBのSQLのように複雑なクエリを実行することができない）なので、検索が得意なOpenSearchを導入します。

# 環境

macOS Catalina
Docker version 20.10.2
docker-compose version 1.29.2

（ Dockerの基礎学習は、下記がおすすめです。）
>Udemy　[米国AI開発者がゼロから教えるDocker講座](https://www.udemy.com/course/aidocker/)
ブログ　[かめさんブログ - Docker超入門①](https://datawokagaku.com/whatisdocker/)
Twitter　[かめさんツイッター](https://twitter.com/usdatascientist?s=21)

# Docker起動
参考：[OpenSearchをローカル環境でDockerを利用して構築する](https://dev.classmethod.jp/articles/how-to-build-opensearch-with-docker/)

## 1. プロジェクト内にDocker用ファイルを 2つ作成

```docker-compose.yml
version: '3'

services:
  opensearch-dashboards:
    image: opensearchproject/opensearch-dashboards:1.1.0
    container_name: opensearch-dashboards
    environment:
      OPENSEARCH_HOSTS: "https://opensearch:9200"
    ports:
      - 5601:5601
    links:
      - opensearch
    networks:
      - sandbox

  opensearch:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: opensearch
    environment:
      - cluster.name=docker-cluster
      - node.name=os-node
      - cluster.initial_master_nodes=os-node
      - bootstrap.memory_lock=true
      - http.host=0.0.0.0
      - transport.host=127.0.0.1
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - $PWD/.local/opensearch:/usr/share/opensearch/data
    ports:
      - 9200:9200
    networks:
      - sandbox

networks:
  sandbox:
```

```Dockerfile
FROM opensearchproject/opensearch:1.1.0
RUN /usr/share/opensearch/bin/opensearch-plugin install analysis-kuromoji
RUN /usr/share/opensearch/bin/opensearch-plugin install analysis-icu
```


## 2. Docker起動
Docker Desktopを立ち上げ、以下コマンド実行

```terminal
$ docker-compose up -d   #（buildされていなければbuild後に）コンテナ起動後、コンテナから出る
$ docker-compose ps   #コンテナのステータスを確認する
```

opensearchとopensearch-dashboardsのコンテナがUP状態のはず。



## 3. curl コマンドで Opensearch へアクセスする
参考：[Elasticsearchの個人的によく使うコマンド集](https://zatoima.github.io/aws-elasticsearch-commands-lists.html)

```terminal: インデックスの確認
$ curl -u admin:admin --insecure https://localhost:9200/_cat/indices?v
```

```terminal: インデックスの詳細確認
$ curl -u admin:admin --insecure https://localhost:9200/インデックス名/_settings?pretty
```

```terminal: エイリアスの確認
$ curl -u admin:admin --insecure https://localhost:9200/_aliases?pretty
```

```terminal: インデックスの作成
$ curl -X PUT -u admin:admin --insecure https://localhost:9200/インデックス名
```

```terminal: インデックスの削除
$ curl -X DELETE -u admin:admin --insecure https://localhost:9200/インデックス名?pretty=true
```

```terminal: 件数確認
$ curl -u admin:admin --insecure https://localhost:9200/_cat/count/インデックス名?v
$ curl -u admin:admin --insecure https://localhost:9200/インデックス名/_count?pretty

```

```terminal: データ検索（無条件）
$ curl -u admin:admin --insecure https://localhost:9200/インデックス名/_search?pretty
```

```terminal: 統計情報
$ curl -u admin:admin --insecure https://localhost:9200/インデックス名/_stats?pretty
```

# さいごに

Opensearchをlocalで試したい、、さっそく出来ちゃいました！（Docker便利！）
ここからは、実際にドキュメントを作成したり、クエリ叩いたりしてみます。

今後、追記予定です。
