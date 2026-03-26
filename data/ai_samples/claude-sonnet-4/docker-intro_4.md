# Docker入門ガイド：コンテナ技術で開発効率を劇的に向上させよう

## はじめに

現代のソフトウェア開発において、Docker は欠かせない技術の一つとなっています。「ローカル環境では動くのに、本番環境では動かない」という問題や、開発環境の構築に時間がかかる問題を解決する強力なツールです。

この記事では、Docker の基本概念から実践的な使用方法まで、エンジニアが知っておくべき要点をまとめて解説します。

## Dockerとは

Docker は、アプリケーションとその実行環境を「コンテナ」という軽量な仮想化技術で管理するプラットフォームです。従来の仮想マシンと比較して、以下の特徴があります：

- **軽量性**: OSカーネルを共有するため、リソース使用量が少ない
- **高速起動**: 数秒でコンテナを起動可能
- **ポータビリティ**: 環境依存を排除し、どこでも同じ動作を保証

## 基本概念の理解

### コンテナとイメージ

```
イメージ（Image）: アプリケーションの実行に必要なファイルシステムのスナップショット
コンテナ（Container）: イメージから作成された実行中のインスタンス
```

### Dockerfile

Dockerfile は、イメージを自動的に構築するための設計書です。以下は Node.js アプリケーションの例：

```dockerfile
# ベースイメージを指定
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# package.json をコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install

# アプリケーションコードをコピー
COPY . .

# ポートを公開
EXPOSE 3000

# アプリケーションを起動
CMD ["npm", "start"]
```

## 基本的なDockerコマンド

### イメージ操作

```bash
# イメージをダウンロード
docker pull nginx:latest

# ローカルのイメージ一覧を表示
docker images

# イメージをビルド
docker build -t myapp:1.0 .

# イメージを削除
docker rmi myapp:1.0
```

### コンテナ操作

```bash
# コンテナを起動
docker run -d -p 8080:80 --name webserver nginx

# 実行中のコンテナを表示
docker ps

# 全てのコンテナを表示（停止中も含む）
docker ps -a

# コンテナを停止
docker stop webserver

# コンテナを削除
docker rm webserver

# コンテナ内でコマンド実行
docker exec -it webserver /bin/bash
```

## Docker Compose の活用

複数のコンテナを組み合わせたアプリケーションの管理には、Docker Compose を使用します。

### docker-compose.yml の例

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=mongodb://db:27017/myapp

  db:
    image: mongo:5.0
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongodb_data:
```

### Docker Compose の基本コマンド

```bash
# サービスを起動
docker-compose up -d

# ログを確認
docker-compose logs

# サービスを停止・削除
docker-compose down

# 特定のサービスを再構築
docker-compose build web
```

## 実践的な開発フロー

### 1. 開発環境の構築

```bash
# プロジェクトディレクトリを作成
mkdir my-docker-project
cd my-docker-project

# Dockerfile と docker-compose.yml を作成
touch Dockerfile docker-compose.yml

# 開発環境を起動
docker-compose up -d
```

### 2. ボリュームマウントによるライブリロード

開発時にはソースコードの変更を即座に反映させたいため、ボリュームマウントを使用：

```yaml
services:
  web:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules  # node_modulesは除外
```

### 3. マルチステージビルド

本番用の軽量イメージを作成するためのベストプラクティス：

```dockerfile
# 開発・ビルド用ステージ
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 本番用ステージ
FROM node:18-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
CMD ["npm", "start"]
```

## ベストプラクティス

### 1. イメージサイズの最適化

- Alpine Linux ベースのイメージを使用
- 不要なファイルを `.dockerignore` で除外
- マルチステージビルドを活用

### 2. セキュリティの考慮

```dockerfile
# 非rootユーザーを作成
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# ユーザーを切り替え
USER nextjs
```

### 3. キャッシュの効果的な利用

依存関係のインストールとソースコードのコピーを分離：

```dockerfile
# 依存関係を先にコピー（変更頻度が低い）
COPY package*.json ./
RUN npm install

# ソースコードは後でコピー（変更頻度が高い）
COPY . .
```

## よくある問題と解決方法

### 1. ポートの競合

```bash
# 使用中のポートを確認
docker ps
lsof -i :3000

# 別のポートを使用
docker run -p 3001:3000 myapp
```

### 2. ボリュームのパーミッション問題

```dockerfile
# Dockerfile でユーザー ID を一致させる
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user
RUN useradd -u $USER_ID -g $GROUP_ID user
```

## まとめ

Docker は現代の開発において必須のスキルです。コンテナ技術を適切に活用することで：

- 環境の統一による「動作しない」問題の解決
- 開発環境構築の自動化・高速化
- マイクロサービスアーキテクチャの実現
- CI/CD パイプラインの効率化

が可能になります。

まずは簡単なアプリケーションから Docker 化を始めて、徐々に複雑な構成に挑戦していきましょう。継続的な学習と実践により、Docker の恩恵を最大限に活用できるようになります。

## 参考リンク

- [Docker 公式ドキュメント](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose 公式ガイド](https://docs.docker.com/compose/)