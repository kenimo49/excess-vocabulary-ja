# Docker入門ガイド

近年、クラウドコンピューティングやマイクロサービスアーキテクチャの普及に伴い、効率的なアプリケーションの開発・デプロイメントが求められています。そこで注目されているのがコンテナ技術であり、その代表的なツールがDockerです。本記事では、エンジニアの皆さんを対象に、Dockerの基本概念から始め、基本的なコマンドや簡単な使い方について解説します。

## Dockerとは？

Dockerは、軽量なコンテナ型仮想環境を作成・管理するためのオープンソースプラットフォームです。従来の仮想化技術と異なり、ホストOSと共通のカーネルを使用するため、より高速に動作し、リソースの消費も少なくなります。Dockerを使用すると、ソフトウェアを「イメージ」としてパッケージ化し、それを「コンテナ」という独立した実行環境で動かすことが可能です。

## Dockerの基本構造

- **イメージ**: アプリケーションとそれに必要なすべてのライブラリ、設定、依存関係をパッケージ化したもの。Docker Hubなどのリポジトリから取得可能です。
- **コンテナ**: イメージを実行したもので、それ自身が軽量な仮想環境となります。
- **Dockerfile**: イメージを作成するための設定ファイルです。どの基盤イメージを使用し、何をインストールするかを指定します。

## Dockerのインストール

まずは、Dockerをインストールしましょう。DockerはWindows、macOS、Linuxの各プラットフォームで利用可能です。以下では、簡単にインストール手順を紹介します。

### WindowsおよびmacOS

1. [公式サイト](https://www.docker.com/products/docker-desktop/)からDocker Desktopをダウンロードし、インストールします。
2. インストーラーの指示に従いインストールを完了させ、Docker Desktopを起動します。

### Linux

各ディストリビューションに対応したインストール手順を利用してください。以下はUbuntuの例です。

```bash
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

インストール後、以下のコマンドでDockerが正常に動作していることを確認できます。

```bash
docker --version
```

## 基本コマンド

### 1. イメージの取得

Docker Hubからイメージを取得するには`docker pull`コマンドを使用します。例えば、Ubuntuイメージを取得するには以下のコマンドを実行します。

```bash
docker pull ubuntu
```

### 2. コンテナの起動

イメージからコンテナを作成して起動するには`docker run`コマンドを使用します。Ubuntuのコンテナを起動する例は以下の通りです。

```bash
docker run -it ubuntu
```

`-it`フラグは、インタラクティブモードでコンテナを起動するためのものです。

### 3. 実行中のコンテナの確認

実行中のコンテナを確認するには`docker ps`を使用します。

```bash
docker ps
```

全てのコンテナ（停止中も含む）を確認する場合は`-a`フラグを付けます。

```bash
docker ps -a
```

### 4. コンテナの停止

特定のコンテナを停止する場合は`docker stop [コンテナIDまたは名前]`を使用します。

```bash
docker stop <container_id>
```

### 5. コンテナの削除

コンテナを削除するには`docker rm`を使用します。

```bash
docker rm <container_id>
```

### 6. イメージの削除

不要なイメージを削除するには`docker rmi`を使用します。

```bash
docker rmi <image_id>
```

## Dockerfileの活用

Dockerfileを使用して、カスタムイメージを作成することが可能です。以下に簡単な例を示します。

```dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3
COPY ./myapp /app
WORKDIR /app
CMD ["python3", "myapp.py"]
```

このファイルをプロジェクトディレクトリに保存し、`docker build`コマンドでイメージを作成します。

```bash
docker build -t mypythonapp .
```

`-t`オプションはイメージに名前を付けるためのものです。このイメージを使用してコンテナを起動すれば、Pythonアプリケーションを独自の環境で実行することができます。

## まとめ

本記事では、Dockerの基本概念から入門するためのステップを解説しました。Dockerを使うことで、開発環境の整備やアプリケーションのデプロイがより簡単になり、マイクロサービスアーキテクチャの導入にも役立つでしょう。ぜひ、Dockerを利用して効率的な開発を進めてみてください。