# モダンなCI/CDパイプラインの構築方法 - GitHub ActionsとDockerを使った実践ガイド

## はじめに

継続的インテグレーション/継続的デリバリー（CI/CD）は、現代のソフトウェア開発において必要不可欠な要素となっています。本記事では、GitHub ActionsとDockerを使用したCI/CDパイプラインの構築方法を、実践的な例を交えて解説します。

## CI/CDパイプラインとは

CI/CDパイプラインは、コードの変更から本番環境へのデプロイまでを自動化する一連のプロセスです。

- **CI（継続的インテグレーション）**: コードの変更を頻繁にメインブランチに統合し、自動テストを実行
- **CD（継続的デリバリー/デプロイ）**: テストに合格したコードを自動的にステージング環境や本番環境にデプロイ

## 基本的なパイプラインの構成要素

効果的なCI/CDパイプラインには以下の要素が含まれます：

1. **ソースコード管理**: Git/GitHub
2. **ビルド**: アプリケーションのコンパイル/パッケージング
3. **テスト**: 単体テスト、統合テスト、E2Eテスト
4. **セキュリティスキャン**: 脆弱性チェック
5. **デプロイ**: 各環境への自動配布

## GitHub Actionsを使った実装例

### 1. 基本的なワークフローファイルの作成

`.github/workflows/ci-cd.yml`を作成します：

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
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }}
          ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max

  security-scan:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }}
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  deploy-staging:
    needs: [build, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
    - name: Deploy to Staging
      run: |
        echo "Deploying to staging environment"
        # ここに実際のデプロイコマンドを記述
        # 例: kubectl set image deployment/myapp myapp=${{ secrets.DOCKER_USERNAME }}/${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }}

  deploy-production:
    needs: [build, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://myapp.example.com
    steps:
    - name: Deploy to Production
      run: |
        echo "Deploying to production environment"
        # ここに実際のデプロイコマンドを記述
```

### 2. Dockerfileの例

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
USER node
CMD ["node", "index.js"]
```

## ベストプラクティス

### 1. **ブランチ戦略の採用**
- Git Flowまたは GitHub Flowを使用
- 本番ブランチ（main）とステージングブランチ（develop）を分離

### 2. **環境変数とシークレットの管理**
```yaml
env:
  NODE_ENV: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
  API_KEY: ${{ secrets.API_KEY }}
```

### 3. **キャッシュの活用**
- Docker layer caching
- 依存関係のキャッシュ
- ビルド成果物のキャッシュ

### 4. **並列実行とジョブの依存関係**
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

### 5. **通知とモニタリング**
```yaml
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  if: always()
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## セキュリティの考慮事項

1. **最小権限の原則**: 各ステップに必要最小限の権限のみを付与
2. **シークレットの暗号化**: GitHub Secretsを使用
3. **依存関係の定期的な更新**: Dependabotの活用
4. **コンテナイメージのスキャン**: Trivyなどのツールを使用

## まとめ

CI/CDパイプラインの構築は、開発効率とコード品質を大幅に向上させます。本記事で紹介したGitHub Actionsの設定をベースに、プロジェクトの要件に合わせてカスタマイズしていくことをお勧めします。

重要なのは、小さく始めて徐々に改善していくことです。まずは基本的なテストとビルドから始め、必要に応じてセキュリティスキャンやデプロイの自動化を追加していきましょう。

## 参考リンク

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [The Twelve-Factor App](https://12factor.net/)