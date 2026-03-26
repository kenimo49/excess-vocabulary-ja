# Webアプリケーションのセキュリティ対策：実装すべき基本的な防御策

Webアプリケーション開発において、機能実装と同じくらい重要なのがセキュリティ対策です。サイバー攻撃の手法が高度化する現代において、セキュアなアプリケーションの構築は開発者の必須スキルとなっています。本記事では、Webアプリケーションで実装すべき基本的なセキュリティ対策について、実装例を交えて解説します。

## 1. SQLインジェクション対策

SQLインジェクションは、不正なSQLクエリを注入してデータベースを操作する攻撃手法です。

### 脆弱なコードの例

```python
# 危険：ユーザー入力を直接SQL文に結合
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)
```

### 安全な実装

```python
# 安全：プリペアドステートメントを使用
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return execute_query(query, [user_id])

# ORMを使用した場合（Django ORM）
def get_user(user_id):
    return User.objects.filter(id=user_id).first()
```

**対策のポイント：**
- プリペアドステートメント（パラメータ化クエリ）の使用
- ORMの適切な利用
- 入力値の型チェックとバリデーション

## 2. XSS（Cross-Site Scripting）対策

XSSは、悪意のあるスクリプトをWebページに注入し、他のユーザーのブラウザで実行させる攻撃です。

### エスケープ処理の実装

```javascript
// HTMLエスケープ関数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 使用例
const userInput = '<script>alert("XSS")</script>';
document.getElementById('output').innerHTML = escapeHtml(userInput);
```

```python
# Pythonでのエスケープ（Jinja2テンプレート）
from markupsafe import escape

def render_comment(comment):
    return f"<p>{escape(comment)}</p>"
```

### Content Security Policy（CSP）の設定

```html
<!-- HTTPヘッダーまたはmetaタグで設定 -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'unsafe-inline';">
```

```nginx
# Nginxでの設定例
add_header Content-Security-Policy "default-src 'self'; script-src 'self';" always;
```

## 3. CSRF（Cross-Site Request Forgery）対策

CSRFは、ユーザーの意図しないリクエストを送信させる攻撃手法です。

### CSRFトークンの実装

```html
<!-- フォームにCSRFトークンを埋め込み -->
<form method="post" action="/transfer">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="text" name="amount">
    <button type="submit">送金</button>
</form>
```

```python
# Flaskでのトークン検証例
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

@app.route('/transfer', methods=['POST'])
def transfer():
    # CSRFトークンは自動で検証される
    amount = request.form['amount']
    # 処理を実行
```

### SameSite Cookie属性の設定

```python
# セッションクッキーの設定
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS必須
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

## 4. 認証・認可の実装

### パスワードハッシュ化

```python
import bcrypt

def hash_password(password):
    # ソルトを自動生成してハッシュ化
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

### JWTトークンの安全な使用

```javascript
// JWTの生成（Node.js）
const jwt = require('jsonwebtoken');

function generateToken(user) {
    return jwt.sign(
        { userId: user.id, email: user.email },
        process.env.JWT_SECRET,
        { expiresIn: '1h' }
    );
}

function verifyToken(token) {
    try {
        return jwt.verify(token, process.env.JWT_SECRET);
    } catch (error) {
        throw new Error('Invalid token');
    }
}
```

## 5. HTTPセキュリティヘッダーの設定

```nginx
# Nginxでのセキュリティヘッダー設定
server {
    # HTTPS強制
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # クリックジャッキング対策
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # MIME Type Sniffing対策
    add_header X-Content-Type-Options "nosniff" always;
    
    # XSS Protection
    add_header X-XSS-Protection "1; mode=block" always;
    
    # リファラー制御
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

## 6. 入力値検証とサニタイゼーション

```python
from marshmallow import Schema, fields, validate, ValidationError

class UserRegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128)
    )
    age = fields.Int(
        required=True,
        validate=validate.Range(min=0, max=150)
    )

def register_user(data):
    schema = UserRegistrationSchema()
    try:
        validated_data = schema.load(data)
        # バリデーション済みデータで処理
        return create_user(validated_data)
    except ValidationError as err:
        return {"errors": err.messages}, 400
```

## まとめ

Webアプリケーションのセキュリティは、単一の対策で完全になるものではありません。本記事で紹介した対策を組み合わせて多層防御を構築することが重要です。

**重要なポイント：**
- 入力値の検証とエスケープ処理の徹底
- 最新のセキュリティベストプラクティスの継続的な学習
- 定期的なセキュリティテストとコードレビューの実施
- フレームワークのセキュリティ機能の積極的な活用

セキュリティは一度設定すれば終わりではなく、継続的な改善が必要です。OWASP Top 10などの脅威情報を定期的にチェックし、最新の攻撃手法に対する防御策を学び続けることで、より安全なWebアプリケーションを構築できます。