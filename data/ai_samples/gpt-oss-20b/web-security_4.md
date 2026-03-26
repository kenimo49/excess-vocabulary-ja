# Webアプリケーションのセキュリティ対策 ― エンジニア向け実践ガイド

Webアプリは「情報を外部に公開しつつ、内部ロジックを安全に保つ」というジレンマを抱えています。実際に稼働させる際に「ゼロデイ」「SQLインジェクション」「XSS」などといった脆弱性に対して、どのように防御を組み込むかが重要です。本稿では、エンジニアがすぐに実装できる対策を、OWASP Top 10 を軸に解説します。

> **読者層**: バックエンド／フロントエンド開発者、DevOps エンジニア  
> **前提知識**: HTTP/HTTPS, REST API, 基本的なプログラミング（Python/JavaScript など）  
> **目的**: コード例と共に「何が危険か」「どう防げるか」を明示し、実装時のヒントを提供

---

## 1. 何が危険か ― OWASP Top 10 をざっくり見る

| 番号 | 項目 | 代表的な脆弱性 | 典型的な攻撃シナリオ |
|------|------|----------------|----------------------|
| 1 | Injection | SQLi, NoSQLi, OSコマンドインジェクション | 未検証入力をそのままクエリに埋め込む |
| 2 | Broken Authentication | セッションハイジャック, パスワード漏洩 | Cookie の盗聴、弱いパスワード |
| 3 | Sensitive Data Exposure | 暗号化不備, パスワードハッシュ | クリアテキストで送信、ハッシュ化されていないパスワード |
| 4 | XML External Entities (XXE) | 外部エンティティの読み取り | XML パーサが外部ファイルを解釈 |
| 5 | Broken Access Control | 不正アクセス許可 | 認証済みユーザーが他ユーザーのリソースを閲覧 |
| 6 | Security Misconfiguration | デフォルト設定のまま | デバッグモード有効、管理画面公開 |
| 7 | Cross‑Site Scripting (XSS) | 悪意あるスクリプト埋め込み | コメント欄に `<script>` を投げ込む |
| 8 | Insecure Deserialization | 変更可能なオブジェクトの直列化 | 直列化データを改ざんしてサーバに投げる |
| 9 | Using Components with Known Vulnerabilities | 依存ライブラリの脆弱性 | 依存パッケージが古い |
| 10 | Insufficient Logging & Monitoring | 監査証跡の欠如 | 攻撃を検知できない |

これらを網羅的に防御するために、以下の「防御レイヤー」を実装することが推奨されます。

---

## 2. 防御レイヤー ― 基本設計のチェックリスト

| レイヤー | 実装ポイント | 例（Python/Flask） |
|----------|--------------|--------------------|
| **入力検証** | 正規表現・サニタイズ | `re.compile(r'^[A-Za-z0-9]+$')` |
| **パラメータ化クエリ** | PreparedStatement | `cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))` |
| **CSRF 防御** | トークン（SameSite） | `session['csrf_token'] = secrets.token_urlsafe()` |
| **セキュア Cookie** | `Secure`, `HttpOnly`, `SameSite` | `Set-Cookie: session=...; Secure; HttpOnly; SameSite=Strict` |
| **HTTPS 強制** | HSTS | `app.config['PREFERRED_URL_SCHEME'] = 'https'` |
| **エラーハンドリング** | スタックトレース隠蔽 | `abort(500)` |
| **暗号化** | TLS、AES-GCM | `ssl.create_default_context()` |
| **アクセス制御** | RBAC、ACL | `@login_required` デコレータ |
| **ログ** | 監査証跡 | `logging.getLogger('audit').info(...)` |

### 例：入力検証 + パラメータ化クエリ

```python
import re
import sqlite3
from flask import request, abort

# ① 正規表現で検証
username = request.form.get('username', '')
if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
    abort(400, 'Invalid username')

# ② パラメータ化クエリで SQLi 防御
conn = sqlite3.connect('app.db')
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE username = ?", (username,))
user = cur.fetchone()
```

---

## 3. 実装パターン ― よくあるケースでの対策

### 3-1. XSS 防御

| シナリオ | 防御策 | 実装例 |
|----------|--------|--------|
| フロント側で表示 | エスケープ | `{{ user_input | e }}` (Jinja2) |
| JSON で返却 | `JSON.stringify` で自動エスケープ | `res.json({msg: userInput})` |
| 画像アップロード | MIME タイプ検証 | `if content_type.startswith('image/')` |

> **ポイント**: すべてのユーザー生成コンテンツは「入力時」ではなく「出力時」にエスケープする。

### 3-2. CSRF 防御

| 方法 | 概要 | 例 |
|------|------|----|
| 同期トークン | フォームに hidden フィールド | `<input type="hidden" name="csrf_token" value="{{ csrf_token }}">` |
| SameSite Cookie | ブラウザ側で CSRF を防止 | `Set-Cookie: session=...; SameSite=Lax` |

> **実装コツ**: `django.middleware.csrf.CsrfViewMiddleware` や `Flask-WTF` などフレームワークに組み込まれている機能を利用すると手軽です。

### 3-3. 依存パッケージの脆弱性対策

- `npm audit`, `pip audit`, `bundle audit` で定期的にチェック
- `Dependabot` や `Renovate` を CI に組み込む
- `Snyk` で自動修正を検証

---

## 4. 監査と自動化 ― DevSecOps で継続的に防御を

1. **CI/CD Pipeline**  
   - 静的解析（`SonarQube`, `Bandit`）  
   - 動的解析（`OWASP ZAP`, `Burp Suite`）  
   - コンテナイメージの脆弱性スキャン（`Trivy`, `Clair`）

2. **ロギングとアラート**  
   - `ELK`/`EFK` で集中管理  
   - `fail2ban` でブロックリストに追加

3. **脆弱性情報共有**  
   - **OWASP Top 10** をチーム共有  
   - **脆弱性情報共有**：`CVE` データベースを定期チェック

---

## 5. まとめ

- **入力検証** と **パラメータ化クエリ** は最優先。  
- **HTTPS**、**Secure Cookie**、**SameSite**、**HSTS** で通信とセッションを守る。  
- **XSS**, **CSRF** は「出力時」エスケープとトークンで防御。  
- 依存ライブラリは常に最新化し、脆弱性情報を監視。  
- CI/CD に **静的・動的解析** を組み込み、継続的なセキュリティを確保。

「セキュリティは最後に付け足すもの」ではなく、設計段階から組み込むべきです。実装を始める前に、上記のチェックリストを必ずレビューし、CI パイプラインに組み込むことで、プロダクション環境に不具合を持ち込むリスクを大幅に削減できます。ぜひ、今日から「コードに安全を詰め込む」習慣を取り入れてみてください。