# Webアプリケーションのセキュリティ対策 – エンジニア向け実践ガイド

## はじめに  
Webアプリは常に外部からの攻撃対象になり得ます。小さなミスが情報漏えいやサービス停止へとつながるため、**設計段階からセキュリティを組み込むこと**が必須です。ここでは、エンジニアがすぐに実装できる対策を、OWASP Top 10 を基にまとめました。

---

## 1. 主要脅威と対策（OWASP Top 10）

| # | 脅威 | 主な対策 |
|---|------|-----------|
| 1 | **Injection** (SQL, OS, NoSQL) | パラメータ化クエリ／プリペアドステートメントを使用。入力をサニタイズし、ORM の安全なメソッドを採用。 |
| 2 | **Broken Authentication** | 多要素認証 (MFA)、パスワードハッシュは `bcrypt` / `argon2`、ログイン試行制限。 |
| 3 | **Sensitive Data Exposure** | TLS 1.3 の強制、暗号化ストレージ、パスワードはハッシュ化のみ保存。 |
| 4 | **XML External Entities (XXE)** | XML パーサは外部エンティティを無効化。 |
| 5 | **Broken Access Control** | RBAC / ABAC を実装し、サーバ側でアクセス権を検証。 |
| 6 | **Security Misconfiguration** | デフォルト設定を最小限にし、不要機能は削除。 |
| 7 | **Cross‑Site Scripting (XSS)** | 出力エスケープ、Content‑Security‑Policy (CSP) を設定。 |
| 8 | **Insecure Deserialization** | 受信データはバリデーションし、シリアライズは安全なライブラリを使用。 |
| 9 | **Using Components with Known Vulnerabilities** | 依存ライブラリを常に最新に保ち、自動スキャン（GitHub Dependabot 等）を活用。 |
|10 | **Insufficient Logging & Monitoring** | 監査ログを保存し、SIEM で異常検知。 |

---

## 2. コードレベルでの実装例

### 2‑1 パラメータ化クエリ（Node.js + PostgreSQL）

```js
const { Client } = require('pg');
const client = new Client();
await client.connect();

const userId = req.params.id;
const res = await client.query(
  'SELECT * FROM users WHERE id = $1', [userId]
);
```

### 2‑2 CSRF 対策（Express + csurf）

```js
const csrf = require('csurf');
app.use(csrf({ cookie: true }));

app.get('/form', (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});
```

### 2‑3 CSP ヘッダー設定（Nginx）

```
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'nonce-abc123';";
```

---

## 3. 開発フローに組み込む

1. **コードレビュー**：安全性のチェックリストを設ける。  
2. **CI/CD パイプライン**：`npm audit`、`OWASP ZAP` など自動テストを走らせる。  
3. **脆弱性スキャン**：定期的に外部ツール（Snyk, Nessus）で脆弱性を検知。  
4. **監視**：ログを ELK / Loki で収集し、異常検知ルールを構築。  

---

## 4. まとめ

- **設計段階から** セキュリティを意識する。  
- **OWASP Top 10** を参照し、主要脅威に対する対策を必ず実装。  
- **自動化**（CI/CD, スキャン）で継続的に脆弱性を抑制。  
- **監査ログ** と **異常検知** を通じて、インシデント発生時に迅速に対応。

エンジニア同士で「安全なコーディング」を共有し、堅牢な Web アプリを作り上げましょう。