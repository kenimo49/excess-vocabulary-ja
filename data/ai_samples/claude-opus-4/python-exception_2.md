# Pythonの例外処理のベストプラクティス

## はじめに

Pythonにおいて、例外処理は堅牢なアプリケーションを構築するための重要な要素です。適切な例外処理により、予期しないエラーが発生してもプログラムが適切に対処し、ユーザーに分かりやすいエラーメッセージを提供できます。本記事では、Pythonの例外処理におけるベストプラクティスを実践的な例とともに解説します。

## 1. 具体的な例外をキャッチする

### ❌ 悪い例
```python
try:
    value = dictionary[key]
    result = 10 / value
except:  # すべての例外をキャッチ
    print("エラーが発生しました")
```

### ✅ 良い例
```python
try:
    value = dictionary[key]
    result = 10 / value
except KeyError:
    print(f"キー '{key}' が見つかりません")
except ZeroDivisionError:
    print("ゼロで除算することはできません")
except Exception as e:
    # 予期しない例外のログ出力
    logger.error(f"予期しないエラー: {type(e).__name__}: {e}")
    raise
```

具体的な例外をキャッチすることで、エラーの原因を正確に特定し、適切な対処ができます。

## 2. finallyブロックの活用

リソースのクリーンアップには`finally`ブロックを使用します。

```python
def read_file_content(filename):
    file = None
    try:
        file = open(filename, 'r')
        return file.read()
    except FileNotFoundError:
        print(f"ファイル '{filename}' が見つかりません")
        return None
    finally:
        if file:
            file.close()  # 必ず実行される
```

より良い方法として、コンテキストマネージャーを使用することを推奨します：

```python
def read_file_content_better(filename):
    try:
        with open(filename, 'r') as file:  # 自動的にクローズされる
            return file.read()
    except FileNotFoundError:
        print(f"ファイル '{filename}' が見つかりません")
        return None
```

## 3. カスタム例外の定義

ビジネスロジックに特化した例外を定義することで、エラーの意味をより明確にできます。

```python
class ValidationError(Exception):
    """入力検証エラーの基底クラス"""
    pass

class EmailValidationError(ValidationError):
    """メールアドレス検証エラー"""
    def __init__(self, email, message="無効なメールアドレスです"):
        self.email = email
        self.message = message
        super().__init__(self.message)

class AgeValidationError(ValidationError):
    """年齢検証エラー"""
    def __init__(self, age, message="無効な年齢です"):
        self.age = age
        self.message = message
        super().__init__(self.message)

def validate_user_input(email, age):
    if not '@' in email:
        raise EmailValidationError(email)
    
    if age < 0 or age > 150:
        raise AgeValidationError(age)
```

## 4. 例外チェーンの活用

Python 3では、例外チェーンを使って元の例外情報を保持できます。

```python
def process_data(data):
    try:
        # データ処理
        result = json.loads(data)
    except json.JSONDecodeError as e:
        # 元の例外情報を保持しつつ、新しい例外を発生させる
        raise ValueError(f"無効なJSONデータ: {data[:50]}...") from e

# 使用例
try:
    process_data("invalid json")
except ValueError as e:
    print(f"エラー: {e}")
    print(f"原因: {e.__cause__}")
```

## 5. ロギングとの組み合わせ

例外処理とロギングを組み合わせることで、デバッグが容易になります。

```python
import logging
import traceback

logger = logging.getLogger(__name__)

def critical_operation():
    try:
        # 重要な処理
        result = perform_calculation()
    except CalculationError as e:
        # エラーレベルのログ
        logger.error(f"計算エラー: {e}", exc_info=True)
        # ユーザー向けの処理
        return None
    except Exception as e:
        # 予期しないエラーの詳細ログ
        logger.critical(
            f"予期しないエラーが発生しました\n"
            f"エラータイプ: {type(e).__name__}\n"
            f"エラーメッセージ: {e}\n"
            f"スタックトレース:\n{traceback.format_exc()}"
        )
        # 再スロー
        raise
```

## 6. 早期returnパターン

ネストを深くせずに、エラー条件を早期にチェックします。

```python
def process_user_data(user_data):
    # 早期バリデーション
    if not user_data:
        raise ValueError("ユーザーデータが空です")
    
    if 'id' not in user_data:
        raise KeyError("ユーザーIDが必要です")
    
    if not isinstance(user_data['id'], int):
        raise TypeError("ユーザーIDは整数である必要があります")
    
    # メイン処理
    return transform_user_data(user_data)
```

## 7. 実践的な例：APIクライアント

これらのベストプラクティスを組み合わせた実践例を見てみましょう。

```python
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class APIError(Exception):
    """API関連エラーの基底クラス"""
    pass

class APIConnectionError(APIError):
    """API接続エラー"""
    pass

class APIResponseError(APIError):
    """APIレスポンスエラー"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"APIエラー (status={status_code}): {message}")

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def get_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """APIからデータを取得する"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"APIタイムアウト: {url}")
            raise APIConnectionError("APIへの接続がタイムアウトしました")
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"API接続エラー: {url}", exc_info=True)
            raise APIConnectionError("APIに接続できません") from e
            
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTPエラー: {e.response.status_code} - {url}")
            raise APIResponseError(
                e.response.status_code,
                e.response.text
            ) from e
            
        except ValueError as e:
            logger.error(f"JSONパースエラー: {url}", exc_info=True)
            raise APIResponseError(
                response.status_code,
                "無効なJSONレスポンス"
            ) from e
```

## まとめ

Pythonの例外処理において重要なポイントは以下のとおりです：

1. **具体的な例外をキャッチ**し、適切に処理する
2. **カスタム例外**を定義して、エラーの意味を明確にする
3. **ロギング**と組み合わせて、デバッグを容易にする
4. **例外チェーン**を活用して、元のエラー情報を保持する
5. **リソース管理**にはコンテキストマネージャーを使用する

これらのベストプラクティスを実践することで、より堅牢でメンテナンスしやすいPythonアプリケーションを構築できます。例外処理は単なるエラー対策ではなく、アプリケーションの品質を高める重要な設計要素として捉えることが大切です。