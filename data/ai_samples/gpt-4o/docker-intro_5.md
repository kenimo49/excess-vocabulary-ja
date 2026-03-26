# Docker入門ガイド

Dockerは、開発環境から本番環境まで一貫したコンテナ技術を提供することで、ソフトウェアの開発、テスト、デプロイを劇的に改善します。このブログ記事では、Dockerの基本概念、主要なコンポーネント、基本的な使い方などについて詳しく解説します。この記事を読むことで、Dockerの基本を理解し、開発環境に活用するための第一歩を踏み出せることでしょう。

## 1. Dockerとは？

Dockerは、コンテナと呼ばれる軽量な仮想化技術を提供するオープンソースプラットフォームです。コンテナは、アプリケーションとその依存関係をまとめて管理し、どの環境でも一貫して動作させることができます。これにより、「動作するはずなのに環境が違うから動かない」という問題を解消します。

## 2. Dockerの主要コンポーネント

Dockerは以下の主要なコンポーネントから構成されています：

- **Dockerイメージ**: アプリケーションとその依存関係をパッケージ化したものです。
- **Dockerコンテナ**: 実行可能なDockerイメージのインスタンスです。
- **Dockerファイル**: Dockerイメージを作成するためのレシピが書かれている設定ファイルです。
- **Docker Hub**: Dockerイメージを共有するためのレジストリサービスです。

## 3. Dockerのセットアップ

Dockerを始めるには、ローカルマシンにDockerをインストールする必要があります。以下は一般的なOSでのインストール手順です：

### Windows / Mac

1. [Docker Desktop](https://www.docker.com/products/docker-desktop)を公式サイトからダウンロードします。
2. インストーラーを実行して、画面の指示に従いインストールします。
3. インストール完了後、Docker Desktopを起動します。

### Linux

1. 使用しているディストリビューションのパッケージマネージャを利用し、Docker Engineをインストールします。
   ```bash
   # Ubuntuの場合
   sudo apt update
   sudo apt install docker.io
   ```
2. インストール後、Dockerサービスを起動します。
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

## 4. Dockerの基本操作

Dockerをインストールしたら、実際に使ってみましょう。以下のセクションでは、基本的なDockerの使い方を学びます。

### イメージの取得

DockerイメージはDocker Hubから取得できます。例えば、`hello-world`イメージを取得する場合は以下のコマンドを実行します：

```bash
docker pull hello-world
```

### コンテナの起動

取得したイメージからコンテナを起動します：

```bash
docker run hello-world
```

このコマンドを実行すると`hello-world`コンテナが起動し、メッセージが表示されます。

### コンテナの管理

- **実行中のコンテナを一覧表示**:
  ```bash
  docker ps
  ```

- **すべてのコンテナを一覧表示**:
  ```bash
  docker ps -a
  ```

- **コンテナを停止**:
  ```bash
  docker stop <container_id>
  ```

- **コンテナを削除**:
  ```bash
  docker rm <container_id>
  ```

## 5. Dockerファイルの作成

Dockerイメージをカスタマイズしたい場合は、`Dockerfile`を作成します。ここでは、シンプルなNode.jsアプリケーションのDockerfileを作成する例を示します。

根ディレクトリに以下の内容の`Dockerfile`を作成します：

```dockerfile
# ベースイメージ
FROM node:14

# 作業ディレクトリを設定
WORKDIR /usr/src/app

# パッケージをインストールしてアプリケーションをバンドル
COPY package*.json ./
RUN npm install

# アプリケーションのソースをバンドル
COPY . .

# アプリケーションをビルド
CMD ["node", "app.js"]

# コンテナがバインドするポートを公開
EXPOSE 8080
```

このDockerfileを使ってイメージをビルドします：

```bash
docker build -t my-node-app .
```

`my-node-app`という名前のDockerイメージが作成されます。

## 6. Docker Composeによる複数コンテナの管理

複数のコンテナを連携させてアプリケーションを構成する場合、Docker Composeが便利です。`docker-compose.yml`を作成することで、複数のコンテナをまとめて管理できます。

以下は`docker-compose.yml`の例です：

```yaml
version: '3'
services:
  web:
    image: my-node-app
    ports:
      - "8080:8080"
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: example
```

この設定ファイルを使って、以下のコマンドでサービスを起動します：

```bash
docker-compose up
```

以上で、複数のサービスが連携して起動します。

## まとめ

この記事では、Dockerの基本的なコンセプト、主要コンポーネント、セットアップ方法、基本的なコマンド、Dockerfileの作成、そしてDocker Composeを使った複数コンテナの管理方法を紹介しました。Dockerを活用することで、開発から本番環境へのデプロイまで、一貫した環境でアプリケーションを運用できます。このガイドを活用して、ぜひDockerを試してみてください。