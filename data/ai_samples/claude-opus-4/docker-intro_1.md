# Docker入門ガイド：コンテナ技術で開発環境を革新する

## はじめに

Dockerは、アプリケーションをコンテナと呼ばれる軽量な実行環境にパッケージ化する技術です。「開発環境では動いたのに、本番環境では動かない」という問題を解決し、開発・デプロイの効率を大幅に向上させます。

本記事では、Dockerの基本概念から実際の使い方まで、初心者エンジニアの方にも分かりやすく解説します。

## Dockerとは何か？

Dockerは、コンテナ型仮想化技術を提供するプラットフォームです。従来の仮想マシン（VM）と比較して、以下のような特徴があります：

- **軽量性**: OSカーネルを共有するため、起動が高速でリソース消費が少ない
- **可搬性**: 「どこでも同じように動く」環境を実現
- **再現性**: 同じDockerイメージから同一の実行環境を何度でも作成可能

## 主要な概念

### 1. イメージ（Image）
アプリケーションの実行に必要なすべてのファイルとメタデータを含む、読み取り専用のテンプレートです。

### 2. コンテナ（Container）
イメージから作成される実行可能なインスタンスです。独立した環境で動作し、必要に応じて起動・停止できます。

### 3. Dockerfile
イメージをビルドするための設定ファイルです。ベースイメージの指定や、実行するコマンドを記述します。

### 4. Docker Hub
Dockerイメージを共有するためのクラウドベースのレジストリサービスです。

## インストールと初期設定

### macOSの場合
```bash
# Docker Desktop for Macをダウンロード
# https://www.docker.com/products/docker-desktop

# インストール後、バージョン確認
docker --version
```

### Ubuntuの場合
```bash
# リポジトリの更新
sudo apt update

# 必要なパッケージのインストール
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# Docker公式GPGキーの追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Dockerリポジトリの追加
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Dockerのインストール
sudo apt update
sudo apt install docker-ce
```

## 基本的な使い方

### Hello Worldを実行
```bash
docker run hello-world
```

### Nginxコンテナの起動
```bash
# Nginxイメージをダウンロードして起動
docker run -d -p 8080:80 --name my-nginx nginx

# コンテナの状態確認
docker ps

# ブラウザでhttp://localhost:8080にアクセス
```

### よく使うコマンド
```bash
# イメージ一覧
docker images

# コンテナ一覧（実行中）
docker ps

# コンテナ一覧（すべて）
docker ps -a

# コンテナの停止
docker stop <container-id>

# コンテナの削除
docker rm <container-id>

# イメージの削除
docker rmi <image-id>
```

## Dockerfileを使ったイメージの作成

簡単なNode.jsアプリケーションを例に、Dockerfileの書き方を説明します。

```dockerfile
# ベースイメージの指定
FROM node:14-alpine

# 作業ディレクトリの設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# アプリケーションコードをコピー
COPY . .

# ポートの公開
EXPOSE 3000

# アプリケーションの起動
CMD ["node", "app.js"]
```

### イメージのビルドと実行
```bash
# イメージのビルド
docker build -t my-node-app .

# コンテナの実行
docker run -p 3000:3000 my-node-app
```

## Docker Composeによる複数コンテナの管理

複数のサービスを連携させる場合は、Docker Composeが便利です。

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgres://user:password@db:5432/mydb

  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Docker Composeの実行
```bash
# サービスの起動
docker-compose up -d

# ログの確認
docker-compose logs -f

# サービスの停止
docker-compose down
```

## ベストプラクティス

1. **軽量なベースイメージを使用**: Alpine Linuxベースのイメージを選ぶ
2. **レイヤーを最小限に**: RUN命令をまとめて実行
3. **.dockerignoreファイルの活用**: 不要なファイルをコンテナに含めない
4. **マルチステージビルド**: 最終イメージのサイズを削減
5. **非rootユーザーで実行**: セキュリティの向上

## まとめ

Dockerは現代の開発において欠かせないツールとなっています。本記事で紹介した基本的な使い方をマスターすれば、開発環境の構築や共有が格段に楽になります。

次のステップとして、以下のトピックについて学習することをお勧めします：
- Kubernetesによるコンテナオーケストレーション
- CI/CDパイプラインへのDockerの組み込み
- セキュリティベストプラクティス

Dockerを活用して、より効率的な開発環境を構築していきましょう！

## 参考資料

- [Docker公式ドキュメント](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)