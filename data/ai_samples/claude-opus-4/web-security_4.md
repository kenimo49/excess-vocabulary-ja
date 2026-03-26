# Webアプリケーションのセキュリティ対策：エンジニアが押さえるべき基本と実装

## はじめに

Webアプリケーションの脆弱性を狙った攻撃は年々巧妙化しており、セキュリティ対策は開発者にとって避けて通れない重要な課題となっています。本記事では、OWASP Top 10を参考に、特に重要な脆弱性とその対策について、実装例を交えながら解説します。

## 1. SQLインジェクション対策

### 脆弱性の概要
SQLインジェクションは、ユーザー入力を適切に処理せずにSQL文に組み込むことで発生します。

### 悪い例
```javascript
// 危険：文字列結合でSQLを構築
const userId = req.params.userId;
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

### 対策：プリペアドステートメントの使用
```javascript
// 安全：パラメータ化されたクエリ
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId], (error, results) => {
  // 処理
});

// ORMを使用する場合（例：Sequelize）
const user = await User.findOne({
  where: { id: userId }
});
```

## 2. XSS（クロスサイトスクリプティング）対策

### 脆弱性の概要
XSSは、ユーザー入力をそのままHTMLに出力することで、悪意のあるスクリプトが実行される脆弱性です。

### 対策1：出力時のエスケープ処理
```javascript
// HTMLエスケープ関数
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  return text.replace(/[&<>"'/]/g, (m) => map[m]);
}

// 使用例
const userInput = req.body.comment;
const safeOutput = escapeHtml(userInput);
```

### 対策2：Content Security Policy (CSP) の設定
```javascript
// Express.jsでのCSP設定例
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' 'unsafe-inline'"
  );
  next();
});
```

## 3. CSRF（クロスサイトリクエストフォージェリ）対策

### 脆弱性の概要
CSRFは、ユーザーの意図しない操作を強制的に実行させる攻撃です。

### 対策：CSRFトークンの実装
```javascript
// Express.jsでのCSRF対策
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.use(csrfProtection);

app.get('/form', (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

// フォーム側
// <input type="hidden" name="_csrf" value="{{csrfToken}}">
```

## 4. 認証・セッション管理のセキュリティ

### パスワードの安全な保存
```javascript
const bcrypt = require('bcrypt');

// パスワードのハッシュ化
const saltRounds = 10;
const hashedPassword = await bcrypt.hash(plainPassword, saltRounds);

// パスワードの検証
const isValid = await bcrypt.compare(plainPassword, hashedPassword);
```

### セッション管理の強化
```javascript
const session = require('express-session');

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true, // HTTPS必須
    httpOnly: true, // XSS対策
    maxAge: 1000 * 60 * 60 * 24 // 24時間
  }
}));
```

## 5. HTTPSの強制とセキュリティヘッダー

```javascript
// HTTPS強制
app.use((req, res, next) => {
  if (!req.secure && process.env.NODE_ENV === 'production') {
    return res.redirect('https://' + req.headers.host + req.url);
  }
  next();
});

// セキュリティヘッダーの設定
app.use((req, res, next) => {
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000');
  next();
});
```

## 6. 入力検証とサニタイゼーション

```javascript
const validator = require('validator');

// メールアドレスの検証
if (!validator.isEmail(email)) {
  return res.status(400).json({ error: 'Invalid email format' });
}

// 入力の長さ制限
if (username.length > 50) {
  return res.status(400).json({ error: 'Username too long' });
}

// 特殊文字の除去
const sanitizedInput = input.replace(/[<>]/g, '');
```

## セキュリティ対策のベストプラクティス

1. **最小権限の原則**: データベースユーザーには必要最小限の権限のみを付与
2. **定期的な依存関係の更新**: `npm audit`を活用して脆弱性をチェック
3. **エラーメッセージの制御**: 本番環境では詳細なエラー情報を隠蔽
4. **ロギングとモニタリング**: 不審なアクセスパターンを検知
5. **セキュリティテストの自動化**: CI/CDパイプラインにセキュリティテストを組み込む

## まとめ

Webアプリケーションのセキュリティは、単一の対策で完結するものではありません。多層防御の考え方を持ち、継続的にセキュリティ対策を見直し、改善していくことが重要です。

開発の初期段階からセキュリティを意識し、コードレビューやセキュリティテストを開発プロセスに組み込むことで、より安全なアプリケーションを構築できます。

セキュリティは全てのエンジニアの責任です。常に最新の脅威動向を把握し、適切な対策を実装していきましょう。

## 参考資料
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)