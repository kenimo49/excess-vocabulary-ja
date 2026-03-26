# CI/CDパイプラインの構築方法：GitHub ActionsとDockerを使った実践ガイド

## はじめに

現代のソフトウェア開発において、CI/CD（継続的インテグレーション/継続的デリバリー）パイプラインは欠かせない要素となっています。本記事では、GitHub ActionsとDockerを使用した実践的なCI/CDパイプラインの構築方法を解説します。

## CI/CDパイプラインとは

CI/CDパイプラインは、コードの変更から本番環境へのデプロイまでを自動化する仕組みです。

- **CI（継続的インテグレーション）**: コードの変更を頻繁にメインブランチに統合し、自動テストを実行
- **CD（継続的デリバリー/デプロイ）**: テストに合格したコードを自動的にステージング環境や本番環境にデプロイ

## 構築するパイプラインの全体像

今回構築するパイプラインは以下のステップで構成されます：

1. コードのチェックアウト
2. 依存関係のインストール
3. ユニットテストの実行
4. Dockerイメージのビルド
5. イメージのプッシュ
6. デプロイ

## 実装手順

### 1. GitHub Actionsワークフローファイルの作成

`.github/workflows/ci-cd.yml`ファイルを作成します：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  DOCKER_IMAGE: myapp
  DOCKER_TAG: ${{ github.sha }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run linter
        run: npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }}
            ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USERNAME }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            docker pull ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }}
            docker stop myapp || true
            docker rm myapp || true
            docker run -d --name myapp -p 80:3000 \
              ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }}
```

### 2. Dockerfileの作成

アプリケーションのルートディレクトリに`Dockerfile`を作成します：

```dockerfile
# マルチステージビルド
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
```

### 3. GitHub Secretsの設定

以下のSecretをGitHubリポジトリに設定します：

- `DOCKER_USERNAME`: Docker Hubのユーザー名
- `DOCKER_PASSWORD`: Docker Hubのパスワード
- `PRODUCTION_HOST`: 本番サーバーのホスト
- `PRODUCTION_USERNAME`: SSHユーザー名
- `PRODUCTION_SSH_KEY`: SSH秘密鍵

## ベストプラクティス

### 1. ブランチ戦略の活用

```yaml
on:
  push:
    branches:
      - main      # 本番環境へのデプロイ
      - develop   # 開発環境へのデプロイ
      - 'feature/*' # 機能ブランチでのテスト実行
```

### 2. キャッシュの活用

```yaml
- name: Cache node modules
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### 3. 並列実行の活用

```yaml
jobs:
  test-unit:
    runs-on: ubuntu-latest
    # ...
  
  test-integration:
    runs-on: ubuntu-latest
    # ...
  
  build:
    needs: [test-unit, test-integration]
    # ...
```

### 4. セキュリティスキャンの追加

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: '${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
```

## トラブルシューティング

### よくある問題と解決方法

1. **権限エラー**: GitHub ActionsのPERMISSIONSを確認
2. **Dockerビルドの失敗**: マルチステージビルドでのパス指定を確認
3. **デプロイの失敗**: SSH鍵の権限（600）を確認

## まとめ

CI/CDパイプラインの構築により、以下のメリットが得られます：

- コード品質の向上
- デプロイの自動化による作業効率化
- 本番環境への安全なリリース

今回紹介した構成をベースに、プロジェクトの要件に合わせてカスタマイズすることで、より効果的なCI/CDパイプラインを構築できます。

## 参考リンク

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Docker Documentation](https://docs.docker.com/)
- [CI/CD Best Practices](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)