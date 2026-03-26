# CI/CDパイプラインの構築方法  
**読者**: エンジニア  
**文字数**: 約1,500文字  

---

## 1. まずは「CI」と「CD」の本質を押さえる  
- **CI (Continuous Integration)**  
  - コミットごとにビルド・テストを自動化し、統合の障害を早期発見。  
- **CD (Continuous Delivery / Continuous Deployment)**  
  - ビルドが通った成果物を、ステージング／本番へ自動でデリバリー。  

CI/CDは「コードが**常に動く状態**」を保証するための文化とツールセットです。  

---

## 2. 典型的なパイプライン構成  
| ステージ | 主なタスク | 推奨ツール | 備考 |
|----------|------------|------------|------|
| コード取得 | Git fetch | GitHub, GitLab, Bitbucket | |
| ビルド | コンパイル・Dockerイメージ作成 | Maven, Gradle, Docker CLI | |
| テスト | 単体/統合テスト | JUnit, pytest, Testcontainers | |
| コード品質 | 静的解析・フォーマット | SonarQube, ESLint, PMD | |
| アーティファクト | バージョン管理・レジストリへpush | Nexus, GitHub Packages, Docker Hub | |
| デプロイ | ステージング/本番へデプロイ | Helm, kubectl, Terraform | |
| 監視 | SLA・ヘルスチェック | Prometheus, Grafana | |

---

## 3. ツール選定のポイント  
1. **CI/CDを自前で実装したいか？**  
   - **オープンソース**: Jenkins, GitLab CI, CircleCI。  
   - **サーバーレス**: GitHub Actions, GitLab CI/CD（Runnerをセルフホスト）。  

2. **IaC と統合したいか？**  
   - Terraform + GitHub Actions → **GitOps**。  

3. **コンテナベース**  
   - Dockerfile + BuildKit → **高速ビルド**。  
   - K8s 用 Helm Chart → **再現性あるデプロイ**。  

---

## 4. GitHub Actions での実装例  
以下は簡易的な CI/CD パイプライン例です。プロジェクトは Java + Docker です。

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: myorg/myapp

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build with Maven
        run: mvn -B package --file pom.xml

      - name: Build Docker image
        run: |
          docker build -t $REGISTRY/$IMAGE_NAME:$GITHUB_SHA .
          echo ${{ secrets.GITHUB_TOKEN }} | docker login $REGISTRY -u ${{ github.actor }} --password-stdin

      - name: Push image
        run: |
          docker push $REGISTRY/$IMAGE_NAME:$GITHUB_SHA
          docker tag $REGISTRY/$IMAGE_NAME:$GITHUB_SHA $REGISTRY/$IMAGE_NAME:latest
          docker push $REGISTRY/$IMAGE_NAME:latest

  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Set up kubectl
        uses: azure/setup-kubectl@v1
        with:
          version: 'latest'

      - name: Deploy to K8s
        run: |
          helm upgrade --install myapp ./helm-chart \
            --set image.repository=$REGISTRY/$IMAGE_NAME \
            --set image.tag=$GITHUB_SHA
```

### 重要ポイント
- **Secrets**: `GITHUB_TOKEN` で DockerHub/GHCR へ push。  
- **タグ付け**: `:latest` は必ず最新イメージに合わせる。  
- **条件付きデプロイ**: `if: github.ref == 'refs/heads/main'` で main ブランチのみデプロイ。  

---

## 5. ベストプラクティス  
| 項目 | 具体策 | 期待効果 |
|------|--------|----------|
| **分岐戦略** | Git Flow / Trunk Based Development | マージ衝突を最小化 |
| **テスト網羅率** | 90%以上のコードカバレッジ | バグ早期検出 |
| **パイプラインの分割** | Build / Test / Deploy を別ジョブに | 障害箇所を迅速に特定 |
| **キャッシュ活用** | Maven local repo, Docker layer cache | ビルド時間短縮 |
| **安全性** | Secrets を環境変数に | 機密情報漏洩防止 |

---

## 6. よくある落とし穴と対策  
| 落とし穴 | 原因 | 対策 |
|-----------|------|------|
| **CI が遅い** | 依存関係の再ビルド | キャッシュ設定、マルチステージ Docker |
| **デプロイ失敗** | 変数の誤設定 | Helm dry‑run、kube‑config の確認 |
| **Secrets が漏れ** | .env をコミット | secrets manager で管理、`.gitignore` を活用 |

---

## 7. まとめ  
CI/CD は「自動化で品質と速度を両立する」ための手段です。  
- **ツールはシンプルに**：まずは GitHub Actions で構築し、課題が出てきたら Jenkins や Argo CD に拡張。  
- **品質を可視化**：SonarQube、Grafana で継続的に改善。  
- **安全に**：Secrets を必ず暗号化し、最小権限で運用。  

これで、初めての CI/CD パイプライン構築に挑むエンジニアの一助となれば幸いです。 🚀  

--- 

> **さらに学びたい方へ**  
> - [GitHub Actions Docs](https://docs.github.com/en/actions)  
> - [Jenkins 入門](https://www.jenkins.io/doc/)  
> - [Helm 公式サイト](https://helm.sh/)  
> - [SonarQube](https://www.sonarqube.org/)  
> - [Argo CD](https://argo-cd.readthedocs.io/en/stable/)  

---