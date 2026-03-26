# CI/CDパイプラインの構築方法：GitHub ActionsとDockerを使った実践ガイド

## はじめに

現代のソフトウェア開発において、CI/CD（継続的インテグレーション/継続的デリバリー）は欠かせない要素となっています。本記事では、GitHub ActionsとDockerを使用して、実践的なCI/CDパイプラインを構築する方法を解説します。

## CI/CDとは

**CI（Continuous Integration）**：開発者が頻繁にコードをメインブランチに統合し、自動的にビルドやテストを実行するプラクティス

**CD（Continuous Delivery/Deployment）**：CIで検証されたコードを本番環境に自動的または半自動的にデプロイするプロセス

## 必要な準備

- GitHubアカウント
- Dockerの基礎知識
- Node.js（サンプルアプリケーション用）

## ステップ1：プロジェクトの準備

まず、シンプルなNode.jsアプリケーションを作成します。

```javascript
// app.js
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello CI/CD!' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
```

```json
// package.json
{
  "name": "ci-cd-demo",
  "version": "1.0.0",
  "scripts": {
    "start": "node app.js",
    "test": "jest",
    "test:coverage": "jest --coverage"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "jest": "^29.5.0",
    "supertest": "^6.3.3"
  }
}
```

## ステップ2：テストの作成

```javascript
// app.test.js
const request = require('supertest');
const express = require('express');

describe('API Tests', () => {
  let app;
  
  beforeEach(() => {
    app = require('./app');
  });

  test('GET / should return message', async () => {
    const response = await request(app).get('/');
    expect(response.status).toBe(200);
    expect(response.body.message).toBe('Hello CI/CD!');
  });

  test('GET /health should return healthy status', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body.status).toBe('healthy');
  });
});
```

## ステップ3：Dockerfileの作成

```dockerfile
# Dockerfile
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
CMD ["node", "app.js"]
```

## ステップ4：GitHub Actionsワークフローの設定

`.github/workflows/ci-cd.yml`を作成します：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  DOCKER_IMAGE: ${{ secrets.DOCKER_HUB_USERNAME }}/ci-cd-demo
  
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
    
    - name: Generate coverage report
      run: npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_HUB_USERNAME }}
        password: ${{ secrets.DOCKER_HUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        push: true
        tags: |
          ${{ env.DOCKER_IMAGE }}:latest
          ${{ env.DOCKER_IMAGE }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DEPLOY_HOST }}
        username: ${{ secrets.DEPLOY_USER }}
        key: ${{ secrets.DEPLOY_KEY }}
        script: |
          docker pull ${{ env.DOCKER_IMAGE }}:${{ github.sha }}
          docker stop ci-cd-demo || true
          docker rm ci-cd-demo || true
          docker run -d --name ci-cd-demo -p 80:3000 \
            ${{ env.DOCKER_IMAGE }}:${{ github.sha }}
```

## ステップ5：シークレットの設定

GitHubリポジトリの設定で以下のシークレットを追加：

- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_KEY`

## ベストプラクティス

### 1. ブランチ戦略
- `main`ブランチは本番環境へのデプロイ
- `develop`ブランチは開発環境へのデプロイ
- フィーチャーブランチからのPRは必須

### 2. セキュリティ
- シークレット情報は必ずGitHub Secretsを使用
- 最小権限の原則を適用
- 定期的な依存関係の更新

### 3. パフォーマンス最適化
```yaml
# キャッシュの活用例
- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-
```

### 4. 通知の設定
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## まとめ

本記事では、GitHub ActionsとDockerを使用したCI/CDパイプラインの構築方法を解説しました。このパイプラインにより、コードの品質を保ちながら、安全かつ迅速なデプロイが可能になります。

重要なポイント：
- 自動テストで品質を担保
- Dockerによる環境の統一
- GitHub Actionsによる自動化
- セキュリティを考慮した設計

この基本的なパイプラインをベースに、プロジェクトの要件に応じてカスタマイズしていくことで、より堅牢な開発フローを構築できます。