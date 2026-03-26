# Webアプリケーションのセキュリティ対策 ― エンジニア向け実践ガイド

Webアプリは常に外部からの攻撃対象になり得ます。  
そのため「セキュリティ対策＝バグを後から修正する」ではなく、**開発フェーズから設計・実装・運用までを見通した一貫した対策**が必要です。本記事では、実際に開発で使える具体的な対策を、OWASP Top 10 などの業界標準と合わせて紹介します。

> **読者の前提**  
> • ある程度の Web 開発経験がある  
> • 言語は **JavaScript / Node.js**（または同等のフレームワーク）  
> • CI/CD 環境が整っている

---

## 1. まずは OWASP Top 10 を確認

| No. | 名前 | 主な攻撃手法 | 対策の概要 |
|-----|------|--------------|------------|
| 1 | A1:2023 Injection | SQL, NoSQL, OS コマンド | パラメータ化クエリ、ORM  |
| 2 | A2:2023 Broken Authentication | パスワード推測、セッション乗っ取り | MFA、セッションハンドリング |
| 3 | A3:2023 Sensitive Data Exposure | 暗号化不備、弱いハッシュ | TLS, AES-GCM, HMAC |
| 4 | A4:2023 XML External Entity | 外部エンティティ攻撃 | XML パーサー無効化 |
| 5 | A5:2023 Broken Authorization | 権限チェック漏れ | RBAC、最小権限 |
| 6 | A6:2023 Security Misconfiguration | デフォルト設定漏れ | 設定管理ツール、CI |
| 7 | A7:2023 Cross‑Site Scripting (XSS) | 文字列埋め込み | コンテキストエスケープ |
| 8 | A8:2023 Insecure Deserialization | オブジェクト再構築 | シリアライズの制御 |
| 9 | A9:2023 Using Components with Known Vulnerabilities | 依存ライブラリ | Snyk, Dependabot |
| 10 | A10:2023 Insufficient Logging & Monitoring | 不十分な監査 | WAF、ELK スタック |

> **ポイント**  
> ① 先ずは **脆弱性を列挙し**、それに対する一般的対策を把握する。  
> ② その上で **プロジェクト固有のリスク**を洗い出し、優先順位を決める。

---

## 2. 入力検証（Validation）と出力エンコーディング（Encoding）

### 2.1 バリデーションは「サーバー側で必ず」  
クライアント側でのチェックは UX 向上に有効だが、**必ずサーバー側で再チェック**する。  
例: Joi, Yup, Zod 等でスキーマを定義。

```ts
// 例: Node.js + Express + Zod
import { z } from "zod";

const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

app.post("/api/register", async (req, res) => {
  const parseResult = userSchema.safeParse(req.body);
  if (!parseResult.success) return res.status(400).json(parseResult.error);
  // 続く処理
});
```

### 2.2 エンコーディングは「コンテキストに応じて」  
HTML 出力は `text/html` エンコード、JSON は `application/json`。  
XSS を防ぐため、**サーバー側でエスケープ**する。

```html
<!-- Express + Pug -->
<p>Hello, #{user.name}!</p>
```

> **実践ヒント**  
> - `express-validator` + `helmet` で自動化  
> - `DOMPurify` などをフロント側で使用する場合は、サーバー側でも再エンコード

---

## 3. 認証・認可（Auth & Authz）

### 3.1 パスワードはハッシュ化＋ソルト  
- **bcrypt** / **argon2** を使う  
- `maxLength` で無制限入力を防止

```ts
import argon2 from "argon2";
await argon2.hash(password, { type: argon2.argon2id, memoryCost: 2 ** 16 });
```

### 3.2 MFA（多要素認証）  
- TOTP（Google Authenticator 等）  
- WebAuthn（パスワードレス）  

### 3.3 セッション管理  
- `httpOnly` + `secure` フラグ付き Cookie  
- `SameSite=Lax/Strict`  
- CSRF トークンは **同一サイト** か **SameSite** で代替可

```ts
app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  },
}));
```

### 3.4 RBAC / ABAC の設計  
- 役割ベースで **最小権限** を設計  
- 権限チェックは **ミドルウェア** で一元化

