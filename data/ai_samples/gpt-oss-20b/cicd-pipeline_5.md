# CI/CDパイプラインの構築方法

## 1. はじめに  
ソフトウェア開発のスピードが速まる中、**継続的インテグレーション (CI)** と **継続的デリバリ／デプロイ (CD)** は欠かせない工程です。  
この記事では、エンジニア向けにCI/CDパイプラインの設計・実装手順を「GitHub Actions + Docker + Kubernetes」を例にまとめます。  

---

## 2. CI/CD の基本概念  
| 用語 | 目的 |
|------|------|
| **CI** | コミットごとにビルド・テストを自動実行し、品質を早期に検証 |
| **CD** | 成功したビルドを自動でデプロイ、環境間での差異を最小化 |

パイプラインは「ソース取得 → ビルド → テスト → イメージ化 → デプロイ → 監視」といったステップで構成されます。

---

## 3. ツール選定ポイント  
| 分類 | 代表ツール | 特徴 |
|------|-----------|------|
| **ソース管理** | GitHub, GitLab | 変更履歴管理 |
| **CI** | GitHub Actions, GitLab CI, Jenkins | プラグイン自由度、ビルトイン |
| **ビルド** | Docker | コンテナイメージ化 |
| **レジストリ** | Docker Hub, GitHub Packages, ECR | シークレット管理 |
| **デプロイ** | Kubernetes, Helm, ArgoCD | 自動ロールアウト、ロールバック |
| **監視** | Prometheus, Grafana, Loki | メトリクス・ログ |

---

## 4. 実装手順（GitHub Actions + Docker + K8s）

### 4.1. リポジトリ構成  
```
├─ src/          # アプリコード
├─ Dockerfile    # コンテナビルド
├─ helm/         # K8s Helmチャート
├─ .github/
│  └─ workflows/
│     └─ ci-cd.yml   # CI/CDワークフロー
```

### 4.2. ワークフローファイル (`ci-cd.yml`)  
```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    - name: Build & Test
      run: |
        docker build -t myapp:latest .
        # テストコマンド例
        docker run --rm myapp:latest npm test

  publish:
    needs: build-test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Log in to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DH_USER }}
        password: ${{ secrets.DH_PASS }}
    - name: Build & Push
      run: |
        docker build -t myapp:${{ github.sha }} .
        docker push myapp:${{ github.sha }}

  deploy:
    needs: publish
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
    - name: Deploy to K8s
      run: |
        helm upgrade --install myapp ./helm \
          --set image.tag=${{ github.sha }} \
          --namespace prod
```

- **ビルドとテスト**  
  - `docker build` でイメージ化  
  - `npm test` などでユニット・統合テスト実行  

- **レジストリへのプッシュ**  
  - シークレット (`DH_USER`, `DH_PASS`) で認証  
  - SHA をタグにしてバージョン管理  

- **デプロイ**  
  - Helm でチャートをアップグレード  
  - `image.tag` にビルド SHA を渡す  

### 4.3. 環境変数とシークレット管理  
- **`.env`** や **ConfigMap** で設定値を分離  
- **GitHub Secrets** で機密情報を保持し、`secrets.` で参照  

### 4.4. ブランチ戦略  
- **Feature ブランチ** → PR → CI  
- **main** → マージ → 自動CD  
- **release ブランチ** でバージョンタグ付与  

---

## 5. 重要ポイントとベストプラクティス  

| 項目 | 推奨策 |
|------|--------|
| **ビルド時間** | キャッシュ（Docker BuildKit）を活用 |
| **テスト網羅** | すべてのマージ前にユニット＋統合テスト |
| **ロールバック** | Helm の `--rollback` を自動化 |
| **監視** | Prometheus + Loki で異常検知 |
| **通知** | Slack/Teams へのデプロイ失敗メッセージ |

---

## 6. よくある落とし穴  

1. **レジストリ認証失敗**  
   - シークレット漏れを防ぐため、環境別に別々のレジストリを使用する。  

2. **テスト不完全**  
   - コードカバレッジをチェックし、低い場合はテスト追加。  

3. **デプロイ失敗時の通知不足**  
   - `failure()` でステップを失敗させ、通知を設定。  

4. **環境差異**  
   - `kubeconfig` をCIで安全に取得し、テスト環境と本番環境を明確に分離。  

---

## 7. まとめ  
CI/CDパイプラインは「自動化」「安全性」「可視化」の三要素を兼ね備える必要があります。  
GitHub Actions でビルド・テストを、Docker でイメージ化し、Kubernetes でデプロイする構成は、設定が比較的簡潔で拡張性も高いため、実務導入がしやすいモデルです。  

パイプラインを構築したら、実際に運用しながら **メトリクス** を収集し、改善サイクルを回すことが重要です。  

> **実装の際のチェックリスト**  
> - CIはすべてのコミットで走るか  
> - ビルドキャッシュは有効か  
> - テストは必ず失敗時にパイプラインを停止するか  
> - デプロイはロールアウト戦略を持つか  
> - ログ・メトリクスは可視化されているか  

これらを意識して構築すれば、安定した高速デリバリが実現できます。 Happy Coding!