# Webアプリケーションのセキュリティ対策：開発者が知っておくべき基本と実装方法

## はじめに

現代のWebアプリケーション開発において、セキュリティ対策は機能開発と同等に重要な要素です。サイバー攻撃の手法が日々進化する中、開発者は常に最新の脅威と対策を理解し、実装に反映させる必要があります。

本記事では、Webアプリケーションで頻繁に遭遇するセキュリティリスクと、その具体的な対策方法について解説します。

## 主要なセキュリティ脅威と対策

### 1. SQLインジェクション

SQLインジェクションは、不正なSQLクエリを実行させることでデータベースを攻撃する手法です。

**脆弱なコード例（PHP）:**
```php
// 危険：ユーザー入力を直接クエリに埋め込み
$sql = "SELECT * FROM users WHERE id = " . $_GET['id'];
$result = mysqli_query($connection, $sql);
```

**対策実装例:**
```php
// 安全：プリペアドステートメントを使用
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->bindParam(':id', $_GET['id'], PDO::PARAM_INT);
$stmt->execute();
$result = $stmt->fetchAll();
```

**対策のポイント:**
- プリペアドステートメントの使用
- 入力値の型チェック
- ORMライブラリの活用（Laravel Eloquent、Django ORM等）

### 2. クロスサイトスクリプティング（XSS）

XSSは悪意のあるスクリプトをWebページに埋め込む攻撃です。

**脆弱なコード例（JavaScript/HTML）:**
```html
<!-- 危険：ユーザー入力をそのまま表示 -->
<div id="message"></div>
<script>
document.getElementById('message').innerHTML = userInput;
</script>
```

**対策実装例:**
```javascript
// 安全：HTMLエスケープを実行
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById('message').innerHTML = escapeHtml(userInput);
```

**React/Vue.jsでの対策:**
```jsx
// React - JSXは自動的にエスケープされる
function UserMessage({ userInput }) {
    return <div>{userInput}</div>; // 安全
}

// Vue.js - テンプレート内でのエスケープ
<template>
    <div>{{ userInput }}</div> <!-- 安全 -->
</template>
```

### 3. クロスサイトリクエストフォージェリ（CSRF）

CSRFは、ユーザーの意図しない操作を実行させる攻撃です。

**対策実装例（Express.js）:**
```javascript
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.use(csrfProtection);

app.get('/form', (req, res) => {
    res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/transfer', (req, res) => {
    // CSRFトークンが自動的に検証される
    // 処理を実行
});
```

**フロントエンド側の実装:**
```html
<form method="POST" action="/transfer">
    <input type="hidden" name="_csrf" value="{{ csrfToken }}">
    <input type="text" name="amount">
    <button type="submit">送金</button>
</form>
```

## 認証・認可のセキュリティ

### JWT（JSON Web Token）の安全な実装

```javascript
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

// ログイン処理
app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    
    // ユーザー情報の取得
    const user = await User.findOne({ email });
    if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // パスワードの検証
    const isValid = await bcrypt.compare(password, user.hashedPassword);
    if (!isValid) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // JWTトークンの生成
    const token = jwt.sign(
        { userId: user.id, email: user.email },
        process.env.JWT_SECRET,
        { expiresIn: '1h', algorithm: 'HS256' }
    );
    
    res.json({ token });
});

// 認証ミドルウェア
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }
    
    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid token' });
        }
        req.user = user;
        next();
    });
}
```

## セキュリティヘッダーの設定

適切なHTTPセキュリティヘッダーの設定は、多くの攻撃を防ぐ効果があります。

```javascript
// Express.js + helmet.jsの例
const helmet = require('helmet');

app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            scriptSrc: ["'self'"],
            imgSrc: ["'self'", "data:", "https:"]
        }
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
    }
}));
```

**重要なセキュリティヘッダー:**
- `Content-Security-Policy`: XSS攻撃の軽減
- `Strict-Transport-Security`: HTTPS強制
- `X-Frame-Options`: クリックジャッキング防止
- `X-Content-Type-Options`: MIMEタイプ推測防止

## 入力検証とサニタイゼーション

```javascript
const validator = require('validator');
const DOMPurify = require('isomorphic-dompurify');

function validateUserInput(req, res, next) {
    const { email, username, content } = req.body;
    
    // バリデーション
    if (!validator.isEmail(email)) {
        return res.status(400).json({ error: 'Invalid email format' });
    }
    
    if (!validator.isLength(username, { min: 3, max: 20 })) {
        return res.status(400).json({ error: 'Username must be 3-20 characters' });
    }
    
    // HTMLサニタイゼーション
    req.body.content = DOMPurify.sanitize(content);
    
    next();
}
```

## まとめ

Webアプリケーションのセキュリティは、開発初期段階から継続的に考慮すべき重要な要素です。以下のポイントを常に意識しましょう：

1. **入力値の検証・サニタイゼーション**を徹底する
2. **適切な認証・認可**メカニズムを実装する
3. **セキュリティヘッダー**を正しく設定する
4. **最新の脅威情報**を定期的に確認し、対策を更新する
5. **セキュリティテスト**を開発プロセスに組み込む

セキュリティは「完璧」な状態というものが存在しない分野です。継続的な学習と改善を通じて、より安全なWebアプリケーションを構築していきましょう。

参考リソースとして、OWASP Top 10やセキュリティライブラリのドキュメントを定期的に確認することをお勧めします。