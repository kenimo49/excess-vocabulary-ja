# Docker入門ガイド ― エンジニア向け

## 1. はじめに

開発環境や本番環境の差異を減らしたい、依存関係を明示的に管理したい、といった課題に直面したとき、Docker が解決策として登場します。本記事では「Docker の基礎から実際に使えるコマンド・ファイル構成まで」を、エンジニアの観点から簡潔にまとめました。Docker を使ったことがない、あるいは軽く触っただけの方でもすぐに試せる内容を意識しています。

## 2. Docker とは？

- **軽量仮想化**: ホスト OS のカーネルを共有しつつ、独立したユーザー空間（コンテナ）を作成。VM より高速でリソース効率が高い。
- **イメージ**: コンテナを生成するためのテンプレート。イメージはレイヤー単位で管理され、重複は共有される。
- **レジストリ**: Docker Hub や自前の Registry にイメージを格納・配布。`docker pull` / `docker push` でやり取り。

> **ポイント**  
> コンテナは「イメージから起動したプロセスの集合」です。コンテナを再起動するときは、再びイメージから生成します。

## 3. 何ができるのか？

- **環境差異の除去**: 開発 → ステージング → 本番で同じイメージを使うことで「動くはずなのに動かない」問題を軽減。
- **依存関係のカプセル化**: ランタイム、ライブラリ、設定ファイルをすべてイメージに含める。
- **自動化**: CI/CD でビルド・テスト・デプロイを統一的に実行可能。
- **マイクロサービス**: 各サービスを独立したコンテナで実行し、ネットワークを通じて通信。

## 4. まずはインストール

### Windows / macOS

[公式サイト](https://www.docker.com/products/docker-desktop) から Docker Desktop をダウンロードし、指示に従ってインストール。インストール後、`docker --version` で確認。

### Linux (Ubuntu 例)

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# リポジトリ追加
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# インストール
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

## 5. 基本コマンド

| コマンド | 説明 |
|---|---|
| `docker pull <image>` | イメージをレジストリから取得 |
| `docker run <options> <image> <cmd>` | コンテナを起動 |
| `docker build -t <name> .` | Dockerfile からイメージ作成 |
| `docker ps` | 実行中のコンテナ一覧 |
| `docker stop <id>` | コンテナ停止 |
| `docker rm <id>` | コンテナ削除 |
| `docker rmi <image>` | イメージ削除 |

> **例**  
> ```bash
> docker run -d --name webapp -p 8080:80 nginx
> ```

## 6. Dockerfile でイメージ作成

### 例：Node.js アプリ

```dockerfile
# ベースイメージ
FROM node:18-alpine

# 作業ディレクトリ作成
WORKDIR /app

# 依存ファイルをコピー
COPY package*.json ./

# 依存関係インストール
RUN npm ci --only=production

# アプリコードをコピー
COPY . .

# ポート宣言
EXPOSE 3000

# アプリ起動
CMD ["node", "index.js"]
```

`docker build -t my-node-app .` でイメージをビルドし、`docker run -p 3000:3000 my-node-app` で起動できます。

## 7. コンテナ管理

- **永続化**: `docker run -v /host/path:/container/path` でホストディレクトリをマウント。
- **環境変数**: `-e` で渡す。例: `docker run -e NODE_ENV=production my-node-app`
- **名前付け**: `--name` で管理しやすく。`docker rm <name>` で削除も簡単。

## 8. ボリュームとネットワーク

### ボリューム

```bash
# ボリューム作成
docker volume create dbdata

# コンテナにマウント
docker run -d --name db -v dbdata:/var/lib/mysql mysql:8
```

### ネットワーク

```bash
# カスタムネットワーク作成
docker network create mynet

# コンテナをネットワークに接続
docker run -d --name api --network mynet my-api-image
docker run -d --name frontend --network mynet my-frontend-image
```

## 9. Docker Compose で複数コンテナ

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: example
    volumes:
      - dbdata:/var/lib/mysql

  api:
    build: ./api
    depends_on:
      - db
    environment:
      DB_HOST: db
    ports:
      - "3000:3000"

  frontend:
    build: ./frontend
    depends_on:
      - api
    ports:
      - "8080:80"

volumes:
  dbdata:
```

`docker compose up -d` で一括起動。サービス間の通信はサービス名で解決されます。

## 10. よくあるエラーと対処

| エラー | 原因 | 対策 |
|---|---|---|
| `no such file or directory: open /etc/passwd` | ホスト側の `/etc/passwd` が参照されている | `--user` オプションで UID/GID を指定 |
| `Permission denied` | ボリュームの権限 | コンテナ内で権限を付与 (`chown`) |
| `image not found` | イメージ名間違い | `docker images` で確認、タグ付けを確認 |
| `Cannot connect to the Docker daemon` | Docker デーモン未起動 / 権限不足 | `sudo systemctl start docker` / `sudo usermod -aG docker $USER` |

## 11. まとめ

Docker は「イメージ × コンテナ」の組み合わせで環境差異を解消し、開発・本番を同じスクリプトでデプロイできるパワフルなツールです。この記事で紹介した基本コマンド・Dockerfile・Compose を土台に、次のステップとしては以下を検討してみてください。

1. **CI/CD パイプラインへの組み込み**  
   GitHub Actions / GitLab CI でビルド・テスト・デプロイを自動化。

2. **マルチステージビルド**  
   ビルド環境と実行環境を分離し、イメージサイズを削減。

3. **Kubernetes 連携**  
   `kubectl` と連携し、スケーラブルなクラスタ構成へ。

Docker の学習は「まずは動かす」ことから始まります。小さなプロジェクトで実際にイメージを作成・デプロイしてみて、コンテナの挙動を体感してみてください。成功すれば、開発チーム全体の生産性向上へ直結します。 Happy Dockering! 🚀