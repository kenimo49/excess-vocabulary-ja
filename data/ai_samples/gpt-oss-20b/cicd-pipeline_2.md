# CI/CDパイプラインの構築方法

## はじめに  
ソフトウェア開発のスピードと品質を両立させるために不可欠なのが CI（継続的インテグレーション）と CD（継続的デリバリー/デプロイ）です。本記事では、実践的なパイプライン構築手順とベストプラクティスを解説します。  

## CI/CD とは  
- **CI**: コミットごとにビルドとテストを自動化し、早期に問題を検出。  
- **CD**: ビルドが成功したら自動でステージング/本番へデプロイ。  

これにより「コードの変更 → 自動テスト → 自動デプロイ」のサイクルが短縮され、リリース頻度が向上します。  

## 主要なツール  
| ツール | 特徴 |
|--------|------|
| **GitHub Actions** | GitHubと統合、無料枠あり。 |
| **GitLab CI** | GitLabリポジトリに組み込み。 |
| **Jenkins** | 柔軟なプラグインエコシステム。 |
| **CircleCI** | 高速なビルド、簡易設定。 |

本記事では **GitHub Actions** を例にします。  

## パイプライン設計のポイント  
1. **分離** – ビルド・テスト・デプロイを別ジョブに分ける。  
2. **並列化** – テストを並列実行し、時間短縮。  
3. **キャッシュ** – 依存パッケージをキャッシュしビルド時間を削減。  
4. **セキュリティ** – シークレットは環境変数で管理。  

## 実際の構築例（GitHub Actions）  
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.build.outputs.image_tag }}
    steps:
      - uses: actions/checkout@v3
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
      - name: Cache Maven packages
        uses: actions/cache@v3
        with:
          path: ~/.m2/repository
          key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
      - name: Build with Maven
        run: mvn -B package --file pom.xml
      - name: Build Docker image
        id: build
        run: |
          IMAGE_TAG=${GITHUB_SHA:0:7}
          docker build -t myapp:${IMAGE_TAG} .
          echo "::set-output name=image_tag::${IMAGE_TAG}"
  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: mvn test
  deploy-staging:
    needs: [build, test]
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Kubernetes
        env:
          KUBE_CONFIG_DATA: ${{ secrets.KUBE_CONFIG_STAGING }}
        run: |
          echo "${KUBE_CONFIG_DATA}" | base64 -d > kubeconfig
          kubectl --kubeconfig kubeconfig set image deployment/myapp myapp=${{ needs.build.outputs.image_tag }}
          kubectl --kubeconfig kubeconfig rollout status deployment/myapp
```

### 重要ポイント  
- **キャッシュ** で Maven 依存を再利用。  
- **Dockerイメージタグ** をコミット SHA の先頭7文字に設定し、追跡性を確保。  
- **環境変数** に Kubeconfig を格納し、セキュアにデプロイ。  

## テストと品質保証  
- **ユニットテスト**: 変更箇所に対して必須。  
- **統合テスト**: Docker Compose でサービスを起動し、エンドツーエンドを検証。  
- **コードカバレッジ**: `codecov` などでレポートを GitHub に表示。  
- **静的解析**: `sonarcloud` を CI に組み込み、コード品質を監視。  

## デプロイ戦略  
- **Blue/Green**: 新旧環境を並行で稼働し、切替時のダウンタイムを最小化。  
- **Canary**: 小規模ユーザーに先行リリースし、問題を検知。  
- **Rollback**: ステータスチェックに失敗したら自動で前バージョンへ戻すスクリプトを用意。  

## 監視とロールバック  
- **Prometheus + Grafana** で稼働状況を可視化。  
- **Kubernetes の liveness / readiness probe** で異常検知。  
- **SRE の SLO/SLA** を設定し、問題発生時のアラートを自動化。  

## まとめ  
CI/CD パイプラインは「自動化」「可視化」「安全性」の三拍子で構築されます。  
1. コミットごとにビルド・テストを走らせる。  
2. 成功したビルドを安全にステージング、本番へデプロイ。  
3. 監視とロールバックを備えてリスクを最小化。  

この記事で紹介した GitHub Actions の例をベースに、プロジェクトに合わせて調整すれば、開発サイクルを高速化しつつ品質も維持できます。ぜひ自動化の一歩を踏み出してください。