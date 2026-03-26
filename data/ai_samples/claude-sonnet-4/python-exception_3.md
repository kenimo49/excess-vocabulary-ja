# Pythonの例外処理のベストプラクティス

## はじめに

Pythonにおける例外処理は、堅牢なアプリケーションを構築するための重要な要素です。適切な例外処理により、予期しないエラーに対して優雅に対応し、デバッグを容易にし、ユーザー体験を向上させることができます。本記事では、Pythonの例外処理における実践的なベストプラクティスを解説します。

## 1. 具体的な例外をキャッチする

### ❌ 悪い例
```python
try:
    result = int(user_input)
    data = fetch_data_from_api()
except Exception:
    print("何かエラーが発生しました")
```

### ✅ 良い例
```python
try:
    result = int(user_input)
    data = fetch_data_from_api()
except ValueError:
    print("無効な数値が入力されました")
except requests.RequestException:
    print("API通信でエラーが発生しました")
```

**理由**: 具体的な例外をキャッチすることで、エラーの原因を特定しやすくなり、それぞれに適した処理を行えます。

## 2. 例外の詳細情報を活用する

```python
import logging

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError as e:
    logging.error(f"設定ファイルが見つかりません: {e.filename}")
    # デフォルト設定を使用
    config = get_default_config()
except json.JSONDecodeError as e:
    logging.error(f"JSONパースエラー: 行{e.lineno}, 列{e.colno}")
    raise
```

例外オブジェクトから詳細な情報を取得することで、より有用なエラーメッセージを提供できます。

## 3. EAFP（Easier to Ask for Forgiveness than Permission）の原則

### ❌ LBYL（Look Before You Leap）
```python
import os

if os.path.exists('data.txt'):
    with open('data.txt', 'r') as f:
        content = f.read()
else:
    content = ""
```

### ✅ EAFP
```python
try:
    with open('data.txt', 'r') as f:
        content = f.read()
except FileNotFoundError:
    content = ""
```

**理由**: EAFPの方がPythonicで、レースコンディションも回避できます。

## 4. カスタム例外の適切な使用

```python
class ValidationError(Exception):
    """入力値検証エラー"""
    pass

class ConfigurationError(Exception):
    """設定エラー"""
    def __init__(self, message, config_key=None):
        super().__init__(message)
        self.config_key = config_key

def validate_email(email):
    if '@' not in email:
        raise ValidationError(f"無効なメールアドレス: {email}")
    return email

def load_config(config_dict):
    try:
        database_url = config_dict['DATABASE_URL']
    except KeyError:
        raise ConfigurationError(
            "データベースURLが設定されていません", 
            config_key='DATABASE_URL'
        )
```

カスタム例外を使用することで、アプリケーション固有のエラー状況を明確に表現できます。

## 5. リソースの適切なクリーンアップ

### Context Managerを活用
```python
# ファイル操作
with open('data.txt', 'r') as f:
    data = f.read()

# データベース接続
with get_database_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
```

### finallyブロックの使用
```python
resource = None
try:
    resource = acquire_expensive_resource()
    process_data(resource)
except ProcessingError as e:
    logging.error(f"処理中にエラーが発生: {e}")
    raise
finally:
    if resource:
        resource.cleanup()
```

## 6. ログ出力のベストプラクティス

```python
import logging
import traceback

logger = logging.getLogger(__name__)

def process_user_data(user_id):
    try:
        user = get_user(user_id)
        result = complex_processing(user)
        return result
    except UserNotFoundError:
        logger.warning(f"ユーザーが見つかりません: {user_id}")
        return None
    except Exception:
        logger.error(
            f"ユーザーデータ処理中に予期しないエラーが発生: {user_id}",
            exc_info=True
        )
        raise
```

**ポイント**:
- `exc_info=True`でスタックトレースも記録
- ログレベルを適切に設定（WARNING、ERROR等）
- 必要な文脈情報を含める

## 7. 例外の再発生（re-raise）の適切な使用

```python
def api_call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            return response.json()
        except requests.Timeout:
            if attempt == max_retries - 1:
                logger.error(f"API呼び出しが最大試行回数でタイムアウト: {url}")
                raise  # 最後の試行でも失敗した場合は例外を再発生
            logger.warning(f"API呼び出しタイムアウト、再試行します (試行 {attempt + 1})")
            time.sleep(2 ** attempt)  # 指数バックオフ
```

## 8. チェーン例外の活用

```python
def process_config_file(filename):
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
        return validate_config(config)
    except FileNotFoundError as e:
        raise ConfigurationError(f"設定ファイルの読み込みに失敗: {filename}") from e
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"設定ファイルの形式が不正: {filename}") from e
```

`raise ... from e`を使用することで、元の例外情報を保持しつつ、より意味のある例外を発生させることができます。

## まとめ

適切な例外処理は以下の原則に従うことが重要です：

1. **具体的な例外をキャッチ**し、適切な処理を行う
2. **例外の詳細情報を活用**してデバッグを容易にする
3. **EAFP原則**に従いPythonicなコードを書く
4. **カスタム例外**でアプリケーション固有のエラーを表現
5. **リソースの適切なクリーンアップ**を確実に行う
6. **適切なログ出力**で運用時の問題解決を支援
7. **例外の再発生**を適切に使い分ける
8. **チェーン例外**で例外の文脈を保持する

これらのベストプラクティスを適用することで、保守性が高く、デバッグしやすい堅牢なPythonアプリケーションを構築できます。