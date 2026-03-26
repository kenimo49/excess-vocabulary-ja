# Pythonの例外処理のベストプラクティス

Pythonで堅牢なアプリケーションを開発する上で、適切な例外処理は欠かせません。本記事では、Pythonの例外処理における実践的なベストプラクティスを、具体的なコード例とともに解説します。

## 1. 具体的な例外をキャッチする

### ❌ 悪い例
```python
try:
    user_input = int(input("数字を入力してください: "))
    result = 100 / user_input
except:  # すべての例外をキャッチしてしまう
    print("エラーが発生しました")
```

### ✅ 良い例
```python
try:
    user_input = int(input("数字を入力してください: "))
    result = 100 / user_input
except ValueError:
    print("有効な数値を入力してください")
except ZeroDivisionError:
    print("0では除算できません")
except Exception as e:
    print(f"予期しないエラーが発生しました: {type(e).__name__}")
```

具体的な例外をキャッチすることで、エラーの種類に応じた適切な処理が可能になります。

## 2. EAFPの原則を活用する

Python では「**Easier to Ask for Forgiveness than Permission (EAFP)**」の原則が推奨されています。

### LBYLアプローチ（推奨されない）
```python
# Look Before You Leap
if hasattr(obj, 'method') and callable(getattr(obj, 'method')):
    obj.method()
```

### EAFPアプローチ（推奨）
```python
try:
    obj.method()
except AttributeError:
    print("メソッドが存在しません")
```

## 3. finallyブロックでリソースを確実に解放する

```python
file = None
try:
    file = open('data.txt', 'r')
    data = file.read()
    # データ処理
except FileNotFoundError:
    print("ファイルが見つかりません")
except IOError as e:
    print(f"ファイル読み込みエラー: {e}")
finally:
    if file:
        file.close()  # 必ず実行される
```

さらに良い方法として、コンテキストマネージャーの使用を推奨します：

```python
try:
    with open('data.txt', 'r') as file:
        data = file.read()
        # データ処理
except FileNotFoundError:
    print("ファイルが見つかりません")
except IOError as e:
    print(f"ファイル読み込みエラー: {e}")
# withブロックを抜けると自動的にfile.close()が呼ばれる
```

## 4. カスタム例外クラスを定義する

アプリケーション固有のエラーには、カスタム例外を定義することで可読性が向上します。

```python
class ValidationError(Exception):
    """入力検証エラー"""
    pass

class AuthenticationError(Exception):
    """認証エラー"""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code

def validate_email(email):
    if '@' not in email:
        raise ValidationError(f"無効なメールアドレス: {email}")
    return True

def authenticate_user(username, password):
    if username != "admin" or password != "secret":
        raise AuthenticationError("認証に失敗しました", error_code="AUTH001")
```

## 5. 例外の再発生と例外チェーン

### 例外の再発生
```python
def process_data(data):
    try:
        # 何らかの処理
        result = risky_operation(data)
    except SpecificError:
        # ログを記録してから再発生
        logger.error(f"データ処理エラー: {data}")
        raise  # 元の例外を再発生
```

### 例外チェーン
```python
try:
    config = load_config()
except FileNotFoundError as e:
    raise ConfigurationError("設定ファイルの読み込みに失敗しました") from e
```

## 6. ログ記録のベストプラクティス

```python
import logging

logger = logging.getLogger(__name__)

def divide_numbers(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        logger.exception("ゼロ除算エラーが発生しました")  # トレースバック情報も記録
        return None
    except Exception as e:
        logger.error(f"予期しないエラー: {type(e).__name__}: {e}")
        raise
```

## 7. 例外処理のアンチパターン

### 避けるべきパターン

```python
# ❌ 例外を握りつぶす
try:
    risky_operation()
except:
    pass  # エラーを無視してしまう

# ❌ 広すぎる例外ブロック
try:
    user_data = get_user_data()
    processed_data = process_data(user_data)
    save_to_database(processed_data)
    send_notification(user_data.email)
except Exception as e:
    # どの処理でエラーが発生したか分からない
    print(f"エラー: {e}")
```

### 改善例

```python
# ✅ 各処理を適切に分離
try:
    user_data = get_user_data()
except APIError as e:
    logger.error(f"ユーザーデータ取得エラー: {e}")
    return

try:
    processed_data = process_data(user_data)
except ValidationError as e:
    logger.error(f"データ検証エラー: {e}")
    return

try:
    save_to_database(processed_data)
except DatabaseError as e:
    logger.error(f"データベース保存エラー: {e}")
    # 通知は送信を試みる
    
try:
    send_notification(user_data.email)
except NotificationError as e:
    logger.warning(f"通知送信エラー: {e}")  # 致命的でないエラー
```

## まとめ

Pythonの例外処理を適切に実装することで、エラーに強い堅牢なアプリケーションを構築できます。重要なポイントは以下の通りです：

1. **具体的な例外をキャッチ**し、適切なエラーハンドリングを行う
2. **EAFPの原則**を活用して、Pythonらしいコードを書く
3. **リソース管理**にはコンテキストマネージャーを使用する
4. **カスタム例外**でドメイン固有のエラーを表現する
5. **ログ記録**を適切に行い、デバッグを容易にする

これらのベストプラクティスを実践することで、保守性が高く、デバッグしやすいPythonアプリケーションを開発できるようになります。