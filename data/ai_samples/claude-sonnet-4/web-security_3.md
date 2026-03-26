# Webアプリケーションのセキュリティ対策：開発者が押さえるべき基本原則

## はじめに

近年、サイバー攻撃の手法は巧妙化し、Webアプリケーションを狙った攻撃が増加しています。開発者として、セキュアなアプリケーションを構築することは、もはや選択肢ではなく必須要件となっています。本記事では、Webアプリケーション開発において最低限押さえておくべきセキュリティ対策について解説します。

## 主要な脆弱性と対策

### 1. SQLインジェクション対策

SQLインジェクションは、入力値がそのままSQL文に組み込まれることで発生する脆弱性です。

**悪い例：**
```python
# 危険なコード
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

**良い例：**
```python
# プリペアドステートメントを使用
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

**対策のポイント：**
- プリペアドステートメントの使用
- ORMの適切な利用
- 入力値の厳密な検証

### 2. クロスサイトスクリプティング（XSS）対策

XSSは、悪意のあるスクリプトがWebページに挿入される攻撃です。

**対策例（JavaScript）：**
```javascript
// HTMLエスケープ関数
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 安全な表示
document.getElementById('content').textContent = userInput;
```

**Content Security Policy（CSP）の設定：**
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'unsafe-inline';">
```

### 3. クロスサイトリクエストフォージェリ（CSRF）対策

CSRFは、ユーザーの意図しない操作を実行させる攻撃です。

**CSRFトークンの実装例：**
```html
<!-- フォームにCSRFトークンを埋め込み -->
<form method="POST" action="/transfer">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="text" name="amount" placeholder="金額">
    <button type="submit">送金</button>
</form>
```

```python
# サーバーサイドでの検証
def validate_csrf_token(request):
    session_token = request.session.get('csrf_token')
    form_token = request.form.get('csrf_token')
    return session_token and session_token == form_token
```

## 認証・認可の実装

### セキュアな認証システム

**パスワードハッシュ化の実装：**
```python
import bcrypt

def hash_password(password):
    # ソルト付きでハッシュ化
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

**JWT（JSON Web Token）の安全な実装：**
```python
import jwt
from datetime import datetime, timedelta

def create_jwt_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
```

### セッション管理のベストプラクティス

```python
# セキュアなセッション設定
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS必須
    SESSION_COOKIE_HTTPONLY=True,    # XSS対策
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF対策
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)
```

## データ保護

### 機密情報の暗号化

```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data).decode()

# 使用例
encryption = DataEncryption(os.environ['ENCRYPTION_KEY'])
encrypted_data = encryption.encrypt("機密情報")
```

### 安全なファイルアップロード

```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_file_upload(file):
    if file and allowed_file(file.filename):
        # ファイル名をサニタイズ
        filename = secure_filename(file.filename)
        # ファイルサイズチェック
        if len(file.read()) > MAX_FILE_SIZE:
            raise ValueError("ファイルサイズが大きすぎます")
        file.seek(0)  # ポインタを先頭に戻す
        return filename
    raise ValueError("許可されていないファイル形式です")
```

## セキュリティヘッダーの設定

```python
def add_security_headers(response):
    # XSS保護
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # コンテンツタイプの推測を無効化
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # フレーム埋め込み制御
    response.headers['X-Frame-Options'] = 'DENY'
    # HTTPS強制
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## ログ記録と監視

```python
import logging
from datetime import datetime

def setup_security_logging():
    security_logger = logging.getLogger('security')
    handler = logging.FileHandler('security.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)
    security_logger.setLevel(logging.WARNING)
    return security_logger

def log_security_event(event_type, user_id=None, ip_address=None, details=None):
    security_logger.warning(f"Security Event: {event_type} | "
                           f"User: {user_id} | "
                           f"IP: {ip_address} | "
                           f"Details: {details}")
```

## まとめ

Webアプリケーションのセキュリティは、開発の初期段階から継続的に考慮すべき重要な要素です。本記事で紹介した対策は基本的なものですが、これらを確実に実装することで、多くの一般的な攻撃を防ぐことができます。

**重要なポイント：**
- 入力値は常に検証・サニタイズする
- 認証・認可の仕組みを適切に実装する
- 機密情報は暗号化して保存する
- セキュリティヘッダーを適切に設定する
- ログ記録と監視体制を整える

セキュリティは一度設定すれば終わりではありません。新しい脅威に対応するため、定期的な見直しとアップデートを心がけ、セキュアなアプリケーション開発を継続していきましょう。