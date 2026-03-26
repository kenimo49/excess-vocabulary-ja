# Docker入門ガイド ― エンジニア向け実践的解説

Docker は「アプリをどこでも同じように動かす」ためのプラットフォームです。  
このガイドでは、Docker の基礎概念から実際にイメージを作成し、コンテナを走らせる手順を 1000–2000 字程度でまとめました。  
初心者でも一歩ずつ理解できるよう、コード例とともに解説します。

---

## 1. Docker とは？

- **コンテナ**：OS のカーネルを共有しつつ、アプリとその依存関係を隔離した実行環境。  
- **イメージ**：コンテナを起動するためのスナップショット。  
- **レジストリ**：イメージを保存・共有する場所（公式は Docker Hub）。

> **ポイント**  
> *コンテナ＝実行環境、イメージ＝その環境を作るためのテンプレート。*

---

## 2. 何ができるのか？

- **環境差異の解消**：開発→ステージング→本番まで同じイメージを使える。  
- **高速デプロイ**：イメージを pull してすぐに実行。  
- **スケールアウト**：同じコンテナを複数起動してロードバランシング。

---

## 3. インストール（Ubuntu 22.04 の例）

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

> `docker --version` で確認。  
> `sudo usermod -aG docker $USER` で一般ユーザーが Docker を使えるように。

---

## 4. 基本操作

| コマンド | 意味 | 例 |
|----------|------|----|
| `docker run` | イメージからコンテナを起動 | `docker run -d -p 8080:80 nginx` |
| `docker build` | Dockerfile からイメージを作る | `docker build -t myapp .` |
| `docker ps` | 実行中のコンテナ一覧 | `docker ps` |
| `docker stop` | コンテナ停止 | `docker stop <id>` |
| `docker rm` | コンテナ削除 | `docker rm <id>` |
| `docker rmi` | イメージ削除 | `docker rmi myapp` |

---

## 5. Dockerfile の書き方

簡単な Python Flask アプリを例にします。

```dockerfile
# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存ファイルをコピー
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY . .

# ポート公開
EXPOSE 5000

# 起動コマンド
CMD ["python", "app.py"]
```

### 使い方

```bash
# Dockerfile があるディレクトリで
docker build -t myflask .
docker run -d -p 5000:5000 myflask
```

---

## 6. Docker Compose で複数コンテナを管理

`docker-compose.yml` を作成し、サービスを一括起動します。

```yaml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "5000:5000"
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: example
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

```bash
docker compose up -d      # 起動
docker compose down       # 停止＆削除
```

---

## 7. ベストプラクティス

| 項目 | 推奨内容 |
|------|----------|
| **.dockerignore** | ビルドコンテキストに不要ファイルを含めない。 |
| **マルチステージビルド** | ビルド時に必要なツールを入れ、最終イメージは必要最低限。 |
| **イメージサイズの最適化** | `FROM python:slim` など軽量イメージを使い、不要ファイルを削除。 |
| **環境変数管理** | `ARG` と `ENV` を使い、ビルド時とランタイム時の差分を明確化。 |
| **セキュリティ** | 可能なら非 root ユーザーで実行 (`USER appuser`)。 |
| **レジストリ** | Docker Hub だけでなく、プライベートレジストリ（Harbor など）を活用。 |

---

## 8. よくあるトラブルと対処法

| エラー | 原因 | 解決策 |
|--------|------|--------|
| `Cannot connect to the Docker daemon` | Docker デーモンが起動していない | `sudo systemctl start docker` |
| `permission denied` | ユーザーに docker グループ権限が無い | `sudo usermod -aG docker $USER` で追加し、再ログイン |
| `Error response from daemon: pull access denied` | イメージ名誤記またはプライベートレジストリ認証不足 | イメージ名確認、`docker login` でログイン |

---

## 9. まとめ

- **Docker** は「イメージ → コンテナ」の概念で、同一環境を何度でも作れる。  
- **基本操作** (`docker run`, `docker build`, `docker ps`) を覚え、**Dockerfile** で自分だけのイメージを作成。  
- **Compose** でマイクロサービスを一括管理し、開発・デプロイをスムーズに。  
- **ベストプラクティス** を取り入れることで、サイズ・セキュリティ・保守性が向上。  

これで Docker を使い始めるための基礎が整いました。  
実際にプロジェクトに導入してみて、CI/CD で自動ビルド・デプロイまでワークフローを完成させてみてください。 🚀