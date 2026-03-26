# 初心者でもできる！GitHub ActionsでCI/CDパイプラインを構築する方法

## はじめに

CI/CD（継続的インテグレーション/継続的デリバリー）は、現代のソフトウェア開発において欠かせないプラクティスです。本記事では、GitHub Actionsを使用して実践的なCI/CDパイプラインを構築する方法を解説します。

## CI/CDとは？

**CI（Continuous Integration）**：コードの変更を頻繁にメインブランチに統合し、自動テストを実行することで品質を保つ手法

**CD（Continuous Delivery/Deployment）**：テスト済みのコードを自動的に本番環境へデプロイする仕組み

## なぜGitHub Actions？

- GitHubとの統合が容易
- 豊富な事前定義アクション
- 無料枠が充実（パブリックリポジトリは無制限）
- YAMLベースの設定で学習コストが低い

## 実践：Node.jsアプリケーションのCI/CDパイプライン構築

### 1. プロジェクトの準備

まず、シンプルなNode.jsプロジェクトを用意します。

```json
// package.json
{
  "name": "ci-cd-demo",
  "version": "1.0.0",
  "scripts": {
    "test": "jest",
    "lint": "eslint .",
    "build": "webpack --mode production",
    "start": "node dist/index.js"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0",
    "webpack": "^5.0.0"
  }
}
```

### 2. GitHub Actionsワークフローの作成

`.github/workflows/ci-cd.yml`を作成します。

```yaml
name: CI/CD Pipeline

# トリガーの設定
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  # テストジョブ
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint
    
    - name: Run tests
      run: npm test -- --coverage
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        token: ${{ secrets.CODECOV_TOKEN }}

  # ビルドジョブ
  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18.x'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build application
      run: npm run build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist-files
        path: dist/

  # デプロイジョブ（mainブランチのみ）
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: dist-files
        path: dist/
    
    - name: Deploy to production
      env:
        DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
      run: |
        # デプロイスクリプトの例
        echo "Deploying to production..."
        # rsync -avz dist/ user@server:/var/www/app/
        # または、AWS S3へのデプロイ
        # aws s3 sync dist/ s3://my-app-bucket/
```

### 3. セキュリティとベストプラクティス

#### シークレットの管理
```yaml
- name: Deploy to AWS
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  run: |
    aws s3 sync dist/ s3://my-bucket/
```

#### 環境ごとの設定
```yaml
deploy-staging:
  if: github.ref == 'refs/heads/develop'
  environment:
    name: staging
    url: https://staging.myapp.com
  
deploy-production:
  if: github.ref == 'refs/heads/main'
  environment:
    name: production
    url: https://myapp.com
  needs: [test, build]
```

### 4. 高度な設定

#### 並列実行とキャッシュ
```yaml
- name: Cache node modules
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

#### 条件付き実行
```yaml
- name: Deploy only on tag
  if: startsWith(github.ref, 'refs/tags/')
  run: echo "Deploying version ${{ github.ref_name }}"
```

## トラブルシューティング

### よくある問題と解決策

1. **権限エラー**: `permissions`セクションで適切な権限を設定
2. **タイムアウト**: `timeout-minutes`で実行時間を調整
3. **依存関係の問題**: `npm ci`の使用とキャッシュの活用

## まとめ

GitHub Actionsを使用することで、簡単にCI/CDパイプラインを構築できます。重要なポイントは：

- 小さく始めて段階的に拡張する
- セキュリティを常に意識する
- キャッシュを活用してビルド時間を短縮する
- 環境ごとに適切な設定を行う

これらの基本を押さえれば、チームの生産性を大幅に向上させることができます。ぜひ自分のプロジェクトで試してみてください！

## 参考リンク

- [GitHub Actions公式ドキュメント](https://docs.github.com/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [CI/CDベストプラクティス](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)