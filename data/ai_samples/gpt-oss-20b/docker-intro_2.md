# Docker入門ガイド

## 1. はじめに  
最近の開発現場では、環境差異による「It works on my machine」問題が頻発しています。  
Docker は「イメージ」というイメージ化された実行環境を提供し、開発・本番を同一に保つためのツールです。本記事では、Docker の基本概念から実際にコンテナを起動するまでをエンジニア向けにまとめます。

## 2. Docker とは？  
- **コンテナ**：OS カーネルを共有しながら、隔離された実行環境。  
- **イメージ**：実行可能なファイル＋設定を一つにまとめたテンプレート。  
- **レジストリ**：イメージを保存・共有するリポジトリ。Docker Hub が代表例。

### なぜコンテナなのか  
- 軽量: 仮想マシンより起動が高速。  
- 一貫性: 依存関係・設定をイメージに固めることで環境差を消す。  
- 可搬性: どこでも同じイメージを実行できる。

## 3. Docker のインストール  
```bash
# Ubuntu 22.04 例
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Docker GPGキーを追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# リポジトリ設定
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# インストール
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
インストール後は `docker version` で確認。`sudo usermod -aG docker $USER` で非rootで実行できるようにしておくと便利。

## 4. 基本コマンド  
| コマンド | 役割 |
|----------|------|
| `docker run` | コンテナ起動 |
| `docker ps` | 実行中コンテナ確認 |
| `docker ps -a` | 全コンテナ確認 |
| `docker stop` | コンテナ停止 |
| `docker rm` | コンテナ削除 |
| `docker images` | 取得済みイメージ一覧 |
| `docker rmi` | イメージ削除 |
| `docker logs` | コンテナログ取得 |
| `docker exec` | 実行中コンテナへアクセス |

### 例：nginx を起動
```bash
docker run --name mynginx -d -p 8080:80 nginx:stable-alpine
```
`-d` はデタッチモード、`-p` はポートフォワード。

## 5. Dockerfile でイメージを作る  
Dockerfile は「イメージのレシピ」です。  
```dockerfile
# ベースイメージ
FROM node:18-alpine

# 作業ディレクトリ
WORKDIR /app

# 依存ファイルコピー
COPY package*.json ./

# 依存インストール
RUN npm ci --only=production

# アプリコピー
COPY . .

# ビルド（必要なら）
# RUN npm run build

# ポート設定
EXPOSE 3000

# 起動コマンド
CMD ["npm", "start"]
```
ビルドは  
```bash
docker build -t myapp:1.0 .
```
実行は  
```bash
docker run -p 3000:3000 myapp:1.0
```

## 6. Docker Compose で複数サービスを管理  
複数コンテナを同時に起動したいときは Compose が便利。`docker-compose.yml` を作成し、`docker compose up` で一括起動。

```yaml
version: "3.9"
services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: example
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```
`docker compose up -d` でデタッチ起動。`docker compose down` で停止・削除。

## 7. ベストプラクティス  
1. **最小権限で実行** – `USER` ディレクティブで root 以外のユーザを指定。  
2. **マルチステージビルド** – 開発環境と本番環境を分離し、不要ファイルを除外。  
3. **キャッシュの活用** – 変更頻度の低いレイヤを先に書くことでビルド時間短縮。  
4. **イメージサイズを意識** – `alpine` ベースを使う、不要なファイルを削除。  
5. **CI/CD で自動ビルド** – GitHub Actions 等で `docker buildx` で多プラットフォームビルド。

## 8. トラブルシューティング  
| 事象 | 原因 | 対処 |
|------|------|------|
| `Error: permission denied while trying to connect to the Docker daemon socket` | ユーザーが docker グループに属していない | `sudo usermod -aG docker $USER` で追加し、再ログイン |
| `Cannot connect to the Docker daemon` | Docker が起動していない | `sudo systemctl start docker` |
| イメージサイズが大きい | ベースイメージが heavy | `node:slim` や `alpine` を検討 |
| コンテナが停止する | CMD が終了 | `docker run -it` でシェルに入る、ログ確認 |

## 9. まとめ  
Docker は「コードと環境を一体化」し、開発・本番を同一に保つための強力なツールです。  
- まずは `docker run` で簡単にコンテナを起動し、イメージの存在感を実感。  
- 次に Dockerfile で自分専用のイメージを作り、再現性を確保。  
- 本番環境では Compose でサービスを統合し、CI/CD で自動化。  

上記の流れを踏めば、環境差に悩むことなくスムーズに開発・デプロイが行えます。ぜひ一度、手を動かして試してみてください。