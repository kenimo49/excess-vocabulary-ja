# Webアプリケーションのセキュリティ対策：開発者が知っておくべき基本と実践

## はじめに

Webアプリケーションのセキュリティ対策は、現代のソフトウェア開発において避けて通れない重要な課題です。サイバー攻撃の手法が日々巧妙化する中、開発者は常に最新のセキュリティ脅威に対応し、ユーザーの情報を守る責任があります。

本記事では、OWASP Top 10を参考に、特に重要な脆弱性とその対策について解説します。

## 主要な脆弱性と対策

### 1. SQLインジェクション

**脆弱性の概要**
SQLインジェクションは、悪意のあるSQL文をアプリケーションに実行させる攻撃手法です。

**対策例**
```javascript
// 悪い例
const query = `SELECT * FROM users WHERE id = ${userId}`;

// 良い例（パラメータ化クエリを使用）
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId], (err, results) => {
  // 処理
});
```

### 2. クロスサイトスクリプティング（XSS）

**脆弱性の概要**
XSSは、悪意のあるスクリプトをWebページに埋め込む攻撃です。

**対策例**
```javascript
// HTMLエスケープ処理
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// Content Security Policy (CSP) の設定
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' 'unsafe-inline'"
  );
  next();
});
```

### 3. 認証・認可の不備

**脆弱性の概要**
不適切な認証・認可の実装により、権限のないユーザーがリソースにアクセスできてしまう問題です。

**対策例**
```javascript
// JWT を使用した認証の実装例
const jwt = require('jsonwebtoken');

// トークンの生成
function generateToken(user) {
  return jwt.sign(
    { id: user.id, email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: '24h' }
  );
}

// 認証ミドルウェア
function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid token' });
  }
}
```

### 4. セッション管理

**重要なポイント**
- セッションIDは予測困難なものを使用
- HTTPS通信でのみCookieを送信（Secureフラグ）
- JavaScriptからのアクセスを防ぐ（HttpOnlyフラグ）

```javascript
// Express-sessionの設定例
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true, // HTTPS接続でのみ送信
    httpOnly: true, // XSS対策
    maxAge: 1000 * 60 * 60 * 24, // 24時間
    sameSite: 'strict' // CSRF対策
  }
}));
```

### 5. CSRF（クロスサイトリクエストフォージェリ）

**対策例**
```javascript
// CSRFトークンの実装
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.use(csrfProtection);

app.get('/form', (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

// フォーム側
// <input type="hidden" name="_csrf" value="{{csrfToken}}">
```

## セキュリティヘッダーの設定

```javascript
// Helmetを使用したセキュリティヘッダーの一括設定
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"]
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

## 入力値検証

```javascript
// express-validatorを使用した入力検証
const { body, validationResult } = require('express-validator');

app.post('/user',
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }).matches(/^(?=.*[A-Za-z])(?=.*\d)/),
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    // 処理続行
  }
);
```

## セキュリティテストの自動化

```yaml
# GitHub Actions での OWASP ZAP 実行例
name: Security Scan
on: [push]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: OWASP ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://your-app.com'
```

## まとめ

Webアプリケーションのセキュリティは、一度実装したら終わりではありません。継続的な監視、アップデート、そして新たな脅威への対応が必要です。

**チェックリスト**
- [ ] 入力値の検証とサニタイゼーション
- [ ] 適切な認証・認可の実装
- [ ] セキュリティヘッダーの設定
- [ ] HTTPS通信の強制
- [ ] 依存関係の定期的な更新
- [ ] セキュリティテストの自動化

開発チーム全体でセキュリティ意識を共有し、「セキュリティ・バイ・デザイン」の考え方で開発を進めることが、安全なWebアプリケーションを構築する鍵となります。

## 参考リンク

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)