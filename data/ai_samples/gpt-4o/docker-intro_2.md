# Docker入門ガイド

## はじめに

Dockerは、コンテナ技術を用いた仮想化プラットフォームで、アプリケーションの開発や配布、実行に革命をもたらしました。本記事では、Dockerの基本概念から、実際の環境構築まで、ステップバイステップで導入手順を解説していきます。

## Dockerとは何か？

Dockerは、コンテナと呼ばれる軽量仮想化環境上でアプリケーションを実行するためのプラットフォームです。従来の仮想化技術と異なり、DockerはホストOS上に直接実行されるため、より効率的で高速なアプリケーションのデプロイが可能です。

### コンテナとは？

コンテナは、アプリケーションとその依存ライブラリ、設定ファイルなどを一緒にパッケージ化したものです。コンテナはホストOSのカーネルを共有し、ホストシステムとは独立したプロセス空間で稼働します。このため、コンテナは仮想マシンに比べて軽量で起動も速くなります。

### Dockerの利点

1. **ポータビリティ**: Dockerコンテナは、開発環境から本番環境まで、どこでも同じ動作を保証します。
2. **スケーラビリティ**: 必要に応じて簡単にコンテナを拡張し、負荷分散を図ることができます。
3. **効率性**: コンテナはリソースを効率的に使用し、高速に起動・終了できます。

## Dockerの基本概念

Dockerを利用するためには、いくつかの基本概念を理解する必要があります。

### イメージとコンテナ

- **Dockerイメージ**: コンテナを作成するためのテンプレートです。イメージは不変であり、アプリケーションやライブラリなどの設定を含みます。
- **Dockerコンテナ**: イメージを基に作成される実行可能な実体です。コンテナはイメージのインスタンスであり、複数のコンテナを同じイメージから作成することができます。

### Dockerレジストリ

Dockerイメージはレジストリ上に保存され、そこからプル（ダウンロード）して使用します。Dockerの公式レジストリであるDocker Hubには、様々なイメージが公開されています。

## Dockerのインストール

Dockerを自分のシステムにインストールするには、以下の手順を実行します。ここでは人気のLinuxディストリビューションであるUbuntuを例にとります。

1. 必要なパッケージをインストール
   ```bash
   sudo apt update
   sudo apt install apt-transport-https ca-certificates curl software-properties-common
   ```

2. DockerのGPGキーを追加
   ```bash
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   ```

3. Dockerのリポジトリを追加
   ```bash
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   ```

4. Dockerのインストール
   ```bash
   sudo apt update
   sudo apt install docker-ce
   ```

5. インストール確認
   ```bash
   docker --version
   ```

## コンテナの操作

Dockerがインストールされたら、コンテナを起動してみましょう。

### イメージの取得とコンテナの起動

ここでは、公式のHello Worldイメージを使用します。

1. イメージの取得
   ```bash
   docker pull hello-world
   ```

2. コンテナの起動
   ```bash
   docker run hello-world
   ```

上記のコマンドを実行すると、Hello Worldが出力され、Dockerの動作を確認することができます。

### その他の基本コマンド

- **起動中のコンテナの確認**
  ```bash
  docker ps
  ```

- **全コンテナの確認（終了したコンテナも含む）**
  ```bash
  docker ps -a
  ```

- **コンテナの停止**
  ```bash
  docker stop <コンテナID>
  ```

- **コンテナの削除**
  ```bash
  docker rm <コンテナID>
  ```

- **イメージの削除**
  ```bash
  docker rmi <イメージID>
  ```

## Dockerfileによるイメージの作成

独自のDockerイメージを作成するためには、Dockerfileを使用します。ここでは、シンプルなNode.jsアプリケーションのDockerfileを例に取ります。

### Dockerfileのサンプル

```dockerfile
# ベースとなるイメージ
FROM node:14

# アプリケーションディレクトリを作成
WORKDIR /usr/src/app

# 依存ファイルをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install

# アプリケーションのソースをコピー
COPY . .

# アプリケーションを公開するポート
EXPOSE 8080

# アプリケーション起動コマンド
CMD ["node", "app.js"]
```

### イメージのビルド

Dockerfileのあるディレクトリで以下のコマンドを実行します。

```bash
docker build -t my-node-app .
```

これで、`my-node-app`という名前のDockerイメージが作成されます。

### イメージからコンテナを起動

```bash
docker run -p 8080:8080 my-node-app
```

これで、ローカルの8080ポートでNode.jsアプリケーションがアクセス可能になります。

## まとめ

Dockerは、アプリケーションの開発、デプロイ、運用を効率的に行うための強力なツールです。この記事では、Dockerの基本概念から環境構築、コンテナの操作、Dockerfileによるイメージ作成までを解説しました。次のステップとして、さらに高度なDockerの使用方法やオーケストレーションツール（例：Kubernetes）の導入を検討してみてください。Dockerを活用し、生産性の向上を図りましょう！