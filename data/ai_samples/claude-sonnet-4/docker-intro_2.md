# Docker入門ガイド：コンテナ技術の基礎から実践まで

## はじめに

Dockerは、アプリケーションの開発、配布、実行を効率化するコンテナ技術のデファクトスタンダードです。「開発環境では動いたのに本番環境で動かない」といった問題を解決し、一貫性のある環境を提供します。本記事では、Dockerの基本概念から実際の使い方まで、初心者向けに分かりやすく解説します。

## Dockerとは

Dockerは、アプリケーションとその依存関係を軽量なコンテナにパッケージ化する技術です。従来の仮想マシンとは異なり、ホストOSのカーネルを共有するため、高速起動と低リソース消費を実現します。

### 主なメリット

- **環境の一貫性**: 開発、テスト、本番環境で同一の実行環境を保証
- **ポータビリティ**: どこでも同じように動作する
- **軽量性**: 仮想マシンと比較して高速起動・低メモリ消費
- **スケーラビリティ**: 容易な水平スケーリング

## 基本概念

### イメージとコンテナ

- **イメージ**: アプリケーションの実行に必要なファイルシステムのスナップショット
- **コンテナ**: イメージから作成される実行可能なインスタンス

```bash
# イメージの一覧表示
docker images

# コンテナの一覧表示
docker ps -a
```

### Dockerfile

Dockerイメージをコードとして定義するファイルです。

```dockerfile
# ベースイメージを指定
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# package.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci --only=production

# アプリケーションコードをコピー
COPY . .

# ポートを公開
EXPOSE 3000

# アプリケーションを起動
CMD ["npm", "start"]
```

## Dockerのインストール

### Windows/Mac
Docker Desktopを公式サイトからダウンロードしてインストールします。

### Linux (Ubuntu)
```bash
# 古いバージョンを削除
sudo apt-get remove docker docker-engine docker.io containerd runc

# リポジトリを設定
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# GPGキーを追加
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# リポジトリを追加
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Dockerをインストール
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

## 基本的な使い方

### コンテナの起動

```bash
# Hello Worldを実行
docker run hello-world

# インタラクティブモードでUbuntuを起動
docker run -it ubuntu:20.04 /bin/bash

# バックグラウンドでNginxを起動
docker run -d -p 8080:80 nginx
```

### よく使うコマンド

```bash
# イメージをプル
docker pull ubuntu:20.04

# コンテナを停止
docker stop <container_id>

# コンテナを削除
docker rm <container_id>

# イメージを削除
docker rmi <image_id>

# ログを確認
docker logs <container_id>

# コンテナに接続
docker exec -it <container_id> /bin/bash
```

## 実践例：Node.jsアプリケーションのコンテナ化

### 1. アプリケーションの準備

```javascript
// app.js
const express = require('express');
const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello Docker!' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

```json
// package.json
{
  "name": "docker-demo",
  "version": "1.0.0",
  "description": "",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

### 2. Dockerファイルの作成

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

### 3. イメージのビルドと実行

```bash
# イメージをビルド
docker build -t my-node-app .

# コンテナを起動
docker run -p 3000:3000 my-node-app

# バックグラウンドで起動
docker run -d -p 3000:3000 --name my-app my-node-app
```

## Docker Compose

複数のコンテナを管理する場合は、Docker Composeを使用します。

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
    environment:
      - DB_HOST=db

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# サービスを起動
docker-compose up -d

# サービスを停止
docker-compose down
```

## まとめ

Dockerは現代的なアプリケーション開発において必須の技術です。本記事で紹介した基本概念と実践例を参考に、実際にプロジェクトでDockerを活用してみてください。コンテナ化により、より効率的で信頼性の高い開発ワークフローを構築できるでしょう。

次のステップとして、Kubernetes、CI/CDパイプライン、マルチステージビルドなど、より高度なトピックに挑戦することをお勧めします。