# Docker入門ガイド：コンテナ技術の基礎から実践まで

## はじめに

近年、アプリケーション開発において**Docker**は欠かせない技術となっています。本記事では、Dockerの基本概念から実際の使い方まで、エンジニアの皆さんがすぐに実践できる内容をご紹介します。

## Dockerとは？

Dockerは、アプリケーションとその実行環境を「**コンテナ**」という単位でパッケージ化し、どこでも同じように動作させることができるプラットフォームです。

### 従来の課題
- 「開発環境では動くのに本番環境では動かない」
- 環境構築に時間がかかる
- チーム間で環境の差異が発生する

Dockerはこれらの課題を解決し、**"Build once, Run anywhere"** を実現します。

## Dockerの主要コンポーネント

### 1. **Dockerイメージ**
アプリケーションの実行に必要なすべての要素（コード、ランタイム、ライブラリ、設定など）を含むテンプレート

### 2. **Dockerコンテナ**
Dockerイメージから作成される実行可能なインスタンス

### 3. **Dockerfile**
Dockerイメージを作成するための設計書

### 4. **Docker Hub**
Dockerイメージを保存・共有するためのクラウドレジストリ

## 実践：Dockerを使ってみよう

### インストール

```bash
# macOS
brew install docker

# Ubuntu
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Windows
# Docker Desktop for Windowsをダウンロード
```

### 基本的なDockerコマンド

```bash
# Dockerのバージョン確認
docker --version

# イメージの取得
docker pull nginx:latest

# イメージ一覧の確認
docker images

# コンテナの起動
docker run -d -p 8080:80 --name my-nginx nginx

# 実行中のコンテナ確認
docker ps

# コンテナの停止
docker stop my-nginx

# コンテナの削除
docker rm my-nginx
```

### Dockerfileの作成

Node.jsアプリケーションを例に、Dockerfileを作成してみましょう。

```dockerfile
# ベースイメージの指定
FROM node:16-alpine

# 作業ディレクトリの設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# アプリケーションのソースコードをコピー
COPY . .

# アプリケーションが使用するポートを公開
EXPOSE 3000

# アプリケーションの起動コマンド
CMD ["node", "app.js"]
```

### イメージのビルドと実行

```bash
# イメージのビルド
docker build -t my-node-app .

# コンテナの実行
docker run -d -p 3000:3000 --name my-app my-node-app

# ログの確認
docker logs my-app
```

## Docker Composeで複数コンテナを管理

複数のサービス（Webアプリ、データベース、キャッシュなど）を連携させる場合は、**Docker Compose**が便利です。

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

```bash
# サービスの起動
docker-compose up -d

# サービスの停止
docker-compose down
```

## ベストプラクティス

### 1. **軽量なベースイメージを使用**
```dockerfile
# Good
FROM node:16-alpine

# Avoid
FROM ubuntu:20.04
RUN apt-get install nodejs
```

### 2. **レイヤーキャッシュを活用**
```dockerfile
# 変更頻度の低いものを先に
COPY package*.json ./
RUN npm install

# 変更頻度の高いものを後に
COPY . .
```

### 3. **マルチステージビルドの活用**
```dockerfile
# ビルドステージ
FROM node:16 AS builder
WORKDIR /app
COPY . .
RUN npm ci && npm run build

# 実行ステージ
FROM node:16-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
RUN npm ci --production
CMD ["node", "dist/index.js"]
```

## まとめ

Dockerは現代のアプリケーション開発において必須のツールとなっています。本記事で紹介した基本的な使い方を理解することで、以下のメリットを享受できます：

- 環境構築の時間短縮
- 本番環境との差異の解消
- チーム開発の効率化
- スケーラブルなアプリケーション構築

まずは小さなプロジェクトからDockerを導入し、徐々に活用範囲を広げていくことをおすすめします。

## 参考リンク

- [Docker公式ドキュメント](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

Happy Dockering! 🐳