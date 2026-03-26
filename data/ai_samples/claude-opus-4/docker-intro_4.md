# Docker入門ガイド：コンテナ技術の基礎から実践まで

## はじめに

近年のソフトウェア開発において、Dockerは必須とも言える技術となっています。本記事では、Dockerの基本概念から実際の使い方まで、初心者エンジニアが理解しやすいように解説します。

## Dockerとは何か？

Dockerは、アプリケーションとその実行環境をコンテナという単位でパッケージ化し、どこでも同じように動作させることができるコンテナ型仮想化技術です。

### 従来の仮想化との違い

従来の仮想マシン（VM）と比較すると、Dockerコンテナには以下のような特徴があります：

- **軽量性**: OSカーネルを共有するため、VMより軽量
- **高速性**: 起動が数秒で完了
- **ポータビリティ**: 「開発環境では動くが本番環境では動かない」問題を解決

## Dockerの主要コンポーネント

### 1. Docker Image（イメージ）
アプリケーションの実行に必要なファイルシステムやメタデータを含む読み取り専用のテンプレート

### 2. Docker Container（コンテナ）
イメージから作成される実行可能なインスタンス

### 3. Dockerfile
イメージをビルドするための設定ファイル

### 4. Docker Hub
Dockerイメージを共有するためのクラウドベースのレジストリサービス

## Dockerのインストール

### macOS/Windows
Docker Desktopをダウンロードしてインストールします。

### Linux (Ubuntu/Debian)
```bash
# Dockerの公式GPGキーを追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Dockerリポジトリを追加
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Dockerをインストール
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

## 基本的なDockerコマンド

### イメージの操作
```bash
# イメージの検索
docker search nginx

# イメージのダウンロード
docker pull nginx:latest

# ローカルのイメージ一覧
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

# コンテナのログ確認
docker logs my-nginx
```

## Dockerfileの作成

簡単なNode.jsアプリケーションのDockerfileの例：

```dockerfile
# ベースイメージの指定
FROM node:14-alpine

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
CMD ["node", "index.js"]
```

### イメージのビルドと実行
```bash
# イメージのビルド
docker build -t my-node-app .

# コンテナの実行
docker run -d -p 3000:3000 --name my-app my-node-app
```

## Docker Composeによる複数コンテナの管理

複数のコンテナを組み合わせて使用する場合は、Docker Composeが便利です。

### docker-compose.yml の例
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=mongodb://db:27017/myapp
    depends_on:
      - db

  db:
    image: mongo:4.4
    volumes:
      - mongo-data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password

volumes:
  mongo-data:
```

### Docker Composeの基本コマンド
```bash
# サービスの起動
docker-compose up -d

# サービスの停止
docker-compose down

# ログの確認
docker-compose logs -f

# サービスの再構築
docker-compose build
```

## ベストプラクティス

1. **軽量なベースイメージを使用**: Alpine Linuxベースのイメージを優先
2. **マルチステージビルドの活用**: 本番用イメージのサイズを最小化
3. **.dockerignoreファイルの作成**: 不要なファイルをイメージから除外
4. **1コンテナ1プロセス**: 各コンテナは単一の責任を持つように設計
5. **環境変数の活用**: 設定値は環境変数で管理

## まとめ

Dockerは現代のソフトウェア開発において欠かせない技術となっています。本記事で紹介した基本的な概念とコマンドを理解すれば、Dockerを使った開発を始めることができます。

次のステップとしては、実際にアプリケーションをコンテナ化し、CI/CDパイプラインに組み込むなど、より実践的な使い方を学んでいくことをおすすめします。

## 参考リンク

- [Docker公式ドキュメント](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose公式ドキュメント](https://docs.docker.com/compose/)