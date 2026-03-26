# CI/CDパイプラインの構築方法 ― 実践ガイド

## 1. イントロダクション  
CI（継続的インテグレーション）とCD（継続的デリバリー/デプロイ）は、ソフトウェア品質向上とリリースサイクル短縮の基盤です。この記事では、実務でよく使われる**GitHub Actions + Docker + Kubernetes**を例に、パイプライン設計の手順を解説します。対象はエンジニアレベルで、数千行コードのマイクロサービスを想定しています。

## 2. 基本構成の設計  
| コンポーネント | 役割 |
|-----------------|------|
| **ソースリポジトリ** | コード管理、PRレビュー |
| **CIジョブ** | ビルド → ユニット／統合テスト |
| **Dockerイメージ** | 再現性のある実行環境 |
| **CDジョブ** | イメージプッシュ → K8sデプロイ |
| **Secrets管理** | APIキー・DB接続文字列 |
| **監視/アラート** | デプロイ後の稼働確認 |

> **ポイント**  
> - すべての環境で同一イメージを使うことで「動く環境は同じ」ことを保証。  
> - PRベースでテストを走らせ、Merge時にだけデプロイをトリガー。  

## 3. GitHub Actions での実装例  
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Build and Test
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker run --rm myapp:${{ github.sha }} ./run-tests
      - name: Push image
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - run: |
          docker push ghcr.io/${{ github.repository_owner }}/myapp:${{ github.sha }}
  deploy:
    needs: build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: K8s Deploy
        uses: azure/k8s-deploy@v1
        with:
          namespace: prod
          manifests: |
            k8s/deployment.yaml
          images: |
            ghcr.io/${{ github.repository_owner }}/myapp:${{ github.sha }}
          kubeconfig: ${{ secrets.KUBECONFIG }}
```

- **テスト失敗時はデプロイしない**（`if` 条件）。  
- `secrets` で認証情報を隠蔽。  

## 4. Dockerfile のベストプラクティス  
```dockerfile
# Stage 1: Build
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o /app/bin/myapp

# Stage 2: Runtime
FROM gcr.io/distroless/base
WORKDIR /
COPY --from=builder /app/bin/myapp /app
CMD ["/app/myapp"]
```
- **マルチステージ**でイメージサイズを抑える。  
- `distroless` で攻撃面を縮小。  

## 5. Kubernetes へのデプロイ  
`k8s/deployment.yaml` は以下のように書くと、CIジョブでビルドしたイメージを自動的に参照できます。  

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: ghcr.io/yourorg/myapp:{{ .Values.image.tag }}
        ports:
        - containerPort: 8080
```

HelmやKustomizeを併用すれば、環境ごとの差分管理が容易になります。

## 6. 監視とロールバック  
- **Prometheus + Grafana** で稼働状況を可視化。  
- **Argo Rollouts** を使えば、Canary デプロイや自動ロールバックが可能。  

## 7. よくある落とし穴と対策  
| 落とし穴 | 原因 | 対策 |
|----------|------|------|
| **Secretsが漏れる** | 環境変数をファイルに出力 | GitHub Actions の `secrets` を必ず使う |
| **ビルド時間が長い** | 不要ファイルのコンテキスト | `.dockerignore` を徹底 |
| **デプロイ失敗** | 依存サービス未起動 | Helm Hooks で依存関係を待機 |

## 8. まとめ  
1. **設計フェーズ**で「どの環境で何をテストするか」を明確化。  
2. **Dockerイメージの再現性**と**K8sの宣言的構成**を組み合わせる。  
3. **GitHub Actions** はワークフローを簡潔に保ちながら、Secrets管理・パラレル実行もサポート。  
4. **監視とロールバック**を組み込むことで、障害時の迅速復旧が可能。  

これらを踏まえて、まずは小さなサンプルプロジェクトでCI/CDを構築し、徐々にスケールさせていくのが成功の鍵です。ぜひ試してみてください！