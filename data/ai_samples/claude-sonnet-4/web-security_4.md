# Webアプリケーションのセキュリティ対策：現代のエンジニアが知るべき基本原則

## はじめに

Webアプリケーションのセキュリティは、サイバー攻撃が日常的に発生する現代において、エンジニアにとって避けて通れない重要な課題です。一つのセキュリティ脆弱性が企業の信頼を失墜させ、個人情報漏洩による法的責任を問われる可能性もあります。

本記事では、Webアプリケーション開発において必須となるセキュリティ対策について、実装例を交えながら解説します。

## 主要な脅威と対策

### 1. SQLインジェクション

**脅威の概要**
SQLインジェクションは、不正なSQL文を実行させる攻撃です。データベースの情報漏洩や改ざん、削除などの被害をもたらします。

**対策：プリペアドステートメントの使用**

```python
# 脆弱な例（使用禁止）
user_id = request.form['user_id']
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# 安全な例
user_id = request.form['user_id']
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### 2. XSS（Cross-Site Scripting）

**脅威の概要**
悪意のあるスクリプトをWebページに注入し、ユーザーのブラウザ上で実行させる攻撃です。Cookie盗取やセッションハイジャックのリスクがあります。

**対策：入力値のサニタイゼーション**

```javascript
// 出力時のエスケープ処理
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// React等のフレームワークでは自動的にエスケープされるが、
// dangerouslySetInnerHTMLの使用は避ける
```

### 3. CSRF（Cross-Site Request Forgery）

**脅威の概要**
ユーザーの意図しない操作を実行させる攻撃です。ログイン状態を悪用して、重要な操作を不正に実行されるリスクがあります。

**対策：CSRFトークンの実装**

```html
<!-- フォームにCSRFトークンを埋め込み -->
<form method="POST" action="/transfer">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input type="text" name="amount" placeholder="金額">
    <button type="submit">送金</button>
</form>
```

```python
# サーバーサイドでのトークン検証
def verify_csrf_token(request):
    session_token = session.get('csrf_token')
    request_token = request.form.get('csrf_token')
    return session_token and session_token == request_token
```

## 認証・認可のセキュリティ

### パスワードのハッシュ化

平文パスワードの保存は絶対に避け、適切なハッシュ化を実装しましょう。

```python
import bcrypt

# パスワードのハッシュ化
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

# パスワードの検証
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

### JWTトークンのセキュア実装

```javascript
// JWT生成時の注意点
const jwt = require('jsonwebtoken');

function generateToken(user) {
    return jwt.sign(
        { 
            userId: user.id, 
            email: user.email 
        },
        process.env.JWT_SECRET, // 環境変数で管理
        { 
            expiresIn: '1h', // 適切な有効期限
            algorithm: 'HS256' // 強固なアルゴリズム
        }
    );
}
```

## HTTPSとセキュリティヘッダー

### 必須のセキュリティヘッダー

```nginx
# Nginx設定例
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'";
```

### Cookieのセキュア設定

```python
# セキュアなCookie設定
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS必須
    SESSION_COOKIE_HTTPONLY=True,    # JavaScript不可
    SESSION_COOKIE_SAMESITE='Lax'    # CSRF対策
)
```

## 入力検証とデータ処理

### バリデーションの実装

```python
from marshmallow import Schema, fields, ValidationError

class UserSchema(Schema):
    email = fields.Email(required=True)
    age = fields.Integer(validate=lambda x: 0 <= x <= 150)
    password = fields.String(validate=lambda x: len(x) >= 8)

def validate_user_input(data):
    schema = UserSchema()
    try:
        result = schema.load(data)
        return result, None
    except ValidationError as err:
        return None, err.messages
```

## ログとモニタリング

セキュリティインシデントの早期発見には、適切なログ記録とモニタリングが重要です。

```python
import logging
from datetime import datetime

# セキュリティイベントのログ記録
def log_security_event(event_type, user_id=None, ip_address=None, details=None):
    logger = logging.getLogger('security')
    logger.warning({
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address,
        'details': details
    })
```

## 開発プロセスでのセキュリティ

### 依存関係の脆弱性チェック

```bash
# Node.jsプロジェクト
npm audit
npm audit fix

# Pythonプロジェクト
pip install safety
safety check
```

### 静的解析ツールの活用

```yaml
# GitHub Actionsでのセキュリティチェック例
name: Security Check
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## まとめ

Webアプリケーションのセキュリティ対策は、開発の初期段階から継続的に実装していく必要があります。本記事で紹介した対策は基本的なものですが、これらを確実に実装することで多くの攻撃を防ぐことができます。

重要なポイント：
- **多層防御の原則**：複数のセキュリティ対策を組み合わせる
- **最小権限の原則**：必要最小限の権限のみを付与する
- **継続的な学習**：新しい脅威に対する情報収集を怠らない
- **定期的な見直し**：セキュリティ対策の有効性を定期的に検証する

セキュリティは一度実装すれば終わりではありません。常に最新の脅威情報にアンテナを張り、継続的に改善していく姿勢が重要です。