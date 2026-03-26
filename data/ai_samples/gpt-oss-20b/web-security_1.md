# Webアプリケーションのセキュリティ対策 ― エンジニア向け実践ガイド

Webアプリは外部と直接やり取りするため、攻撃対象になることが多いです。  
本稿では、**開発・運用に携わるエンジニアが実際に取り組める対策**を中心に解説します。  
長さは約 1,500 文字（約 2,400 語）で、Markdown 形式にまとめます。

---

## 1. まずは「OWASP Top 10」を把握しよう

| # | カテゴリ | 代表的な脅威 | 典型的な対策 |
|---|---|---|---|
| 1 | A1: Injection | SQLi, OS コマンドインジェクション | パラメータ化クエリ、ORM 使用 |
| 2 | A2: Broken Authentication | パスワードの弱さ、セッションハイジャック | MFA、パスワードポリシー、JWT の安全設計 |
| 3 | A3: Sensitive Data Exposure | 暗号化されていない通信・ストレージ | TLS、AES 256 で暗号化 |
| 4 | A4: XML External Entities | XXE | XML パーサーで外部エンティティ無効化 |
| 5 | A5: Broken Access Control | 権限チェック漏れ | RBAC の厳格化、ACL の自動検証 |
| 6 | A6: Security Misconfiguration | デフォルト設定残存 | Docker コンテナイメージの再ビルド、不要ポート停止 |
| 7 | A7: Cross‑Site Scripting | XSS | エスケープ、Content‑Security‑Policy |
| 8 | A8: Insecure Deserialization | 任意コード実行 | シリアライズ不要、署名付き |
| 9 | A9: Using Components with Known Vulnerabilities | ライブラリ脆弱性 | Dependabot などで自動更新 |
|10 | A10: Insufficient Logging & Monitoring | 侵入検知遅延 | ELK スタックでログ収集、SIEM 連携 |

**実務での一歩**  
- プロジェクト初期に「OWASP Top 10」チェックリストを作成し、開発フローに組み込む。  
- CI のビルド時に `npm audit`, `pip-audit`, `cargo audit` などで依存関係の脆弱性を自動検出。  

---

## 2. 認証・認可を安全に設計する

### 2.1. パスワードは必ずハッシュ化
- `bcrypt`/`argon2` を使用。  
- **salt** は各ユーザーでランダムに生成し、ハッシュに結合。

### 2.2. MFA を導入
- TOTP (Google Authenticator 等) を推奨。  
- `authenticator-app` へのリンクを自動生成し、設定を簡易化。

### 2.3. セッション管理
- HttpOnly, Secure フラグ付き Cookie を必須。  
- `SameSite=Lax` か `Strict` を設定し、CSRF を軽減。  
- セッション ID は十分なランダム性を確保（≥ 128bit）。

---

## 3. 脆弱性入力検証の実装

### 3.1. サーバーサイドで必ずバリデーション
- フロントエンドのチェックは UI 向けに留め、**サーバーサイドで再検証**。  
- スキーマ検証ツール（Zod, Joi, pydantic など）を使うと一貫性が保てる。

### 3.2. エスケープとサニタイズ
- 出力時に必ずエスケープ（HTML, JS, CSS, SQL）。  
- テンプレートエンジンは自動エスケープ機能を有効化。

---

## 4. 通信層のセキュリティ

### 4.1. HTTPS を必須に
- Let's Encrypt で無料の SSL/TLS 証明書を取得。  
- HTTP → HTTPS リダイレクトをサーバー側で行う。

### 4.2. HSTS, CSP, X‑Frame‑Options
- `Strict-Transport-Security` でブラウザに HTTPS のみを許可。  
- `Content-Security-Policy` を設定し、外部リソースの読み込みを制限。  
- `X-Frame-Options: DENY` でクリックジャッキング対策。

---

## 5. 設定と運用の安全化

### 5.1. コンテナ／クラウド設定
- Docker イメージは `FROM scratch` か公式ベースイメージを利用し、不要パッケージは削除。  
- `docker-compose.yml` で環境変数は `.env` ファイルに格納し、Git へのコミットはしない。  
- AWS / GCP では IAM ロールを最小権限で付与。

### 5.2. 秘密情報管理
- HashiCorp Vault、AWS Secrets Manager、Azure Key Vault などで機密情報を管理。  
- アプリコード内で環境変数ではなく、秘密情報管理サービスから取得。

---

## 6. ログと監視

- **集中ログ**: Docker から Fluentd → Elasticsearch → Kibana (ELK)。  
- **異常検知**: シグネチャベースと機械学習ベースの SIEM を併用。  
- **ログのレベル**: `INFO` で正常、`WARN` で疑わしい動作、`ERROR` で失敗。  
- **ログのローテーション**: 1GB 以上でローテート、保持期間は規定に従う。

---

## 7. CI/CD パイプラインにセキュリティを組み込む

| ステップ | 実施内容 |
|---|---|
| Build | 依存関係の脆弱性スキャン、ビルド結果のスキャン（Trivy, Snyk） |
| Test | セキュリティテスト（OWASP ZAP スキャナー、Static Analysis） |
| Deploy | IaC (Terraform, CloudFormation) で構成管理、Secrets を注入 |
| Monitor | デプロイ後に継続的な脆弱性チェックと自動修正パッチ適用 |

---

## 8. まとめ

| 項目 | 重要ポイント |
|---|---|
| **脆弱性リスト** | OWASP Top 10 を前提に設計 |
| **認証・認可** | パスワードハッシュ、MFA、Cookie セキュリティ |
| **入力検証** | サーバーサイドでバリデーション・エスケープ |
| **通信層** | HTTPS, HSTS, CSP で外部攻撃を防止 |
| **運用** | Secrets 管理、最小権限、コンテナ最小化 |
| **監視** | 集中ログ＋SIEM、異常検知 |
| **CI/CD** | 自動脆弱性スキャン、IaC で構成管理 |

> **「セキュリティは一度設定したら終わり」**という誤解は大きなリスクです。  
> 常に最新の脆弱性情報をチェックし、コードベースや運用フローを改善し続けることが、安心できる Web アプリケーションを作る鍵となります。

---

> **実際の開発で**  
> 1. まずは **OWASP Top 10** をリスト化し、各項目に対して具体的な対策を決める。  
> 2. CI パイプラインに `npm audit`, `trivy`, `zap` などを組み込む。  
> 3. デプロイ前に必ず **セキュリティレビュー** を実施。  

このフレームワークをベースにプロジェクトに合わせてカスタマイズすれば、エンジニア全員が「安全設計」に関与しやすくなります。ぜひ実装に取り組んでみてください。