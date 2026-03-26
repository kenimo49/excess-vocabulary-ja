# Docker入門ガイド ― エンジニア向け基礎から実践まで

Dockerは「コンテナ」という軽量仮想化技術で、アプリケーションを環境に依存せず一貫した状態で実行できるようにします。  
この記事では、Dockerの概念、セットアップ、基本操作、そして実際にコードを書いてみる流れをまとめます。読了後は「Dockerを自分のプロジェクトで使える」レベルを目指しましょう。

---

## 1. Dockerとは？

- **コンテナ**：OSカーネルを共有しながら、独立したファイルシステム、ネットワーク、プロセス空間を持つ実行単位。  
- **イメージ**：コンテナの実行に必要なすべてのファイルと設定をひとまとめにしたテンプレート。  
- **レジストリ**：イメージを格納・配布するリポジトリ。Docker Hubは代表例です。

> **ポイント**  
> *VMはOS単位で仮想化し重くなるのに対し、コンテナはOSを共有するため起動が高速。  
> *イメージは不変（immutable）であるため、再現性が保証される。  

---

## 2. なぜDockerを使うのか？

| 目的 | Dockerで解決できる課題 |
|------|------------------------|
| **開発環境の揺らぎ** | すべての依存をイメージに閉じ込めるので「動くなら私のマシンでも動く」 |
| **デプロイの一貫性** | 本番と同じイメージを任意の環境へデプロイでき、設定ミスを減らす |
| **スケールアウト** | コンテナを素早く起動・停止でき、水平スケールが容易 |
| **リソース効率** | VMに比べて軽量で同じホスト上に多数コンテナを走らせられる |

---

## 3. 環境構築

### 3.1 インストール

```bash
# Ubuntu 22.04 の例
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
```

### 3.2 動作確認

```bash
docker --version
docker run hello-world
```

`hello-world` が正常に表示されればOK。

---

## 4. 基本操作

| コマンド | 説明 |
|----------|------|
| `docker pull <image>` | イメージをレジストリから取得 |
| `docker run <options> <image> [cmd]` | コンテナを起動 |
| `docker ps [-a]` | 実行中/停止済みコンテナ一覧 |
| `docker stop <container>` | コンテナ停止 |
| `docker rm <container>` | コンテナ削除 |
| `docker rmi <image>` | イメージ削除 |
| `docker images` | ローカルイメージ一覧 |

> **Tips**  
> * `-d` はデタッチドモードでバックグラウンド実行。  
> * `-p host:container` でポートマッピング。  
> * `-v host_path:container_path` でボリュームマウント。

---

## 5. Dockerfile でイメージを作る

### 5.1 サンプル：Python アプリ

```Dockerfile
# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存ファイルをコピー
COPY requirements.txt .

# 依存をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

# コンテナ起動時のコマンド
CMD ["python", "app.py"]
```

#### ビルド・実行

```bash
docker build -t my-python-app .
docker run -p 5000:5000 my-python-app
```

---

## 6. Docker Compose で複数コンテナを管理

`docker-compose.yml` でサービスを定義し、`docker compose up` で一括起動。

```yaml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: example
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

> **ポイント**  
> * `volumes` は永続化に便利。  
> * `depends_on` で起動順序を制御可能。  

---

## 7. よくある落とし穴

| 項目 | 注意点 |
|------|--------|
| **イメージのサイズ** | `--squash` で不要ファイルを削除、`alpine` ベースを検討。 |
| **レイヤーキャッシュ** | 頻繁に変更するファイルは `COPY` を後ろに移動。 |
| **環境変数漏洩** | `docker secrets` を使い、パスワードを安全に管理。 |
| **ポート競合** | ホスト側のポートが既に使用中なら別番号へ変更。 |

---

## 8. さらに学ぶために

1. **Docker Desktop** – GUI で簡単に管理。  
2. **Docker Swarm / Kubernetes** – 本番向けクラスタ管理。  
3. **CI/CD** – GitHub Actions で `docker buildx` を活用。  
4. **セキュリティ** – `docker scan`, `trivy` で脆弱性診断。  

---

## 9. まとめ

- Docker は「環境を作らない」開発スタイルを実現。  
- イメージ＝イミュータブル、コンテナ＝ランタイム。  
- `Dockerfile` と `docker compose` を使えば、再現性と拡張性を両立。  
- 最初はシンプルに、実際に動かしてみることが何よりも重要。

次回は **「Docker Swarmでクラスタを構築する」** に挑戦し、実際にスケールアウトを体験してみましょう。 Happy Dockering! 🚀