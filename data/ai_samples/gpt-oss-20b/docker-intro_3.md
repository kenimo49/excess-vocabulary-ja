# Docker入門ガイド  
（エンジニア向け、約1,400文字）

---

## 1. Dockerとは何か  

Dockerは「コンテナ型仮想化」技術で、OSレベルでの仮想化を行います。  
- **イメージ**：アプリケーションとその依存関係をパッケージ化したファイル  
- **コンテナ**：イメージを実行した状態（実行時のプロセス群）  
- **レイヤー**：イメージは複数の読み取り専用レイヤーを積み上げて作られ、同じベースイメージを共有することでストレージ効率が向上  

従来の仮想マシン（VM）と比べて起動時間が数秒、リソース消費も低く、CI/CDやマイクロサービス構成で重宝します。

---

## 2. Dockerのインストール  

### Windows / macOS  
1. Docker Desktopを公式サイトからダウンロード  
2. インストール後、`docker --version`でバージョン確認  

### Linux (Ubuntu)  
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```
※公式リポジトリを使う場合は、`curl -fsSL https://get.docker.com -o get-docker.sh` でインストールすることもできます。

---

## 3. 基本コマンド  

| コマンド | 説明 |
|----------|------|
| `docker pull <イメージ>` | イメージを取得 |
| `docker run <オプション> <イメージ>` | コンテナを起動 |
| `docker ps` | 実行中コンテナ一覧 |
| `docker stop <コンテナID>` | コンテナ停止 |
| `docker rm <コンテナID>` | コンテナ削除 |
| `docker rmi <イメージ>` | イメージ削除 |

**例：Nginxコンテナの起動**  
```bash
docker run -d -p 8080:80 --name web nginx:latest
```

---

## 4. Dockerfile でイメージを作る  

```Dockerfile
# ベースイメージ
FROM python:3.10-slim

# 作業ディレクトリ
WORKDIR /app

# 依存ファイルをコピー
COPY requirements.txt .

# 依存ライブラリインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# コンテナ起動時に実行
CMD ["python", "app.py"]
```

ビルドは `docker build -t myapp:1.0 .`、実行は `docker run -p 5000:5000 myapp:1.0` で行えます。

---

## 5. Docker Composeで複数サービスをまとめる  

`docker-compose.yml`  
```yaml
version: '3.9'
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
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```bash
docker compose up -d   # サービス起動
docker compose down    # 停止・削除
```

---

## 6. ベストプラクティス  

1. **イメージサイズを最小化**  
   - `--no-cache`を使わない  
   - `multi-stage build`で不要ファイルを除外  
2. **レイヤーを整理**  
   - `RUN`, `COPY`の順序は頻度が低いものを上に  
3. **環境変数で設定を分離**  
   - `ENV`を使い、`docker run -e`でオーバーライド  
4. **イメージの署名**  
   - Docker Content Trust（DCT）を有効化  
5. **定期的にベースイメージを更新**  
   - 公式セキュリティパッチを適用  

---

## 7. よくある質問  

| 質問 | 回答 |
|------|------|
| **DockerはVMを置き換えるのか？** | 目的により。軽量なサービスはコンテナ、完全に隔離された環境が必要ならVM。 |
| **Dockerfileでキャッシュを使うとき注意点は？** | 変更頻度が高いステップは最後に置く。 |
| **ボリュームの永続化はどうする？** | `docker volume create`で管理し、Composeで`volumes:`に指定。 |

---

## 8. まとめ  

Dockerはアプリケーションの一貫した実行環境を提供し、開発から本番への移行をスムーズにします。  
- インストールは簡単  
- `Dockerfile`でイメージを自動化  
- `docker compose`でマイクロサービスを一括管理  

実際に手を動かし、最小限のプロジェクトで試してみるのが一番の学習法です。  
次回は**Docker Swarm**や**Kubernetes**との統合について掘り下げます。ぜひご期待ください。