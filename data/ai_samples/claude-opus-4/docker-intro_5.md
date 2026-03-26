# Docker入門ガイド：コンテナ技術で開発環境を革新する

## はじめに

Dockerは、アプリケーションをコンテナと呼ばれる軽量な実行環境にパッケージ化する技術です。本記事では、Dockerの基本概念から実践的な使い方まで、エンジニアが知っておくべき内容を解説します。

## Dockerとは？

Dockerは、アプリケーションとその依存関係を一つのパッケージ（コンテナイメージ）にまとめ、どの環境でも同じように動作させることができるコンテナ型仮想化技術です。

### 従来の仮想化技術との違い

従来の仮想マシン（VM）と比較して、Dockerには以下のメリットがあります：

- **軽量性**: OSカーネルを共有するため、起動が高速でリソース消費が少ない
- **ポータビリティ**: 開発環境と本番環境の差異を解消
- **スケーラビリティ**: コンテナの複製や削除が容易

## 基本概念

### 1. イメージ（Image）
アプリケーションの実行に必要なファイルやライブラリ、設定をパッケージ化したもの。読み取り専用のテンプレート。

### 2. コンテナ（Container）
イメージから作成される実行可能なインスタンス。アプリケーションが実際に動作する環境。

### 3. Dockerfile
イメージを構築するための設計図。必要な手順を記述したテキストファイル。

### 4. Docker Hub
Dockerイメージを共有するための公式レジストリサービス。

## インストールと環境構築

### macOS/Windows
Docker Desktopをインストール：
```bash
# 公式サイトからダウンロード
# https://www.docker.com/products/docker-desktop
```

### Linux (Ubuntu/Debian)
```bash
# リポジトリの更新
sudo apt-get update

# Dockerのインストール
sudo apt-get install docker.io

# Dockerサービスの起動
sudo systemctl start docker
sudo systemctl enable docker
```

## 基本的なコマンド

### イメージ操作
```bash
# イメージの取得
docker pull nginx:latest

# イメージ一覧の表示
docker images

# イメージの削除
docker rmi <image_id>
```

### コンテナ操作
```bash
# コンテナの実行
docker run -d -p 8080:80 --name web nginx

# コンテナ一覧の表示
docker ps -a

# コンテナの停止・開始
docker stop web
docker start web

# コンテナの削除
docker rm web
```

## 実践：シンプルなWebアプリケーションの構築

Node.jsアプリケーションを例に、Dockerイメージを作成してみましょう。

### 1. アプリケーションの準備

`app.js`:
```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello, Docker!');
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

`package.json`:
```json
{
  "name": "docker-demo",
  "version": "1.0.0",
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
# ベースイメージの指定
FROM node:16-alpine

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

# アプリケーションの起動コマンド
CMD ["npm", "start"]
```

### 3. イメージのビルドと実行

```bash
# イメージのビルド
docker build -t my-node-app .

# コンテナの実行
docker run -d -p 3000:3000 --name my-app my-node-app

# ブラウザでhttp://localhost:3000にアクセス
```

## Docker Composeによる複数コンテナの管理

複数のサービスを組み合わせる場合は、Docker Composeが便利です。

`docker-compose.yml`:
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
      - DB_HOST=db
      - DB_USER=root
      - DB_PASS=password
  
  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=myapp
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

実行コマンド：
```bash
# サービスの起動
docker-compose up -d

# サービスの停止
docker-compose down
```

## ベストプラクティス

1. **マルチステージビルド**: イメージサイズの最適化
2. **.dockerignore**: 不要なファイルの除外
3. **タグ管理**: バージョニングの徹底
4. **セキュリティ**: 最小権限の原則、公式イメージの利用

## まとめ

Dockerは現代の開発において欠かせない技術となっています。本記事で紹介した基本的な概念とコマンドを理解することで、開発環境の構築や運用がより効率的になります。

次のステップとしては、Kubernetes等のオーケストレーションツールの学習や、CI/CDパイプラインへの統合を検討することをお勧めします。

開発効率を大幅に向上させるDocker、ぜひ実際に手を動かして体験してみてください。