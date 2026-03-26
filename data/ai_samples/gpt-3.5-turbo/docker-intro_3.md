# Docker入門ガイド

## はじめに

Dockerはコンテナ仮想化技術の一つで、環境をコンテナとして扱い、アプリケーションを簡単にデプロイできるようにするツールです。今回は、Docker入門ガイドとして、基本的な使い方や概念について解説していきます。

## Dockerとは

DockerはLinuxコンテナ技術を用いて独立した環境を作成し、それをアプリケーションの実行のために使うことができます。コンテナ内にはアプリケーションの実行に必要な全てのライブラリや依存関係が含まれており、外部の環境に依存しない実行環境を提供します。

## Dockerの基本コマンド

Dockerを使う上で知っておきたい基本的なコマンドを紹介します。

1. `docker run`: コンテナを実行するためのコマンドです。例えば、`docker run -it ubuntu:latest bash`と入力すると、最新のUbuntuイメージを使用してbashシェルが起動します。
2. `docker ps`: 現在実行中のコンテナを確認するコマンドです。
3. `docker stop`: 実行中のコンテナを停止するコマンドです。
4. `docker rm`: コンテナを削除するコマンドです。
5. `docker images`: ローカルに保存されているイメージを確認するコマンドです。

## Dockerイメージとコンテナ

Dockerでは、イメージとコンテナという2つの概念があります。

- Dockerイメージ: アプリケーション実行に必要なファイルや設定を含む静的なファイルです。イメージはDocker Hubなどのレジストリから取得することもできます。
- Dockerコンテナ: イメージを元に作成される実行中の環境です。コンテナはイメージを元に起動され、独立して動作します。

## Dockerfileとは

DockerfileはDockerイメージを構築するためのスクリプトファイルです。Dockerfileを使用すると、イメージの構築や設定を自動化することができます。以下は、一般的なDockerfileの例です。

```dockerfile
# ベースイメージの指定
FROM ubuntu:latest

# パッケージのインストール
RUN apt-get update && apt-get install -y nginx

# ポートの公開
EXPOSE 80

# コンテナの起動時に実行されるコマンド
CMD ["nginx", "-g", "daemon off;"]
```

## Dockerコンテナのネットワーク

Dockerでは、コンテナ間の通信や外部との通信を行うためにネットワークを設定することができます。以下は、Dockerネットワークの設定例です。

```bash
# ネットワークの作成
docker network create mynetwork

# コンテナの作成とネットワークへの接続
docker run -d --name container1 --network mynetwork nginx
docker run -d --name container2 --network mynetwork nginx
```

## まとめ

以上、Docker入門ガイドとして基本的な使い方や概念について解説しました。Dockerを使うことで、簡単に環境を構築し、アプリケーションをデプロイすることができます。是非、実際にDockerを使ってみて、その便利さを体感してみてください。