```ts
function authorize(role) {
  return (req, res, next) => {
    if (!req.user.roles.includes(role)) {
      return res.status(403).json({ error: "Forbidden" });
    }
    next();
  };
}
app.get("/admin", authorize("admin"), adminHandler);
```

---

## 4. HTTPS / TLS 設定

- **Let’s Encrypt** で自動更新  
- HSTS (`Strict-Transport-Security`)  
- **TLS 1.2+** 強制  
- サイファースイートを `openssl ciphers -v 'HIGH:!aNULL:!MD5' -ssl3` で確認

```bash
# Nginx 設定例
listen 443 ssl;
ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
```

---

## 5. セキュリティヘッダー

| ヘッダー | 用途 |
|----------|------|
| `Content-Security-Policy` | XSS・クリックジャッキング防止 |
| `X-Content-Type-Options: nosniff` | MIME sniffing 防止 |
| `X-Frame-Options: DENY` | クリックジャッキング |
| `Referrer-Policy: no-referrer` | 情報漏洩防止 |
| `Permissions-Policy` | API アクセス制御 |

```js
// Express + helmet
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "cdn.example.com"],
    },
  },
}));
```

---

## 6. 依存ライブラリの管理

- **Dependabot / Renovate** で自動 PR  
- **Snyk** で CVE スキャン  
- `npm audit` の結果は CI で失敗させる

```yaml
# GitHub Actions 例
- name: Run Snyk
  uses: snyk/actions@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

---

## 7. ログ・監視

- **Structured Logging**（JSON）  
- **WAF** で不審トラフィックをブロック  
- **ELK** / **Grafana Loki** で可視化  
- **SIEM**（Splunk, Datadog）で異常検知  
- **Alert** は **Slack / PagerDuty** へ連携

```js
const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [new winston.transports.File({ filename: "app.log" })],
});
```

---

## 8. テスト・自動化

| テスト | 目的 | ツール |
|--------|------|--------|
| **Static Analysis** | ソースコードの脆弱性検出 | ESLint, SonarQube |
| **Dependency Check** | ライブラリ脆弱性 | Snyk, OWASP Dependency-Check |
| **Penetration Test** | 実際の攻撃シナリオ | Burp Suite, OWASP ZAP |
| **Unit/Integration** | バリデーション・認可ロジック | Jest, Mocha |
| **Security Regression** | 変更が脆弱性を生むか | OWASP ZAP API |

> **CI ステップ例**  
> 1. `npm audit` → 失敗時はビルド停止  
> 2. `eslint` + `jest` → 100% カバレッジは必須  
> 3. `ZAP` スキャン → 脆弱性報告メール

---

## 9. まとめ：実装のポイント

| 項目 | チェックリスト | コメント |
|------|----------------|----------|
| 入力/出力 | サーバー側でバリデート、コンテキストエンコード | “サーバーは絶対” |
| 認証 | パスワードハッシュ＋MFA、`httpOnly/secure` Cookie | 5 分間のロックアウト |
| セッション | SameSite、JWT の署名 & 有効期限 | `expiresIn` は短め |
| TLS | HSTS、最新 TLS、サイファースイート | Let's Encrypt 自動更新 |
| ヘッダー | CSP, X-Frame-Options など | 1 行で完了 |
| 依存 | Dependabot で自動 PR | CVE は即修正 |
| ログ | JSON フォーマット、監視 | 1 秒以内にアラート |
| テスト | CI でスキャン & ステップ | “コードが安全か？” を自動化 |

---

## 10. 今後の課題

1. **Zero‑Trust** への移行：ネットワーク分離 + マイクロセグメント  
2. **Server‑less** 環境でのセキュリティ設計  
3. **AI‑based** 侵入検知（Evasion への対策）  

---

### 参考リンク

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Snyk Docs](https://docs.snyk.io/)
- [Node Security Guide](https://nodejs.org/en/security/)

---

> **最後に**  
> 「セキュリティは追加のオプション」ではなく「コードベースの一部」として設計・実装・運用を行うことが重要です。  
> まずは上述のチェックリストをプロジェクトに組み込み、CI に組み込んで自動化を図りましょう。  

Happy hacking（安全に）! 🚀