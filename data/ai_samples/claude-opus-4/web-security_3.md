# Webアプリケーションのセキュリティ対策 - 開発者が知っておくべき基本と実装

## はじめに

Webアプリケーションのセキュリティは、開発者にとって避けて通れない重要なテーマです。データ漏洩やサイバー攻撃のニュースが日々報道される中、適切なセキュリティ対策を実装することは、ユーザーの信頼を維持し、ビジネスを守るために不可欠です。

本記事では、Webアプリケーション開発で必ず押さえておくべきセキュリティ対策について、実装例を交えながら解説します。

## 主要な脆弱性と対策

### 1. SQLインジェクション

SQLインジェクションは、悪意のあるSQLコードを入力値に挿入することで、データベースを不正に操作する攻撃手法です。

**脆弱なコード例（PHP）:**
```php
$id = $_GET['id'];
$query = "SELECT * FROM users WHERE id = " . $id;
$result = mysqli_query($connection, $query);
```

**対策済みコード例:**
```php
$id = $_GET['id'];
$stmt = $connection->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();
$result = $stmt->get_result();
```

### 2. クロスサイトスクリプティング（XSS）

XSSは、悪意のあるスクリプトをWebページに埋め込む攻撃です。

**対策方法:**
- 出力時のエスケープ処理
- Content Security Policy (CSP) の実装

```javascript
// React での例
function SafeComponent({ userInput }) {
  // Reactは自動的にエスケープ処理を行う
  return <div>{userInput}</div>;
}

// 生のHTMLを使う場合は注意
function UnsafeComponent({ htmlContent }) {
  // dangerouslySetInnerHTML を使う場合は必ずサニタイズ
  return <div dangerouslySetInnerHTML={{
    __html: DOMPurify.sanitize(htmlContent)
  }} />;
}
```

### 3. CSRF（クロスサイトリクエストフォージェリ）

CSRFは、ユーザーの意図しない操作を実行させる攻撃です。

**対策実装例（Node.js/Express）:**
```javascript
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/process', csrfProtection, (req, res) => {
  // CSRFトークンが自動的に検証される
  res.send('データが安全に処理されました');
});
```

## セキュアな認証・認可の実装

### パスワードの安全な保存

```javascript
const bcrypt = require('bcrypt');

// パスワードのハッシュ化
async function hashPassword(password) {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds);
}

// パスワードの検証
async function verifyPassword(password, hash) {
  return await bcrypt.compare(password, hash);
}
```

### セッション管理のベストプラクティス

```javascript
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true, // HTTPS必須
    httpOnly: true, // XSS対策
    maxAge: 1000 * 60 * 30, // 30分
    sameSite: 'strict' // CSRF対策
  }
}));
```

## HTTPS の実装

HTTPSは、通信の暗号化により中間者攻撃を防ぎます。

```javascript
// HTTP Strict Transport Security (HSTS) の設定
app.use((req, res, next) => {
  res.setHeader(
    'Strict-Transport-Security',
    'max-age=31536000; includeSubDomains'
  );
  next();
});
```

## セキュリティヘッダーの設定

```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

## 入力値検証とサニタイゼーション

```javascript
const validator = require('validator');

function validateUserInput(req, res, next) {
  const { email, username } = req.body;
  
  if (!validator.isEmail(email)) {
    return res.status(400).json({ error: '無効なメールアドレス' });
  }
  
  if (!validator.isAlphanumeric(username)) {
    return res.status(400).json({ error: 'ユーザー名は英数字のみ' });
  }
  
  // サニタイズ
  req.body.email = validator.normalizeEmail(email);
  req.body.username = validator.escape(username);
  
  next();
}
```

## セキュリティテストの自動化

```json
// package.json
{
  "scripts": {
    "security-check": "npm audit && snyk test"
  },
  "devDependencies": {
    "snyk": "^1.1000.0"
  }
}
```

## まとめ

Webアプリケーションのセキュリティは、一度実装すれば終わりではなく、継続的な取り組みが必要です。以下のポイントを常に意識しましょう：

1. **多層防御の実装**: 単一の対策に頼らず、複数の防御層を設ける
2. **最新の脆弱性情報の追跡**: CVEデータベースやOWASP Top 10を定期的にチェック
3. **依存関係の管理**: 使用しているライブラリの脆弱性を定期的に確認
4. **セキュリティテストの自動化**: CI/CDパイプラインにセキュリティテストを組み込む

セキュリティは開発の最初から組み込むべき要素です。後から追加するよりも、設計段階から考慮することで、より堅牢なアプリケーションを構築できます。

## 参考リンク

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [MDN Web Docs - Web security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [JPCERT/CC](https://www.jpcert.or.jp/)