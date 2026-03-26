# Docker入門ガイド：コンテナ技術を使いこなすための第一歩

## はじめに

近年のソフトウェア開発において、Dockerは欠かせない技術となっています。「でも、Dockerって何？」「どうやって使い始めればいいの？」と思っている方も多いのではないでしょうか。

本記事では、Docker初心者の方を対象に、Dockerの基本概念から実際の使い方まで、わかりやすく解説していきます。

## Dockerとは何か？

Dockerは、アプリケーションを**コンテナ**と呼ばれる軽量な実行環境にパッケージ化する技術です。

### 従来の問題点
- 「開発環境では動くのに、本番環境では動かない」
- 環境構築に時間がかかる
- チーム間で環境の差異が生じやすい

### Dockerが解決すること
- **環境の一貫性**: どこでも同じ環境でアプリケーションが動作
- **軽量性**: 仮想マシンより高速に起動・実行
- **移植性**: 一度作成したコンテナはどこでも実行可能

## Dockerの基本概念

### 1. イメージ（Image）
アプリケーションの実行に必要なすべての要素（コード、ランタイム、ライブラリなど）を含む読み取り専用のテンプレートです。

### 2. コンテナ（Container）
イメージから作成される実行可能なインスタンスです。独立した環境で動作します。

### 3. Dockerfile
イメージを作成するための設計図となるテキストファイルです。

### 4. Docker Hub
Dockerイメージを共有するための公式レジストリです。

## Dockerのインストール

### macOS/Windows
[Docker Desktop](https://www.docker.com/products/docker-desktop)をダウンロードしてインストールします。

### Linux (Ubuntu/Debian)
```bash
# Dockerのインストール
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 現在のユーザーをdockerグループに追加
sudo usermod -aG docker $USER
```

## 基本的なDockerコマンド

### イメージの操作

```bash
# イメージの取得
docker pull nginx:latest

# イメージ一覧の表示
docker images

# イメージの削除
docker rmi nginx:latest
```

### コンテナの操作

```bash
# コンテナの起動
docker run -d -p 8080:80 --name my-nginx nginx:latest

# 実行中のコンテナ一覧
docker ps

# すべてのコンテナ一覧
docker ps -a

# コンテナの停止
docker stop my-nginx

# コンテナの削除
docker rm my-nginx
```

## 実践：シンプルなWebアプリケーションの作成

Node.jsのWebアプリケーションをDocker化してみましょう。

### 1. アプリケーションの作成

**app.js**
```javascript
const express = require('express');
const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello, Docker!' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
```

**package.json**
```json
{
  "name": "docker-node-app",
  "version": "1.0.0",
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
# ベースイメージの指定
FROM node:18-alpine

# 作業ディレクトリの設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm install

# アプリケーションのソースをコピー
COPY . .

# ポートの公開
EXPOSE 3000

# アプリケーションの起動
CMD ["npm", "start"]
```

### 3. イメージのビルドと実行

```bash
# イメージのビルド
docker build -t my-node-app .

# コンテナの起動
docker run -d -p 3000:3000 --name node-container my-node-app

# 動作確認
curl http://localhost:3000
```

## Docker Composeで複数コンテナを管理

複数のサービスを組み合わせる場合は、Docker Composeを使用します。

**docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

```bash
# サービスの起動
docker-compose up -d

# サービスの停止
docker-compose down
```

## ベストプラクティス

1. **軽量なベースイメージを使用**: Alpine Linuxベースのイメージを選択
2. **.dockerignoreファイルの活用**: 不要なファイルをイメージに含めない
3. **マルチステージビルド**: ビルド時と実行時でイメージを分ける
4. **レイヤーのキャッシュを活用**: 変更頻度の低いものから順にCOPY

## まとめ

Dockerは、現代のソフトウェア開発において必須のスキルとなっています。本記事で紹介した基本的な使い方をマスターすれば、開発効率の向上や環境構築の簡素化を実現できます。

次のステップとして、以下を学習することをお勧めします：
- Kubernetesによるコンテナオーケストレーション
- CI/CDパイプラインでのDocker活用
- セキュリティベストプラクティス

Dockerを使いこなして、より効率的な開発環境を構築していきましょう！

## 参考リンク
- [Docker公式ドキュメント](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose公式ドキュメント](https://docs.docker.com/compose/)