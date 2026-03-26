# Docker入門ガイド：コンテナ技術の基礎から実践まで

## はじめに

現代のソフトウェア開発において、Dockerは欠かせない技術の一つとなりました。「動作環境が違うから動かない」「本番環境で謎のエラーが発生する」といった問題を解決し、開発効率を大幅に向上させるコンテナ技術について、基礎から実践まで解説します。

## Dockerとは？

Dockerは、アプリケーションとその実行環境を軽量なコンテナという単位でパッケージ化し、どこでも同じように実行できるプラットフォームです。

### 従来の仮想化との違い

```
従来の仮想化（VM）
┌─────────────────┐
│   アプリケーション   │
├─────────────────┤
│      OS         │
├─────────────────┤
│   ハイパーバイザー   │
├─────────────────┤
│    ホストOS      │
└─────────────────┘

Docker（コンテナ）
┌─────────────────┐
│   アプリケーション   │
├─────────────────┤
│ Dockerエンジン    │
├─────────────────┤
│    ホストOS      │
└─────────────────┘
```

Dockerコンテナは、ホストOSのカーネルを共有するため、仮想マシンと比較して軽量で高速に起動します。

## Dockerの主要概念

### イメージとコンテナ

- **イメージ**: アプリケーションの実行に必要なファイルシステムのスナップショット
- **コンテナ**: イメージから作成された実行可能なインスタンス

### Dockerfile

アプリケーション環境を定義するテキストファイルです。

```dockerfile
# ベースイメージを指定
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci --only=production

# アプリケーションファイルをコピー
COPY . .

# ポート番号を指定
EXPOSE 3000

# アプリケーション実行コマンド
CMD ["npm", "start"]
```

## 基本的なDockerコマンド

### イメージ操作

```bash
# イメージをビルド
docker build -t my-app:latest .

# イメージ一覧を表示
docker images

# イメージを削除
docker rmi image_name
```

### コンテナ操作

```bash
# コンテナを実行
docker run -d -p 3000:3000 --name my-container my-app:latest

# 実行中のコンテナを表示
docker ps

# コンテナに接続
docker exec -it my-container /bin/sh

# コンテナを停止
docker stop my-container

# コンテナを削除
docker rm my-container
```

### レジストリ操作

```bash
# Docker Hubからイメージを取得
docker pull nginx:latest

# Docker Hubにイメージをプッシュ
docker push username/my-app:latest
```

## 実践例：Node.jsアプリケーションのDockerization

### 1. サンプルアプリケーションの準備

```javascript
// app.js
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello Docker!' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```

```json
{
  "name": "docker-demo",
  "version": "1.0.0",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

### 2. Dockerfileの作成

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

USER node

CMD ["npm", "start"]
```

### 3. .dockerignoreファイル

```
node_modules
npm-debug.log
.git
.gitignore
README.md
Dockerfile
.dockerignore
```

### 4. ビルドと実行

```bash
# イメージをビルド
docker build -t node-demo .

# コンテナを実行
docker run -d -p 3000:3000 --name node-app node-demo

# 動作確認
curl http://localhost:3000
```

## Docker Composeによる複数コンテナ管理

複数のサービスを組み合わせる場合は、Docker Composeが便利です。

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
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# 全サービスを起動
docker-compose up -d

# 全サービスを停止・削除
docker-compose down
```

## ベストプラクティス

### 1. マルチステージビルド

```dockerfile
# ビルドステージ
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 本番ステージ
FROM node:18-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
CMD ["npm", "start"]
```

### 2. セキュリティ対策

- 非rootユーザーでの実行
- 最小限の権限でのコンテナ実行
- 定期的なベースイメージの更新

### 3. パフォーマンス最適化

- レイヤーキャッシュの活用
- 不要なファイルの除外
- 軽量なベースイメージの使用

## まとめ

Dockerは現代の開発において必須のスキルです。本記事で紹介した基礎知識と実践例を参考に、まずは簡単なアプリケーションからDockerization を始めてみてください。

継続的な学習のポイント：
- 公式ドキュメントの定期的な確認
- セキュリティベストプラクティスの習得
- Kubernetesなどのオーケストレーションツールへの発展

Dockerを活用して、より効率的で信頼性の高い開発環境を構築していきましょう。