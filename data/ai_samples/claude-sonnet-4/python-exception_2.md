# Pythonの例外処理のベストプラクティス

例外処理は、堅牢で保守性の高いPythonコードを書く上で欠かせない要素です。しかし、適切な例外処理を実装するには、いくつかの重要なベストプラクティスを理解する必要があります。本記事では、Pythonにおける例外処理の効果的な使い方を具体例とともに解説します。

## 1. 具体的な例外をキャッチする

### ❌ 悪い例
```python
try:
    result = int(input("数値を入力してください: "))
    value = 10 / result
except:
    print("エラーが発生しました")
```

### ✅ 良い例
```python
try:
    result = int(input("数値を入力してください: "))
    value = 10 / result
except ValueError:
    print("無効な数値が入力されました")
except ZeroDivisionError:
    print("0で割ることはできません")
```

**理由**: 包括的な`except`文は、予期しない例外も隠してしまい、デバッグを困難にします。具体的な例外をキャッチすることで、適切なエラーハンドリングが可能になります。

## 2. EAFP（Easier to Ask for Forgiveness than Permission）を活用する

PythonらしいコーディングスタイルとしてEAFPがあります。事前チェックよりも例外処理を使う方が効率的で読みやすいコードになります。

### ❌ LBYL（Look Before You Leap）スタイル
```python
import os

def read_config_file(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        with open(filename, 'r') as f:
            return f.read()
    else:
        return None
```

### ✅ EAFPスタイル
```python
def read_config_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except PermissionError:
        print(f"ファイル {filename} にアクセス権限がありません")
        return None
```

## 3. 例外の連鎖を活用する

Python 3では、`raise from`を使って例外の連鎖を作ることができます。これにより、元の例外情報を保持しながら新しい例外を発生させることができます。

```python
import json

def parse_user_data(json_string):
    try:
        data = json.loads(json_string)
        return {
            'name': data['name'],
            'age': int(data['age'])
        }
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"ユーザーデータの解析に失敗しました") from e

# 使用例
try:
    user = parse_user_data('{"name": "太郎", "age": "invalid"}')
except ValueError as e:
    print(f"エラー: {e}")
    print(f"原因: {e.__cause__}")
```

## 4. カスタム例外を適切に定義する

アプリケーション固有のエラー状態には、カスタム例外を定義することで可読性が向上します。

```python
class ValidationError(Exception):
    """バリデーションエラー用のカスタム例外"""
    def __init__(self, message, field_name=None):
        super().__init__(message)
        self.field_name = field_name

class UserService:
    @staticmethod
    def validate_email(email):
        if '@' not in email:
            raise ValidationError(
                "有効なメールアドレスを入力してください", 
                field_name="email"
            )
    
    @staticmethod
    def create_user(email, password):
        try:
            UserService.validate_email(email)
            # ユーザー作成処理
            return {"email": email, "status": "created"}
        except ValidationError as e:
            print(f"バリデーションエラー ({e.field_name}): {e}")
            return None
```

## 5. finally句とcontext managerの適切な使用

リソースの確実な解放には、`finally`句やcontext managerを活用しましょう。

```python
# context managerの使用（推奨）
def process_file(filename):
    try:
        with open(filename, 'r') as f:
            # ファイル処理
            data = f.read()
            return process_data(data)
    except FileNotFoundError:
        print(f"ファイル {filename} が見つかりません")
        return None

# カスタムcontext managerの例
from contextlib import contextmanager
import time

@contextmanager
def timer():
    start_time = time.time()
    try:
        yield
    except Exception as e:
        print(f"処理中にエラーが発生: {e}")
        raise
    finally:
        end_time = time.time()
        print(f"処理時間: {end_time - start_time:.2f}秒")

# 使用例
with timer():
    # 何らかの処理
    result = heavy_computation()
```

## 6. ログ出力との組み合わせ

本格的なアプリケーションでは、例外情報を適切にログに記録することが重要です。

```python
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def api_call(url):
    try:
        # API呼び出し処理
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API呼び出しに失敗しました URL: {url}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"予期しないエラーが発生しました", exc_info=True)
        raise
```

## まとめ

効果的な例外処理は以下のポイントを意識することが重要です：

- **具体的な例外をキャッチ**し、適切なエラーハンドリングを行う
- **EAFPスタイル**を採用してPythonらしいコードを書く
- **例外の連鎖**を使って元の例外情報を保持する
- **カスタム例外**でアプリケーション固有のエラー状態を表現する
- **context manager**でリソースを確実に管理する
- **適切なログ出力**で問題の特定と解決を効率化する

これらのベストプラクティスを活用することで、より保守性が高く、デバッグしやすいPythonコードを書くことができるでしょう。