# Docker入門ガイド

## はじめに
Dockerはコンテナ仮想化ソフトウェアの一つであり、ソフトウェアをパッケージ化して実行するためのプラットフォームです。エンジニアにとっては、Dockerを使うことで環境の構築やアプリケーションのデプロイが簡単になります。この記事では、Dockerの基本的な使い方を紹介します。

## Dockerとは
Dockerは、Linuxコンテナを使ってアプリケーションとその依存関係をカプセル化するツールです。Dockerを使用することで、アプリケーションをコンテナにパッケージ化し、異なる環境やマシンでも動作させることができます。

## Dockerの基本コマンド
Dockerを使うためには、いくつかの基本コマンドを覚えておく必要があります。以下は、よく使われるDockerコマンドの一覧です。

- `docker pull`: Docker Hubからイメージを取得するコマンド
- `docker run`: Dockerイメージを実行するコマンド
- `docker ps`: 起動しているコンテナの一覧を表示するコマンド
- `docker exec`: 起動しているコンテナ内でコマンドを実行するコマンド
- `docker build`: Dockerイメージをビルドするコマンド

## Dockerの実践例
以下に、Dockerを使用した実践的な例を示します。

### MySQLのコンテナを起動する
```
docker run -it -d --name mysql_container -e MYSQL_ROOT_PASSWORD=password mysql:latest
```

このコマンドは、最新バージョンのMySQLイメージをダウンロードして、`mysql_container`という名前のコンテナを作成し、`password`というパスワードでMySQLを起動します。

### Node.jsアプリケーションをDockerでデプロイする
1. Node.jsアプリケーションのDockerfileを作成します。
```
FROM node:latest

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "index.js"]
```

2. Dockerイメージをビルドします。
```
docker build -t my-node-app .
```

3. Dockerコンテナを起動します。
```
docker run -d --name my-node-app -p 3000:3000 my-node-app
```

## まとめ
Dockerは、エンジニアにとって非常に便利なツールであり、環境の構築やアプリケーションのデプロイを簡単にすることができます。この記事では、Dockerの基本的な使い方や実践例を紹介しました。是非Dockerを活用して、開発効率を向上させてください。