# Docker入門ガイド：初心者エンジニアのためのコンテナ化技術

## はじめに

現代のソフトウェア開発において、Dockerは欠かせない技術の一つとなっています。本記事では、Dockerの基本概念から実際の使い方まで、初心者エンジニア向けに分かりやすく解説します。

## Dockerとは何か？

Dockerは、アプリケーションとその依存関係を軽量なコンテナとしてパッケージ化する仮想化技術です。従来の仮想マシンとは異なり、ホストOSのカーネルを共有するため、リソース使用量が少なく、起動も高速です。

### 主な特徴

- **軽量性**: VMに比べて少ないリソースで動作
- **ポータビリティ**: 環境に依存せず、どこでも同じように動作
- **スケーラビリティ**: 簡単に複数のコンテナを起動・停止可能
- **分離性**: アプリケーション同士が互いに影響しない

## 基本概念の理解

### イメージ（Image）
アプリケーション実行に必要なファイルシステムのテンプレートです。読み取り専用で、複数のコンテナから共有できます。

### コンテナ（Container）
イメージから作成される実行可能なインスタンスです。アプリケーションが実際に動作する環境となります。

### Dockerfile
イメージを作成するための設計書です。ベースイメージから始まり、必要なソフトウェアのインストールや設定を記述します。

## Dockerのインストール

### Windows/Mac
Docker Desktopを公式サイトからダウンロードしてインストールします。

### Linux（Ubuntu例）
```bash
# 古いバージョンを削除
sudo apt-get remove docker docker-engine docker.io containerd runc

# 必要なパッケージをインストール
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Docker公式GPGキーを追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# リポジトリを追加
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Dockerをインストール
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

## 基本コマンド

### イメージ操作
```bash
# イメージ一覧表示
docker images

# イメージをプル（ダウンロード）
docker pull nginx:latest

# イメージを削除
docker rmi nginx:latest
```

### コンテナ操作
```bash
# コンテナ実行
docker run -d --name my-nginx -p 8080:80 nginx

# 実行中のコンテナ一覧
docker ps

# 全てのコンテナ一覧
docker ps -a

# コンテナに接続
docker exec -it my-nginx bash

# コンテナ停止
docker stop my-nginx

# コンテナ削除
docker rm my-nginx
```

## 実践例：Node.jsアプリケーションのコンテナ化

### 1. サンプルアプリケーションの作成

```javascript
// app.js
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello Docker World!');
});

app.listen(port, () => {
  console.log(`App running on port ${port}`);
});
```

```json
// package.json
{
  "name": "docker-node-app",
  "version": "1.0.0",
  "main": "app.js",
  "dependencies": {
    "express": "^4.18.0"
  },
  "scripts": {
    "start": "node app.js"
  }
}
```

### 2. Dockerfileの作成

```dockerfile
# ベースイメージを指定
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# package.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install

# アプリケーションコードをコピー
COPY . .

# ポート3000を公開
EXPOSE 3000

# アプリケーションを起動
CMD ["npm", "start"]
```

### 3. イメージのビルドと実行

```bash
# イメージをビルド
docker build -t my-node-app .

# コンテナを実行
docker run -d --name node-container -p 3000:3000 my-node-app

# ブラウザで http://localhost:3000 にアクセス
```

## Docker Composeの活用

複数のコンテナを管理する場合は、Docker Composeが便利です。

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
# 全てのサービスを起動
docker-compose up -d

# 停止
docker-compose down
```

## ベストプラクティス

### 1. .dockerignoreの活用
```
node_modules
npm-debug.log
.git
.gitignore
README.md
```

### 2. マルチステージビルド
```dockerfile
# ビルドステージ
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# 実行ステージ
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### 3. セキュリティ対策
- 不要な権限を与えない
- 軽量なベースイメージを使用
- 定期的なイメージ更新

## まとめ

Dockerは開発から本番環境まで一貫した環境を提供し、開発効率を大幅に向上させる強力なツールです。本記事で紹介した基本概念とコマンドをマスターすることで、モダンな開発ワークフローに参加できるようになります。

次のステップとして、Kubernetes、CI/CD パイプラインとの連携など、より高度な topics に挑戦してみてください。継続的な学習により、コンテナ技術の真価を発揮できるエンジニアになれるでしょう。