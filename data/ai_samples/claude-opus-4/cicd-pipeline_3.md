# 実践的なCI/CDパイプラインの構築ガイド

## はじめに

継続的インテグレーション/継続的デリバリー（CI/CD）は、現代のソフトウェア開発において不可欠な要素となっています。本記事では、GitHub ActionsとDockerを使用した実践的なCI/CDパイプラインの構築方法を解説します。

## CI/CDパイプラインとは

CI/CDパイプラインは、コードの変更から本番環境へのデプロイまでを自動化する一連のプロセスです。

### 主な構成要素

- **CI（継続的インテグレーション）**: コードの統合とテストを自動化
- **CD（継続的デリバリー/デプロイ）**: ビルドとデプロイを自動化

## 環境構築

### 必要なツール

```yaml
# 使用するツール一覧
- Git/GitHub
- Docker
- GitHub Actions
- Node.js（サンプルアプリケーション用）
```

## 実装手順

### 1. サンプルアプリケーションの準備

```javascript
// app.js
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello CI/CD!' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
```

```json
// package.json
{
  "name": "ci-cd-demo",
  "version": "1.0.0",
  "scripts": {
    "start": "node app.js",
    "test": "jest",
    "lint": "eslint ."
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  }
}
```

### 2. テストの作成

```javascript
// app.test.js
const request = require('supertest');
const app = require('./app');

describe('GET /', () => {
  it('should return Hello CI/CD message', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body.message).toBe('Hello CI/CD!');
  });
});
```

### 3. Dockerfileの作成

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
```

### 4. GitHub Actionsワークフローの設定

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Run linter
      run: npm run lint
      
    - name: Run tests
      run: npm test
      
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      
  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/app:latest
          ${{ secrets.DOCKER_USERNAME }}/app:${{ github.sha }}
          
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production server..."
        # ここに実際のデプロイコマンドを記述
        # 例: SSH接続、Kubernetes apply、AWS ECS更新など
```

## ベストプラクティス

### 1. ブランチ戦略

```yaml
# ブランチ保護ルールの例
main:
  - PRレビュー必須
  - CI/CDテスト合格必須
  - 直接プッシュ禁止
  
develop:
  - CI/CDテスト合格必須
  
feature/*:
  - developへのPRのみ許可
```

### 2. シークレット管理

```bash
# GitHub Secretsに登録
DOCKER_USERNAME
DOCKER_PASSWORD
DEPLOY_KEY
API_KEYS
```

### 3. キャッシュの活用

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

## モニタリングと通知

### Slackへの通知設定

```yaml
- name: Notify Slack
  if: always()
  uses: slack-notify@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## トラブルシューティング

### よくある問題と解決策

1. **権限エラー**: GitHubトークンの権限を確認
2. **タイムアウト**: ジョブの実行時間制限を調整
3. **キャッシュの問題**: キャッシュをクリアして再実行

## まとめ

CI/CDパイプラインの構築により、以下のメリットが得られます：

- **開発速度の向上**: 手動作業の削減
- **品質の向上**: 自動テストによる品質保証
- **デプロイの安定性**: 一貫性のあるデプロイプロセス

今回紹介した構成を基に、プロジェクトの要件に応じてカスタマイズしていくことで、より効果的なCI/CDパイプラインを構築できます。

## 参考リンク

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Docker Documentation](https://docs.docker.com/)
- [CI/CD Best Practices](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)